from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "What-the-LAW-AI"
    api_prefix: str = "/api/v1"
    sqlite_url: str = "sqlite:///./wtl_ai.db"


settings = Settings()
