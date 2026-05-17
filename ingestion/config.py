"""Configuração carregada do .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    database_url: str = os.getenv("DATABASE_URL", "")
    historico_inicio: str = os.getenv("HISTORICO_INICIO", "2006-01-01")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        if not self.database_url:
            raise ValueError("DATABASE_URL não definido. Verifique o arquivo .env")


config = Config()
