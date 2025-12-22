from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # DataBase
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_echo: bool

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # RabbitMQ
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self):
        return (f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@"
                f"{self.db_host}:{self.db_port}/{self.db_name}")

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"

_settings = None

def get_settings():
    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings
