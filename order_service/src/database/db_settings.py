from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class DBSettings(BaseSettings):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_echo: bool

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self):
        return (f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@"
                f"{self.db_host}:{self.db_port}/{self.db_name}")

_db_settings = None

def get_db_settings():
    global _db_settings

    if _db_settings is None:
        _db_settings = DBSettings()

    return _db_settings
