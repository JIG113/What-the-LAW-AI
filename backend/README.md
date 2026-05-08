# Stage 12 Backend (도메인 검증 규칙 + 검증 이슈 API)

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
1. `ValidationIssue` 모델 추가 (run/item 단위 검증 결과 저장)
2. 도메인 검증 규칙 서비스 추가(`validators.py`)
   - 용적률/건폐율 % 형식/범위 검증
   - 부지면적 단위(㎡) 누락 검증
3. 파이프라인에 검증 단계 연결 (`validate` 이벤트 기록)
4. 검증 이슈 조회 API `GET /analysis/runs/{run_id}/validation-issues`
5. 검증 규칙 및 API 테스트 추가

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
