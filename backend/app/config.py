from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_provider: str = "anthropic"  # "anthropic" or "openai"
    model_name: str = "claude-sonnet-4-20250514"
    database_url: str = "sqlite+aiosqlite:///./bluff.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
