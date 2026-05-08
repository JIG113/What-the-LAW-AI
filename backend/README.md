# Stage 8 Backend (schema-safe init + run list pagination)

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
1. DB 초기화 안전화: drop/create 제거, sqlite 호환 마이그레이션 보강
2. `analysisrun` 컬럼 누락 시 자동 보정(`cancel_requested`, `cancelled_at`)
3. 실행 이력 목록 API `GET /analysis/runs` (document_id/offset/limit)
4. 실행 이력 목록 페이징 테스트 추가

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs`
- `GET /api/v1/analysis/runs/{run_id}`
- `POST /api/v1/analysis/runs/{run_id}/cancel`
- `POST /api/v1/analysis/runs/{run_id}/retry`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
