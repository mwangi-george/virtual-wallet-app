import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    BREVO_API_KEY: str = os.getenv('BREVO_API_KEY')
    BREVO_EMAIL: str = os.getenv('BREVO_EMAIL')
    RESEND_API_KEY: str = os.getenv('RESEND_API_KEY')


settings = Settings()
