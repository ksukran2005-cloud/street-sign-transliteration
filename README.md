# IndicXlit Indic → Roman API

This project wraps AI4Bharat IndicXlit's Indic-to-Roman transliteration engine in a local FastAPI service.

## What it does

Indian script → Roman/English alphabet

Examples:
- తెలుగు: నమస్కారం → namaskaaram
- हिन्दी: नमस्ते → namaste
- தமிழ்: வணக்கம் → vanakkam

## Requirements

Recommended on Windows:
- Python 3.10
- VS Code
- Internet connection for the first dependency/model download

AI4Bharat's IndicXlit supports 21 Indic languages.

## 1. Create and activate virtual environment

PowerShell:

```powershell
py -3.10 -m venv venv
venv\Scripts\Activate.ps1
```

If `py -3.10` is unavailable, install Python 3.10 first.

## 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Start the API

```powershell
uvicorn app:app --reload
```

Open:
http://127.0.0.1:8000/docs

## 4. Test

```powershell
python test.py
```

## API

POST `/transliterate`

Example request:

```json
{
  "text": "నమస్కారం",
  "language": "te"
}
```

Example response:

```json
{
  "language": "te",
  "input": "నమస్కారం",
  "transliteration": "namaskaaram"
}
```

## Supported language codes

as, bn, brx, gu, hi, kn, ks, gom, mai, ml, mni, mr, ne, or, pa, sa, sd, si, ta, te, ur

## Important

IndicXlit's CLI model was trained on words. This starter API uses the package's sentence interface, but for OCR street-sign text we will later add a stronger text-cleaning/tokenization layer and language detection.

The actual AI4Bharat model files are not stored in this ZIP. The official package downloads/uses the model files when initialized. If you already downloaded `indicxlit-indic-en-v1.0.zip`, keep it available; we can wire the local model files directly in the next step if needed.

Official project:
https://github.com/AI4Bharat/IndicXlit
