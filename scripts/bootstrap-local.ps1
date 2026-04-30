$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\backend"
try {
    if (!(Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
    }
    if (!(Test-Path ".venv")) {
        python -m venv .venv
    }
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
finally {
    Pop-Location
}
