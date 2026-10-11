# NakhDrishti - AI Nail Health Screening

A complete website connected to your **Hybrid MobileNetV2 + SVM + XGBoost** nail-disease model.

```
nakhdrishti/
├── app.py              Flask server: serves the website + /api/predict
├── predictor.py        Inference pipeline (mirrors your training / final_test.py logic)
├── conditions.py       Plain-language info shown with each result
├── model/              Your trained files (Keras model, XGBoost, SVM, scaler, ensemble weights)
│   └── metrics.json    Test-set metrics shown on the website
├── frontend/           index.html, style.css, Script.js
├── sample_images/      One test image per class
├── test_api.py         Smoke test
└── run.sh / run.bat    One-step launchers
```

## Run it

Needs **Python 3.9 - 3.12** (TensorFlow requirement).

**macOS / Linux:** `./run.sh`   **Windows:** double-click `run.bat`

Manual alternative:
```
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open **http://localhost:8000**. The first start takes a few seconds while the models load.
(Port 8000 is used because macOS reserves 5000 for AirPlay. Change it with `PORT=9000 python app.py`.)

## How a prediction works

1. Image -> RGB, 224x224, MobileNetV2 preprocessing
2. Fine-tuned MobileNetV2 -> 1,280 features (the GlobalAveragePooling layer)
3. XGBoost and SVM (StandardScaler first) each output class probabilities
4. Where they agree, that class wins. Where they disagree, your learned per-class weights
   (`final_ensemble_weights.npy`) decide - exactly the logic in `final_test.py`

The reported **confidence** is the average probability that the two models give to the final class.

## Verified results (797 held-out test images)

| Model | Accuracy |
|---|---|
| XGBoost | 88.21% |
| SVM | 90.59% |
| **Hybrid ensemble** | **90.84%** |

Running the saved models through this website's pipeline reproduces your saved test features
(max difference 0.00003) and these accuracies.

## API

| Endpoint | |
|---|---|
| `POST /api/predict` | multipart field `image` -> JSON (prediction, confidence, top-3, per-model votes, condition info) |
| `GET /api/health` | model status |
| `GET /api/info` | classes + metrics |

Uploads are processed in memory and **never stored**. Max size 10 MB.

## Notes

- If you open `frontend/index.html` directly from disk, it automatically talks to `http://localhost:8000`.
  To host the frontend and API separately, set `window.NAKHDRISHTI_API = "https://your-api"` before `Script.js`.
- The model will always return *some* class, even for a photo that is not a nail. The site warns when
  confidence is below 50%, but it cannot detect non-nail images.
- Results are screening output, **not a medical diagnosis** (as stated on the site).
