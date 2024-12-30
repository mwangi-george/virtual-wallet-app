import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    DEBUG: bool = True
    BREVO_API_KEY: str = os.getenv('BREVO_API_KEY')
    BREVO_EMAIL: str = os.getenv('BREVO_EMAIL')


settings = Settings()
