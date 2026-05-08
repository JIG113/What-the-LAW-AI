# Stage 2 Backend (ingestion + parsing + chunking + evidence)

## Run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Stage 2 Flow
1. 문서 업로드
2. 파일 파싱 (페이지 단위 텍스트)
3. OCR 게이트 및 confidence 기록
4. 청킹
5. 키워드 기반 카테고리 분류
6. 항목 및 근거(evidence) 저장

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/items?document_id=1`
- `GET /api/v1/evidences/open-target?item_id=1`
