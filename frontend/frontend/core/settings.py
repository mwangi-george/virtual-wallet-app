
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN")


settings = Settings()
