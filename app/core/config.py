import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Environment Variables
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    BREVO_API_KEY: str = os.getenv('BREVO_API_KEY')
    BREVO_EMAIL: str = os.getenv('BREVO_EMAIL')
    RESEND_API_KEY: str = os.getenv('RESEND_API_KEY')
    BACKEND_SECRET_KEY: str = os.getenv('BACKEND_SECRET_KEY')
    BACKEND_DOMAIN: str = os.getenv('BACKEND_DOMAIN')
    SYSTEM_SUPPORT_EMAIL = os.getenv('SYSTEM_SUPPORT_EMAIL')


settings = Settings()
