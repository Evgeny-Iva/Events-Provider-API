import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Все настройки приложения"""
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "events_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME", "")
    POSTGRES_CONNECTION_STRING: str = os.getenv("POSTGRES_CONNECTION_STRING", "")
    POSTGRES_DATABASE_NAME: str = os.getenv("POSTGRES_DATABASE_NAME", "")
    POSTGRES_PASSWORD_K8S: str = os.getenv("POSTGRES_PASSWORD", "")

    @staticmethod
    def _get_postgres_host() -> str:
        """Определяет хост PostgreSQL в зависимости от окружения"""
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            return "postgres-postgresql.postgres.svc"
        return os.getenv("POSTGRES_HOST", "localhost")

    @property
    def DATABASE_URL(self) -> str:
        """Асинхронный URL для приложения"""
        if self.POSTGRES_CONNECTION_STRING:
            conn_str = self.POSTGRES_CONNECTION_STRING
            if conn_str.startswith("postgres://"):
                conn_str = conn_str.replace(
                    "postgres://",
                    "postgresql+asyncpg://", 1
                )
            return conn_str

        if self.POSTGRES_USERNAME and self.POSTGRES_DATABASE_NAME:
            password = self.POSTGRES_PASSWORD_K8S or self.POSTGRES_PASSWORD
            return (f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:"
                    f"{password}@{self.POSTGRES_HOST}:"
                    f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}")

        if (self.DB_USER and self.DB_PASSWORD and
                self.DB_HOST and self.DB_PORT and self.DB_NAME):
            return (f"postgresql+asyncpg://{self.DB_USER}:"
                    f"{self.DB_PASSWORD}@{self.DB_HOST}:"
                    f"{self.DB_PORT}/{self.DB_NAME}")

        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Синхронный URL для миграций"""
        if self.POSTGRES_CONNECTION_STRING:
            return self.POSTGRES_CONNECTION_STRING

        if self.POSTGRES_USERNAME and self.POSTGRES_DATABASE_NAME:
            password = self.POSTGRES_PASSWORD_K8S or self.POSTGRES_PASSWORD
            return (f"postgresql://{self.POSTGRES_USERNAME}:"
                    f"{password}@{self.POSTGRES_HOST}:"
                    f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}")

        if (self.DB_USER and self.DB_PASSWORD and
                self.DB_HOST and self.DB_PORT and self.DB_NAME):
            return (f"postgresql://{self.DB_USER}:"
                    f"{self.DB_PASSWORD}@{self.DB_HOST}:"
                    f"{self.DB_PORT}/{self.DB_NAME}")

        return (f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    DB_ECHO: bool = os.getenv("DB_ECHO", "True").lower() == "true"
    EXTERNAL_API_URL: str = os.getenv(
        "EXTERNAL_API_URL", "https://events-provider.dev-2.python-labs.ru"
    )
    EXTERNAL_API_KEY: str = os.getenv("EXTERNAL_API_KEY", "")
    EXTERNAL_API_TIMEOUT: int = int(os.getenv("EXTERNAL_API_TIMEOUT", "10"))

    API_KEY: str = os.getenv("API_KEY", "my-secret-key")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
