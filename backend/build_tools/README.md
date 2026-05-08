# Executable Build Guide

## 1) Build Windows `.exe`

```powershell
cd backend\build_tools
.\build_windows_exe.ps1
```

Output:
- `backend/dist/what_the_law_backend.exe`

## 2) Build Linux binary

```bash
cd backend/build_tools
./build_linux_binary.sh
```

Output:
- `backend/dist/what_the_law_backend`

## 3) Runtime config (optional)
Create `app_config.json` next to executable:

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "reload": false
}
```

You can copy from `app_config.example.json`.

Also supports env vars:
- `WTL_CONFIG` (config file path)
- `WTL_HOST`
- `WTL_PORT`

## 4) Start executable
- Windows: `start_backend_windows.bat`
- Linux: `./start_backend_linux.sh`

After startup open:
- `http://127.0.0.1:8000/health`
