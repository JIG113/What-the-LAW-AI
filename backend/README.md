# Stage 13 Backend (검증 규칙 확장: 날짜/세대수)

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
1. 검증 규칙 확장 (`validators.py`)
   - 날짜 형식 검증 (`DATE_FORMAT`)
   - 과거 기한 경고 (`DATE_PAST`)
   - 세대수 형식/범위 검증 (`HOUSEHOLD_FORMAT`, `HOUSEHOLD_RANGE`)
2. 검증 함수에 기준 시각 주입 가능 (`now_utc`) -> 테스트/재현성 강화
3. 검증 테스트 확장 (`test_validators.py`)

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/runs/{run_id}/events`
- `GET /api/v1/analysis/runs/{run_id}/validation-issues`
- `POST /api/v1/analysis/runs/{run_id}/cancel`
- `POST /api/v1/analysis/runs/{run_id}/retry`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
