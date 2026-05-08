# Stage 16 Backend (실행파일 배포 운영 설정 고도화)

## Run (source)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Build executable
- Windows `.exe`: `backend/build_tools/build_windows_exe.ps1`
- Linux binary: `backend/build_tools/build_linux_binary.sh`

## Added in this stage
1. 실행파일 런타임 설정 로더 추가 (`run_server.py`)
   - `app_config.json` 읽기
   - 환경변수(`WTL_CONFIG`, `WTL_HOST`, `WTL_PORT`) override 지원
2. 배포 보조 파일 추가
   - `app_config.example.json`
   - `start_backend_windows.bat`
   - `start_backend_linux.sh`
3. 실행 설정 로더 테스트 추가 (`test_run_server_config.py`)

## 주요 API
- `POST /api/v1/documents/upload`
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/runs/{run_id}/validation-issues`
- `GET /api/v1/rule-profiles`
