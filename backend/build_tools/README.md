# Executable Build Guide

## Windows .exe build
Run in PowerShell:

```powershell
cd backend\build_tools
.\build_windows_exe.ps1
```

Output:
- `backend/dist/what_the_law_backend.exe`

## Linux binary build

```bash
cd backend/build_tools
./build_linux_binary.sh
```

Output:
- `backend/dist/what_the_law_backend`

## Run executable
After build:

- Start executable
- Open `http://127.0.0.1:8000/health`

The executable starts FastAPI(Uvicorn) server on port `8000`.
