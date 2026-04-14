from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_optimizer"
    anthropic_api_key: str = Field(min_length=1)
    latex_compile_dir: str = "/tmp/latex-compile"
    google_client_id: str = Field(min_length=1)
    jwt_secret: str
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def async_database_url(self) -> str:
        """Ensure the URL uses the asyncpg driver regardless of how it was provided.

        Railway (and many other platforms) inject DATABASE_URL as
        ``postgresql://...``, which SQLAlchemy's async engine does not accept.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
