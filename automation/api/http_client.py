"""Generic HTTP client - just wraps requests.Session with default headers/timeout
so nothing else has to repeat that setup.
"""

from typing import Any, Optional

import requests


class HttpClient:

    def __init__(
        self, base_url: str, default_headers: Optional[dict] = None, timeout: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path: str, headers: Optional[dict] = None) -> requests.Response:
        return self.session.get(
            f"{self.base_url}{path}",
            headers=headers if headers is not None else self.default_headers,
            timeout=self.timeout,
        )

    def post(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        return self.session.post(
            f"{self.base_url}{path}",
            json=json,
            headers=headers if headers is not None else self.default_headers,
            timeout=self.timeout,
        )
