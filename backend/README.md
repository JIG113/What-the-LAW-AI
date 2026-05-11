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

## CI/CD (배포 아티팩트 자동 생성)
GitHub Actions 워크플로우: `.github/workflows/release-backend.yml`

- PR/브랜치 푸시 시:
  - `backend` 테스트(`pytest -q`) 실행
  - Linux/Windows 실행파일 빌드
  - 빌드 결과물을 Actions Artifact로 업로드
- 태그 푸시(`v*`, 예: `v1.0.0`) 시:
  - 위 빌드 아티팩트를 zip으로 묶어 GitHub Release에 자동 첨부

### 사용 방법
1. 일반 검증: PR 생성 또는 `main` 브랜치 푸시
2. 정식 배포: `git tag v1.0.0 && git push origin v1.0.0`
3. Release 페이지에서 아래 파일 다운로드
   - `backend-linux-binary.zip`
   - `backend-windows-exe.zip`
