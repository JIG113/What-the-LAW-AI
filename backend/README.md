# Stage 6 Backend (async analysis runner + rerun safety)

## Run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test
```bash
cd backend
pytest -q
```

## Added in this stage
1. 비동기 분석 실행 API `POST /analysis/run-async`
2. 백그라운드 실행기(ThreadPoolExecutor) 기반 작업 처리
3. 재분석 시 기존 문서 산출물(page/chunk/item/evidence) 정리 후 재생성
4. 비동기 실행/상태조회 API 흐름 테스트 추가

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
