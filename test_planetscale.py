import os
import pymysql
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la conexión
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE = os.getenv("DATABASE")

try:
    # Intentar la conexión
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        database=DATABASE,
        ssl={
    "ca": "C:/Users/acern/SistemaAfiliados/certs/cacert.pem"
}

    )
    print("Conexión exitosa a la base de datos.")

    # Ejecutar un query para listar tablas
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print("Tablas en la base de datos:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No se encontraron tablas en la base de datos.")
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("Conexión cerrada.")
