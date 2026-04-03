# Ejecuta Selenium + pytest y genera reporte HTML en reportes/reporte.html
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Cree el entorno: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}
.\.venv\Scripts\python.exe -m pytest tests/ --html=reportes/reporte.html --self-contained-html -v
