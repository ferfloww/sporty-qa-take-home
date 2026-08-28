"""Data models for what the UI shows at each step of the placement flow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchSelection:
    home_team: str
    away_team: str
    odd_type: str
    odds: float


@dataclass(frozen=True)
class BetSlipInfo:
    home_team: str
    away_team: str
    odds: float
    payout: float


@dataclass(frozen=True)
class Receipt:
    bet_id: str
    home_team: str
    away_team: str
    stake: float
    odds: float
    payout: float
