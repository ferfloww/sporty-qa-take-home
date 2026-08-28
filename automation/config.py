import os

class Config:

    BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
    USER_ID = os.getenv("USER_ID", "candidate-2zwV7d2uMnKk")

    @property
    def api_base_url(self) -> str:
        return f"{self.BASE_URL}/api"

config = Config()
 