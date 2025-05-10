import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = os.getenv('FLASK_HOST')
    PORT = 6000
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Use asyncpg for async SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace("postgresql://", "postgresql+asyncpg://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 720000)  # 1 hour

# class Config:
#     HOST = os.getenv('FLASK_HOST')
#     PORT = 6000
#     SECRET_KEY = os.getenv('SECRET_KEY')
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
#     JWT_ACCESS_TOKEN_EXPIRES = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 720000)  # 1 hour
