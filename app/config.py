"""app/config.py

Carrega variáveis de ambiente (usando python-dotenv) e expõe um objeto Settings
com atributos como DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES e ALGORITHM.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Carrega o arquivo .env localizado na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings(BaseSettings):
    """Configurações da aplicação carregadas a partir de variáveis de ambiente."""

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )  # valor padrão de 30 minutos
    ALGORITHM: str = Field("HS256", env="ALGORITHM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância única que pode ser importada em todo o projeto
settings = Settings()

__all__ = ["settings", "Settings"]