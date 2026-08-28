"""Data models for what the UI shows at each step of the placement flow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchSelection:

    home_team: str
    away_team: str
    outcome: str
    odds: float

    @property
    def display_name(self) -> str:
        return f"{self.home_team} vs {self.away_team}"


@dataclass(frozen=True)
class Receipt:
    bet_id: str
    match: str
    stake: float
    odds: float
    payout: float
