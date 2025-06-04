import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = os.getenv('FLASK_HOST')
    PORT = 6000
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 1 hour
    JWT_ALGORITHM = "HS256"


