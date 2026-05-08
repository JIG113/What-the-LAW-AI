# Stage 5 Backend (hybrid search + evidence anchor metadata)

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
1. 청크 임베딩 저장(`embedding_json`) 및 해시 기반 임베딩 생성
2. 하이브리드 검색 API 점수 확장 (keyword + vector)
3. 근거 anchor 메타데이터 확장 (`char_start`, `char_end`, `bbox_json`)
4. UTC timezone-aware datetime 기본값 적용

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
