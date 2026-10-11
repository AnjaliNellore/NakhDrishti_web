"""
NakhDrishti - Hybrid nail disease predictor
===========================================

Pipeline (identical to the training / evaluation scripts):

    image
      -> RGB, 224x224 (LANCZOS), MobileNetV2 preprocess_input
      -> fine-tuned MobileNetV2  (GlobalAveragePooling output, 1280 features)
      -> XGBoost   : predict_proba(features)
      -> SVM (RBF) : predict_proba(StandardScaler(features))
      -> class-aware, disagreement-aware ensemble  (final_test.py logic)
"""

import os
import threading

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from PIL import Image, ImageOps

# Alphabetical order = sklearn LabelEncoder order used during training.
CLASS_NAMES = [
    "Acral_Lentiginous_Melanoma",
    "Blue_Finger",
    "Clubbing",
    "Healthy",
    "Onychogryphosis",
    "Onychomycosis",
    "Pitting",
    "Psoriasis",
]

IMAGE_SIZE = (224, 224)
FEATURE_COLUMNS = [f"feature_{i}" for i in range(1280)]


class HybridNailPredictor:
    def __init__(self, model_dir: str):
        import tensorflow as tf  # imported lazily so the module is cheap to import

        self._tf = tf
        self._lock = threading.Lock()

        # 1. Fine-tuned MobileNetV2 -> 1280-d feature extractor
        #    (layer[-3] == GlobalAveragePooling2D, exactly as in finetune_mobilenetv2.py)
        classifier = tf.keras.models.load_model(
            os.path.join(model_dir, "finetuned_mobilenetv2.keras"), compile=False
        )
        self.feature_extractor = tf.keras.Model(
            inputs=classifier.input, outputs=classifier.layers[-3].output
        )
        self._preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

        # 2. XGBoost
        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(
            os.path.join(model_dir, "xgboost_finetuned_mobilenet_model.json")
        )

        # 3. SVM + its scaler
        self.svm_model = joblib.load(os.path.join(model_dir, "svm_model.pkl"))
        self.scaler = joblib.load(os.path.join(model_dir, "svm_scaler.pkl"))

        # 4. Learned per-class XGBoost weights
        self.weights = np.load(os.path.join(model_dir, "final_ensemble_weights.npy"))

        # Warm-up so the first real request is fast
        self._extract(np.zeros((1, *IMAGE_SIZE, 3), dtype=np.float32))

    # ------------------------------------------------------------------ #
    # Image -> features
    # ------------------------------------------------------------------ #
    @staticmethod
    def load_image(source) -> np.ndarray:
        """Open a path / file-like object and return a (224,224,3) float32 array
        in raw 0-255 pixel range (preprocess_input is applied later)."""
        with Image.open(source) as img:
            img = ImageOps.exif_transpose(img)  # honour phone-camera rotation
            img = img.convert("RGB")
            img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            return np.asarray(img, dtype=np.float32)

    def _extract(self, batch: np.ndarray) -> np.ndarray:
        batch = self._preprocess(batch.copy())
        with self._lock:  # Keras models are not guaranteed thread-safe
            feats = self.feature_extractor.predict(batch, verbose=0)
        return np.asarray(feats, dtype=np.float32)

    # ------------------------------------------------------------------ #
    # Features -> hybrid prediction
    # ------------------------------------------------------------------ #
    def predict_features(self, feats: np.ndarray) -> dict:
        # The scaler/SVM were fitted on a DataFrame with named columns.
        frame = pd.DataFrame(feats, columns=FEATURE_COLUMNS)
        xgb_prob = self.xgb_model.predict_proba(frame)
        svm_prob = self.svm_model.predict_proba(self.scaler.transform(frame))

        xgb_pred = xgb_prob.argmax(axis=1)
        svm_pred = svm_prob.argmax(axis=1)

        final = svm_pred.copy()
        for i in np.where(xgb_pred != svm_pred)[0]:
            x_cls, s_cls = xgb_pred[i], svm_pred[i]
            xgb_score = xgb_prob[i, x_cls] * self.weights[x_cls]
            svm_score = svm_prob[i, s_cls] * (1 - self.weights[s_cls])
            final[i] = x_cls if xgb_score > svm_score else s_cls

        return {
            "final": final,
            "xgb_pred": xgb_pred,
            "svm_pred": svm_pred,
            "xgb_prob": xgb_prob,
            "svm_prob": svm_prob,
        }

    def predict_image(self, source) -> dict:
        """Full prediction for one image. Returns a JSON-serialisable dict."""
        arr = self.load_image(source)
        feats = self._extract(arr[None, ...])
        out = self.predict_features(feats)

        final = int(out["final"][0])
        xp, sp = out["xgb_prob"][0], out["svm_prob"][0]

        # Blended distribution used for the "other possibilities" list.
        blended = (xp + sp) / 2.0
        blended = blended / blended.sum()

        # Confidence in the final label = average agreement of both models in it.
        confidence = float((xp[final] + sp[final]) / 2.0)

        order = np.argsort(-blended)
        top = [
            {"class": CLASS_NAMES[int(k)], "probability": round(float(blended[k]) * 100, 2)}
            for k in order[:3]
        ]

        return {
            "prediction": CLASS_NAMES[final],
            "confidence": round(confidence * 100, 2),
            "models_agree": bool(out["xgb_pred"][0] == out["svm_pred"][0]),
            "xgboost": {
                "prediction": CLASS_NAMES[int(out["xgb_pred"][0])],
                "confidence": round(float(xp.max()) * 100, 2),
            },
            "svm": {
                "prediction": CLASS_NAMES[int(out["svm_pred"][0])],
                "confidence": round(float(sp.max()) * 100, 2),
            },
            "top_predictions": top,
            "all_probabilities": {
                CLASS_NAMES[k]: round(float(blended[k]) * 100, 2) for k in range(len(CLASS_NAMES))
            },
        }
