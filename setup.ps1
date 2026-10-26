# AI4Bharat IndicXlit setup for Windows PowerShell
# Recommended: Python 3.10

$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment..."
py -3.10 -m venv venv

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Run: uvicorn app:app --reload"
