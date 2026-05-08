# Stage 10 Backend (OCR/AI 추출 정확도 고도화 1차)

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
1. 한국어 공고/고시 문서용 텍스트 정규화 단계 추가
2. 카테고리별 정규식 기반 구조화 필드 추출(사업개요/제출·심의/대지·법규)
3. 키워드 라우팅 + 정규식 결합 추출(`regex+keyword`)로 정확도 향상
4. 신뢰도 계산 로직 보강
5. 정확도 관련 단위 테스트 추가(`test_analyzer_accuracy.py`)

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
