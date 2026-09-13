import os
from pathlib import Path

from dotenv import load_dotenv


# Always load the .env file located inside the agents directory.
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)


EXASOL_DSN = os.getenv("EXASOL_DSN", "127.0.0.1:8563")
EXASOL_USER = os.getenv("EXASOL_USER", "SYS")
EXASOL_PASSWORD = os.getenv("EXASOL_PASSWORD")

EXASOL_TLS = os.getenv("EXASOL_TLS", "true").lower() == "true"

EXASOL_VERIFY_TLS = (
    os.getenv("EXASOL_VERIFY_TLS", "false").lower() == "true"
)
