from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite+aiosqlite:///./eval.db"

@lru_cache
def get_settings() -> Settings:
    return Settings()
