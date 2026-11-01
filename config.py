import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

INSTANCE_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = (
        "sqlite:///" + (INSTANCE_DIR / "cha_casa_nova.db").as_posix()
    )

# Configuração do driver PostgreSQL psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        if os.getenv("FLASK_ENV") == "production":
            raise RuntimeError(
                "Configure uma SECRET_KEY segura na hospedagem."
            )

        SECRET_KEY = "chave-apenas-para-desenvolvimento"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False