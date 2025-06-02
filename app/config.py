# app/config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from datetime import timedelta

user     = quote_plus(os.getenv("POSTGRES_USER", ""))
password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
db_name  = quote_plus(os.getenv("POSTGRES_DB", ""))

class Config:
    SECRET_KEY          = os.getenv("SECRET_KEY", "fallback-secret")
    JWT_SECRET_KEY      = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{user}:{password}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
