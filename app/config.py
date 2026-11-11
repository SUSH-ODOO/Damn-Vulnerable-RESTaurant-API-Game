import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# Fallback signing secret used only when JWT_SECRET_KEY is not configured.
# It is generated from a cryptographically secure source with 512 bits of
# entropy so that it cannot be brute-forced offline from an observed token.
def generate_random_secret():
    return secrets.token_urlsafe(64)


class Settings:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", generate_random_secret())
    CHEF_USERNAME = os.getenv("CHEF_USERNAME", "chef")

    # Out-of-band secret required to reset the Chef password.
    # When unset, the reset endpoint is disabled (fails closed).
    CHEF_PASSWORD_RESET_TOKEN = os.getenv("CHEF_PASSWORD_RESET_TOKEN")

    # someone needs to remember to set this variable to True in env variables
    JWT_VERIFY_SIGNATURE = os.getenv("JWT_VERIFY_SIGNATURE")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "restaurant")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


settings = Settings()
