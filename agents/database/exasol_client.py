import ssl
from typing import Any, Dict, List, Optional

import pyexasol

from agents.config import (
    EXASOL_DSN,
    EXASOL_PASSWORD,
    EXASOL_TLS,
    EXASOL_USER,
    EXASOL_VERIFY_TLS,
)


class ExasolClient:
    def __init__(
        self,
        dsn: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        if not password:
            password = EXASOL_PASSWORD

        if not password:
            raise ValueError("EXASOL_PASSWORD is not configured.")

        ssl_options = None

        if EXASOL_TLS and not EXASOL_VERIFY_TLS:
            ssl_options = {
                "cert_reqs": ssl.CERT_NONE
            }

        self.connection = pyexasol.connect(
            dsn=dsn or EXASOL_DSN,
            user=user or EXASOL_USER,
            password=password,
            encryption=EXASOL_TLS,
            websocket_sslopt=ssl_options,
            fetch_dict=True,
        )

    def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT/query and return rows as dictionaries.

        The current Exasol Nano environment does not support
        host parameter syntax such as :form_id, so the agents
        currently build their numeric ID filters directly
        into their SQL.
        """

        statement = self.connection.execute(query)

        return statement.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()