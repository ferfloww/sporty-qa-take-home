import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
    USER_ID = os.getenv("USER_ID", "candidate-2zwV7d2uMnKk")

    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "10"))

    @property
    def api_base_url(self) -> str:
        return f"{self.BASE_URL}/api"

    @property
    def app_url(self) -> str:
        return f"{self.BASE_URL}?user-id={self.USER_ID}"


class BusinessRules:
    STAKE_MIN = 1.00
    STAKE_MAX = 100.00

    CURRENCY = "EUR"


config = Config()
