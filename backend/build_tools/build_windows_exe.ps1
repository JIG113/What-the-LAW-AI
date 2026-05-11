# PowerShell (Windows)
Set-Location $PSScriptRoot\..
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller --clean --noconfirm build_tools\backend_server.spec
Write-Host "Build complete: dist\what_the_law_backend.exe"
