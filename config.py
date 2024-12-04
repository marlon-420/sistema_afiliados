import os

class Config:
    MYSQL_HOST = os.getenv("DATABASE_HOST")
    MYSQL_USER = os.getenv("DATABASE_USERNAME")
    MYSQL_PASSWORD = os.getenv("DATABASE_PASSWORD")
    MYSQL_DB = os.getenv("DATABASE")
    MYSQL_SSL_CA = "/etc/ssl/certs/ca-certificates.crt"  # Ruta estándar en Render
