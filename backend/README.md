# Stage 3 Backend (parser adapters + run tracking + dedup)

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

## Pipeline
1. 업로드 (SHA-256 중복 검사)
2. 문서 유형별 파싱 (PDF/DOCX/XLSX/PPTX/TXT)
3. OCR confidence 게이트
4. 청킹
5. 카테고리 항목/근거 추출
6. AnalysisRun 상태 저장 (queued/running/completed/failed)

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/runs/{run_id}`
- `GET /api/v1/analysis/items?document_id=1`
- `GET /api/v1/evidences/open-target?item_id=1`
