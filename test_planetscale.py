from dotenv import load_dotenv
import os
import MySQLdb

# Cargar variables desde .env
load_dotenv()

try:
    # Conexión a la base de datos
    connection = MySQLdb.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USERNAME"),
        passwd=os.getenv("DATABASE_PASSWORD"),
        db=os.getenv("DATABASE"),
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={"ca": "/etc/ssl/certs/ca-certificates.crt"}
    )
    print("Conexión exitosa a la base de datos.")

    # Ejecutar consulta para listar tablas
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tablas en la base de datos:")
        for table in tables:
            print(f"- {table[0]}")

except MySQLdb.Error as e:
    print(f"Error al conectar a la base de datos: {e}")

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("Conexión cerrada.")
