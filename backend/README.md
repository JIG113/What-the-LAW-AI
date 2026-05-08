# Stage 1 Backend (MVP scaffold)

## Run
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Core APIs
- `POST /api/v1/documents/upload?project_id=demo`
- `POST /api/v1/analysis/run`
- `GET /api/v1/analysis/items?document_id=1`
- `GET /api/v1/evidences/open-target?item_id=1`
