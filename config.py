import os

# Configuración dinámica para la ruta del certificado SSL
SSL_CA_PATH = "C:/Users/acern/SistemaAfiliados/certs/cacert.pem" if os.name == "nt" else "/etc/secrets/cacert.pem"

class Config:
    # Variables de conexión a la base de datos
    MYSQL_HOST = os.getenv("DATABASE_HOST")
    MYSQL_USER = os.getenv("DATABASE_USERNAME")
    MYSQL_PASSWORD = os.getenv("DATABASE_PASSWORD")
    MYSQL_DB = os.getenv("DATABASE")
    MYSQL_SSL_CA = SSL_CA_PATH  # Ruta al certificado SSL
