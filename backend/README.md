# Stage 7 Backend (run control: cancel/retry + lifespan)

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
1. 분석 실행 취소 API `POST /analysis/runs/{run_id}/cancel`
2. 분석 실행 재시도 API `POST /analysis/runs/{run_id}/retry`
3. 백그라운드 Future 레지스트리 추가(작업 제어)
4. 파이프라인 cancel 요청 협조 처리(`cancelling` → `cancelled`)
5. FastAPI startup deprecation 제거를 위한 lifespan 방식 전환

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs/{run_id}`
- `POST /api/v1/analysis/runs/{run_id}/cancel`
- `POST /api/v1/analysis/runs/{run_id}/retry`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
