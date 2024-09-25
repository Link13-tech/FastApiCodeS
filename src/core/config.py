import multiprocessing
from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "Code Snippet API"
    app_port: int = 9000
    app_host: str = 'localhost'
    reload: bool = True
    cpu_count: int | None = None
    postgres_dsn: PostgresDsn = MultiHostUrl('postgresql+asyncpg://Link13:link13.22@localhost/FastApi')
    jwt_secret: str = "your_super_secret"
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"  # Обеспечивает правильную кодировку
        _extra = 'allow'  # Позволяет игнорировать неизвестные параметры


# Загружаем настройки
settings = AppSettings()

# Настройки для Uvicorn
uvicorn_options = {
    "host": settings.app_host,
    "port": settings.app_port,
    "workers": settings.cpu_count or multiprocessing.cpu_count(),
    "reload": settings.reload
}
