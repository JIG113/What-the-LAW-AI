# Stage 14 Backend (규칙 프로파일: default/strict)

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
1. 문서별 규칙 프로파일 필드 추가 (`Document.rule_profile`)
2. 업로드 시 규칙 프로파일 지정 지원 (`rule_profile` query)
3. 문서 규칙 프로파일 수정 API 추가
   - `PATCH /documents/{document_id}/rule-profile`
4. 검증기에 프로파일별 임계치 적용
   - `default`: 용적률/건폐율 상한 1000%
   - `strict`: 용적률/건폐율 상한 500%
5. strict 프로파일 테스트/통합 API 테스트 추가

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo&rule_profile=default|strict`
- `POST /api/v1/documents/upload-batch?project_id=demo&rule_profile=default|strict`
- `PATCH /api/v1/documents/{document_id}/rule-profile?rule_profile=strict`
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
