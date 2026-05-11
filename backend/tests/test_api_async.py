import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_run_analysis_async_flow(tmp_path: Path):
    with TestClient(app) as client:
        sample = tmp_path / "sample.txt"
        sample.write_text("사업개요\n\n면적 1000\n\n제출 서류", encoding="utf-8")

        with sample.open("rb") as fp:
            res = client.post("/api/v1/documents/upload?project_id=p1", files={"file": ("sample.txt", fp, "text/plain")})
        assert res.status_code == 200
        doc_id = res.json()["document_id"]

        r2 = client.post("/api/v1/analysis/run-async", json={"document_id": doc_id})
        assert r2.status_code == 200
        run_id = r2.json()["id"]

        status = r2.json()["status"]
        for _ in range(20):
            r3 = client.get(f"/api/v1/analysis/runs/{run_id}")
            assert r3.status_code == 200
            status = r3.json()["status"]
            if status in {"completed", "failed"}:
                break
            time.sleep(0.1)

        assert status == "completed"
