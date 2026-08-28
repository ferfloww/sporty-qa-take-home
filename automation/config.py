import os


class Config:

    BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
    USER_ID = os.getenv("USER_ID", "candidate-2zwV7d2uMnKk")

    API_TIMEOUT = 10

    @property
    def api_base_url(self) -> str:
        return f"{self.BASE_URL}/api"


class BusinessRules:
    STAKE_MIN = 1.00
    STAKE_MAX = 100.00

    CURRENCY = "EUR"


config = Config()
