"""API client for the betting endpoints. Domain-specific stuff lives here
(what a bet is, what a match is) - the actual GET/POST plumbing is in http_client.py.
"""

from typing import Any, Optional

from api.http_client import HttpClient
from config import config


class BettingApiClient:

    def __init__(self, base_url: Optional[str] = None, user_id: Optional[str] = None):
        self.user_id = user_id or config.USER_ID
        self.http = HttpClient(
            base_url or config.api_base_url, self._headers, config.API_TIMEOUT
        )

    @property
    def _headers(self):
        return {"x-user-id": self.user_id, "Content-Type": "application/json"}

    def get_matches(self):
        return self.http.get("/matches")

    def get_balance(self):
        return self.http.get("/balance")

    def reset_balance(self):
        return self.http.post("/reset-balance")

    def place_bet(
        self, match_id: str, selection: str, stake: Any, headers: Optional[dict] = None
    ):
        return self.http.post(
            "/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
            headers=headers,
        )

    def get_first_match_id(self) -> str:
        response = self.get_matches()
        response.raise_for_status()
        matches = response.json()
        if not matches:
            raise RuntimeError("No matches returned by GET /api/matches")
        return matches[0]["id"]

    def get_current_balance(self) -> float:
        response = self.get_balance()
        response.raise_for_status()
        return float(response.json()["balance"])
