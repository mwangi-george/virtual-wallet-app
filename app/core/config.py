import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Represents the settings and environment variables for the application.

    This class loads configuration settings from environment variables.
    It makes it easier to manage sensitive information and configuration options for the backend system.

    Attributes:
    - DATABASE_URL (str): The URL for connecting to the database. Retrieved from the 'DATABASE_URL' environment variable.
    - BREVO_API_KEY (str): The API key for sending emails using Brevo. Retrieved from the 'BREVO_API_KEY' environment variable.
    - BREVO_EMAIL (str): The email address associated with Brevo for sending emails. Retrieved from the 'BREVO_EMAIL' environment variable.
    - RESEND_API_KEY (str): The API key for sending emails using Resend. Retrieved from the 'RESEND_API_KEY' environment variable.
    - BACKEND_SECRET_KEY (str): The secret key used for encoding and decoding data. Retrieved from the 'BACKEND_SECRET_KEY' environment variable.
    - BACKEND_DOMAIN (str): The base URL of the backend system. Retrieved from the 'BACKEND_DOMAIN' environment variable.
    - SYSTEM_SUPPORT_EMAIL (str): The support email address for the system. Retrieved from the 'SYSTEM_SUPPORT_EMAIL' environment variable.
    - JWT_SECRET_KEY (str): The secret key used for encoding and decoding JWT tokens. Retrieved from the 'JWT_SECRET_KEY' environment variable.
    - ALGORITHM (str): The algorithm used for encoding and decoding data. Retrieved from the 'ALGORITHM' environment variable.
    ACCESS_TOKEN_EXPIRE_MINUTES (int): The minimum number of minutes for which a token is valid. Retrieved from the 'ACCESS_TOKEN_EXPIRE_MINUTES' environment variable.
    """

    DATABASE_URL: str = os.getenv('DATABASE_URL')
    BREVO_API_KEY: str = os.getenv('BREVO_API_KEY')
    BREVO_EMAIL: str = os.getenv('BREVO_EMAIL')
    RESEND_API_KEY: str = os.getenv('RESEND_API_KEY')
    BACKEND_SECRET_KEY: str = os.getenv('BACKEND_SECRET_KEY')
    BACKEND_DOMAIN: str = os.getenv('BACKEND_DOMAIN')
    SYSTEM_SUPPORT_EMAIL = os.getenv('SYSTEM_SUPPORT_EMAIL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


settings = Settings()
