
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"
    database_url: str = "sqlite+aiosqlite:///./eval.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
