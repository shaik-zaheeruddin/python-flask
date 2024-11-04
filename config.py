# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY', 'jwt-232323300301')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgress_db_owner:ckza8deAxCT6@ep-falling-cell-a1u2tfnf.ap-southeast-1.aws.neon.tech/postgress_db?sslmode=require')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-232323300301')
#     JWT_ACCESS_TOKEN_EXPIRES = 1200
#     SU_ADMIN_ID = "21bhjb343h4223jmovjk-jmndf"


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'jwt-232323300301')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgress_db_owner:ckza8deAxCT6@ep-falling-cell-a1u2tfnf.ap-southeast-1.aws.neon.tech/postgress_db?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-232323300301')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1200))
    SU_ADMIN_ID = os.getenv('SU_ADMIN_ID', '21bhjb343h4223jmovjk-jmndf')
