# Stage 4 Backend (batch upload + edit history + chunk search)

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
1. 멀티파일 배치 업로드 (`/documents/upload-batch`)
2. 항목 수동 수정 API + 수정 이력 저장 (`UserEdit`)
3. 청크 키워드 검색 API (`/search/chunks`)
4. 기존 분석 실행 이력(AnalysisRun) 유지

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
