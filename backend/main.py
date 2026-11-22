import io
import json
import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(os.getenv('LIVO_MODEL_DIR', str(BASE_DIR / 'models')))
MODEL_FILE = MODEL_DIR / 'smc_efficientnetb3_baseline.keras'
CONFIG_FILE = MODEL_DIR / 'model_config.json'
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title='LivoHealth Research API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "livo-health-detection-of-malignancy.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
model = None
config = None

@app.on_event('startup')
def load_assets():
    global model, config
    if not MODEL_FILE.is_file() or not CONFIG_FILE.is_file():
        print(f'Model assets missing in {MODEL_DIR}. /health will report not ready.')
        return
    with CONFIG_FILE.open(encoding='utf-8') as f:
        config = json.load(f)
    model = tf.keras.models.load_model(str(MODEL_FILE), compile=False)
    print('LivoHealth model loaded.')

@app.get('/health')
def health():
    return {'status': 'ready' if model is not None else 'model_not_loaded', 'model_file': MODEL_FILE.name}

@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    if model is None or config is None:
        raise HTTPException(status_code=503, detail='Model not loaded. Copy .keras and model_config.json to backend/models/.')
    if file.content_type not in ('image/jpeg', 'image/png'):
        raise HTTPException(status_code=400, detail='Upload a JPG or PNG image.')
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='Image exceeds 10 MB limit.')
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.format not in ('JPEG', 'PNG'):
                raise HTTPException(status_code=400, detail='Invalid image format.')
            img = img.convert('RGB')
            image = np.asarray(img, dtype=np.float32)
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail='Could not decode image.')
    # Mirrors tf.image.resize(..., [300, 300]) used during training.
    tensor = tf.image.resize(tf.convert_to_tensor(image), [300, 300], method='bilinear')
    tensor = tf.expand_dims(tensor, axis=0)
    score = float(model(tensor, training=False).numpy().reshape(-1)[0])
    if not np.isfinite(score):
        raise HTTPException(status_code=500, detail='Invalid model output.')
    threshold = float(config.get('classification_threshold', 0.5))
    predicted = 'HCC' if score >= threshold else 'Hemangioma'
    return {
        'predicted_class': predicted,
        'hcc_model_score': round(score, 6),
        'hemangioma_model_score': round(1 - score, 6),
        'threshold': threshold,
        'disclaimer': 'Research-only experimental model. Dataset acquisition bias is known. Not a medical diagnosis; consult a qualified clinician.'
    }
