import os

class Config:
    MYSQL_HOST = os.getenv('DATABASE_HOST')
    MYSQL_USER = os.getenv('DATABASE_USERNAME')
    MYSQL_PASSWORD = os.getenv('DATABASE_PASSWORD')
    MYSQL_DB = os.getenv('DATABASE')
    MYSQL_SSL_CA = os.getenv('MYSQL_SSL_CA')
