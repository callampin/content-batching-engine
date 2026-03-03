import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "change_me")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "content_batching")
    postgres_user: str = os.getenv("POSTGRES_USER", "content_engine")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    google_drive_credentials_json: str = os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON", "{}")
    google_drive_folder_id: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_admin_chat_id: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    celery_task_soft_time_limit: int = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "300"))
    celery_task_time_limit: int = int(os.getenv("CELERY_TASK_TIME_LIMIT", "360"))

    temp_files_dir: str = "/tmp/content_engine"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"


settings = Settings()
