# Stage 15 Backend (동적 규칙 프로파일 관리)

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
1. `RuleProfile` 모델 추가 (DB 저장형 규칙 프로파일)
2. 기본 프로파일 seed (`default`, `strict`) 자동 생성
3. 규칙 프로파일 CRUD API 추가
   - `GET /rule-profiles`
   - `POST /rule-profiles`
   - `PATCH /rule-profiles/{name}`
4. 검증 단계가 문서의 `rule_profile`을 DB에서 조회해 임계치 적용
5. rule profile API 테스트 추가

## Core APIs
- `GET /api/v1/rule-profiles`
- `POST /api/v1/rule-profiles?name=custom&percent_upper_bound=700`
- `PATCH /api/v1/rule-profiles/custom?percent_upper_bound=650&enabled=true`
- `POST /api/v1/documents/upload?project_id=demo&rule_profile=default|strict|custom`
- `POST /api/v1/documents/upload-batch?project_id=demo&rule_profile=...`
- `PATCH /api/v1/documents/{document_id}/rule-profile?rule_profile=...`
- `POST /api/v1/analysis/run`
- `POST /api/v1/analysis/run-async`
- `GET /api/v1/analysis/runs`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/runs/{run_id}/events`
- `GET /api/v1/analysis/runs/{run_id}/validation-issues`
