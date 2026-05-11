import json
from pathlib import Path

from run_server import load_runtime_config


def test_load_runtime_config_from_file(tmp_path: Path, monkeypatch):
    cfg = {"host": "0.0.0.0", "port": 9000, "reload": False}
    path = tmp_path / "app_config.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")

    monkeypatch.setenv("WTL_CONFIG", str(path))
    out = load_runtime_config()
    assert out["host"] == "0.0.0.0"
    assert out["port"] == 9000


def test_load_runtime_config_from_env(monkeypatch):
    monkeypatch.delenv("WTL_CONFIG", raising=False)
    monkeypatch.setenv("WTL_HOST", "0.0.0.0")
    monkeypatch.setenv("WTL_PORT", "9100")
    out = load_runtime_config()
    assert out["host"] == "0.0.0.0"
    assert out["port"] == 9100
