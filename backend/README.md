# Stage 11 Backend (추출 결과 후처리/정규화/중복 병합)

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
1. 추출 결과 후처리 서비스 추가(`postprocess.py`)
2. 값 정규화(`m2 -> ㎡`, 공백 정리)
3. 신뢰도 재계산(단위/수치 포함 항목 가산)
4. 중복 항목 병합(카테고리/키/값 기준)
5. 파이프라인에 후처리 단계 연결
6. 후처리 단위 테스트 추가(`test_postprocess.py`)

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/documents/upload-batch?project_id=demo`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/runs/{run_id}/events`
- `POST /api/v1/analysis/runs/{run_id}/cancel`
- `POST /api/v1/analysis/runs/{run_id}/retry`
- `GET /api/v1/analysis/items?document_id=1`
- `PATCH /api/v1/analysis/items/{item_id}`
- `GET /api/v1/analysis/items/{item_id}/history`
- `GET /api/v1/search/chunks?document_id=1&q=사업개요`
- `GET /api/v1/evidences/open-target?item_id=1`
