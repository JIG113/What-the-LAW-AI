import json
import os
from pathlib import Path

import uvicorn


def load_runtime_config() -> dict:
    default = {"host": "127.0.0.1", "port": 8000, "reload": False}

    config_path = Path(os.getenv("WTL_CONFIG", "app_config.json"))
    if config_path.exists():
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            default.update({k: payload[k] for k in ["host", "port", "reload"] if k in payload})
        except Exception:
            pass

    if os.getenv("WTL_HOST"):
        default["host"] = os.getenv("WTL_HOST")
    if os.getenv("WTL_PORT"):
        default["port"] = int(os.getenv("WTL_PORT"))

    return default


def main() -> None:
    cfg = load_runtime_config()
    uvicorn.run("app.main:app", host=cfg["host"], port=int(cfg["port"]), reload=bool(cfg["reload"]))


if __name__ == "__main__":
    main()
