"""
NakhDrishti - Flask backend
===========================

Serves the website (./frontend) and the prediction API:

    GET  /                 -> website
    GET  /api/health       -> model status
    GET  /api/info         -> classes + held-out test metrics
    POST /api/predict      -> multipart form field "image"  ->  JSON prediction

Run:   python app.py        (then open http://localhost:8000)
"""

import io
import json
import logging
import os
import time

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, UnidentifiedImageError

from conditions import CONDITIONS, get_condition
from predictor import CLASS_NAMES, HybridNailPredictor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

MAX_UPLOAD_MB = 10
LOW_CONFIDENCE = 50.0  # below this the UI warns that the result is uncertain

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("nakhdrishti")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

# --------------------------------------------------------------------------- #
# Load the models once at start-up
# --------------------------------------------------------------------------- #
log.info("Loading hybrid model (MobileNetV2 + SVM + XGBoost)...")
_t0 = time.time()
predictor = HybridNailPredictor(MODEL_DIR)
log.info("Model ready in %.1fs", time.time() - _t0)

try:
    with open(os.path.join(MODEL_DIR, "metrics.json")) as fh:
        METRICS = json.load(fh)
except OSError:
    METRICS = None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@app.after_request
def add_headers(resp):
    # Allows the page to be opened from another origin / file:// while developing.
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


def error(message: str, status: int):
    return jsonify({"success": False, "error": message}), status


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True, "classes": len(CLASS_NAMES)})


@app.get("/api/info")
def info():
    return jsonify(
        {
            "classes": [
                {"key": c, "title": CONDITIONS[c]["title"], "severity": CONDITIONS[c]["severity"]}
                for c in CLASS_NAMES
            ],
            "metrics": METRICS,
        }
    )


@app.route("/api/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return ("", 204)

    file = request.files.get("image")
    if file is None or file.filename == "":
        return error("No image was uploaded. Please choose a nail image.", 400)

    data = file.read()
    if not data:
        return error("The uploaded file is empty.", 400)

    # Validate that it is really a decodable image (never trust the extension).
    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return error("That file is not a valid image. Please upload a JPG, PNG or WEBP photo.", 400)

    try:
        t0 = time.time()
        result = predictor.predict_image(io.BytesIO(data))
        elapsed = time.time() - t0
    except Exception:  # noqa: BLE001
        log.exception("Prediction failed")
        return error("The model could not process this image. Please try another photo.", 500)

    result["condition"] = get_condition(result["prediction"])
    for item in result["top_predictions"]:
        item["title"] = CONDITIONS[item["class"]]["title"]
        item["severity"] = CONDITIONS[item["class"]]["severity"]
    result["low_confidence"] = result["confidence"] < LOW_CONFIDENCE
    result["processing_time_ms"] = int(elapsed * 1000)
    result["success"] = True

    log.info(
        "predicted %-27s conf=%5.1f%% agree=%s  (%d ms)",
        result["prediction"], result["confidence"], result["models_agree"], result["processing_time_ms"],
    )
    # NOTE: the uploaded image is processed in memory only and is never stored.
    return jsonify(result)


@app.errorhandler(413)
def too_large(_):
    return error(f"Image is too large. Maximum size is {MAX_UPLOAD_MB} MB.", 413)


# --------------------------------------------------------------------------- #
# Website
# --------------------------------------------------------------------------- #
@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n  NakhDrishti is running ->  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
