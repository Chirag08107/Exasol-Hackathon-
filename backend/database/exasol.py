import os
import ssl

import pyexasol
from dotenv import load_dotenv

load_dotenv()


EXASOL_HOST = os.getenv("EXASOL_HOST", "127.0.0.1")
EXASOL_PORT = os.getenv("EXASOL_PORT", "18563")
EXASOL_USER = os.getenv("EXASOL_USER", "SYS")
EXASOL_PASSWORD = os.getenv("EXASOL_PASSWORD")


def get_connection():
    connection = pyexasol.connect(
        dsn=f"{EXASOL_HOST}:{EXASOL_PORT}",
        user=EXASOL_USER,
        password=EXASOL_PASSWORD,
        encryption=True,
        websocket_sslopt={
            "cert_reqs": ssl.CERT_NONE
        }
    )

    return connection