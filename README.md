# LivoHealth research demo

This app uses the **user's own saved model**. The model weights are not included.

## Files
- `frontend/index.html`, `style.css`, `script.js`: responsive upload UI
- `backend/main.py`: FastAPI model inference service
- `backend/requirements.txt`: Python dependencies

## Setup (Windows, VS Code)
1. Extract the zip and open `livohealth_app` in VS Code.
2. Create `backend/models/` and copy these two files from Google Drive's `SMC-LUD/models/` folder:
   - `smc_efficientnetb3_baseline.keras`
   - `model_config.json`
3. Open a terminal in `backend` and run:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
   If your Python version differs, use a TensorFlow-supported version and adjust the `py` command. Initial TensorFlow installation can take time.
4. Open `http://127.0.0.1:8000/health`. It should say `ready`.
5. In a **second** terminal, from the `frontend` folder run:
   ```powershell
   py -m http.server 5500
   ```
6. Open `http://127.0.0.1:5500` and upload a JPG or PNG.

**Research only:** The model is trained on a dataset with perfect original-resolution/class confounding. Predictions are not medically reliable. Do not deploy for clinical decision-making or upload patient-identifiable images to public servers.
