import os
from flask import Flask, render_template, request, redirect, url_for
import pymysql
from datetime import datetime
from dotenv import load_dotenv
from config import Config

# Cargar variables del .env
load_dotenv()

# Configuración de Flask
app = Flask(__name__)

# Configuración de conexión a la base de datos
try:
    db = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        ssl={"ca": Config.MYSQL_SSL_CA}
    )
    print("Conexión exitosa a la base de datos.")
except pymysql.MySQLError as e:
    print("Error al conectar a la base de datos.")
    print(f"Código de error: {e.args[0]}")
    print(f"Mensaje de error: {e.args[1]}")
    db = None


# Ruta principal
@app.route('/')
def home():
    return redirect(url_for('listar_afiliados'))

# Probar conexión a la base de datos
@app.route('/test_connection', methods=['GET'])
def test_connection():
    if db is None or not db.open:
        return "Error: No se pudo establecer conexión a la base de datos."
    try:
        with db.cursor() as cur:
            cur.execute("SELECT DATABASE();")
            db_name = cur.fetchone()
            return f"Conexión exitosa. Base de datos: {db_name[0]}"
    except pymysql.MySQLError as e:
        app.logger.error(f"Error al conectar a la base de datos: {e.args[0]} - {e.args[1]}")
        return f"Error al conectar a la base de datos: {str(e)}"





# Ruta para listar afiliados
@app.route('/afiliados', methods=['GET'])
def listar_afiliados():
    if db is None or not db.open:
        return "Error: No se pudo establecer conexión a la base de datos."
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM Afiliados")
            afiliados = cur.fetchall()
        return render_template('listar_afiliados.html', afiliados=afiliados)
    except pymysql.MySQLError as e:
        return f"<h1>Error al listar afiliados: {str(e)}</h1>"

# Ruta para registrar una venta
@app.route('/registrar_venta/<int:afiliado_id>', methods=['GET', 'POST'])
def registrar_venta(afiliado_id):
    if db is None or not db.open:
        return "Error: No se pudo establecer conexión a la base de datos."
    form = VentaForm(request.form)
    if request.method == 'POST' and form.validate():
        modelo = form.modelo.data
        talla = form.talla.data
        fecha = form.fecha.data or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO Ventas (AfiliadoID, Modelo, Talla, Fecha)
                    VALUES (%s, %s, %s, %s)
                """, (afiliado_id, modelo, talla, fecha))
                db.commit()
            return redirect(url_for('listar_afiliados'))
        except pymysql.MySQLError as e:
            return f"<h1>Error al registrar venta: {str(e)}</h1>"
    return render_template('registrar_venta.html', form=form, afiliado_id=afiliado_id)

# Ruta para eliminar un afiliado
@app.route('/eliminar_afiliado/<int:id>', methods=['GET'])
def eliminar_afiliado(id):
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM Afiliados WHERE ID = %s", (id,))
            db.commit()
        return redirect(url_for('listar_afiliados'))
    except pymysql.MySQLError as e:
        return f"<h1>Error al eliminar afiliado: {str(e)}</h1>"

# Ruta para editar un afiliado
@app.route('/editar_afiliado/<int:id>', methods=['GET', 'POST'])
def editar_afiliado(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        estatus = request.form.get('estatus')

        if not nombre or not estatus:
            return "<h1>Error: Todos los campos son obligatorios</h1>"

        try:
            with db.cursor() as cur:
                cur.execute("""
                    UPDATE Afiliados
                    SET Nombre = %s, Estatus = %s
                    WHERE ID = %s
                """, (nombre, estatus, id))
                db.commit()
            return redirect(url_for('listar_afiliados'))
        except pymysql.MySQLError as e:
            return f"<h1>Error al editar afiliado: {str(e)}</h1>"

    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM Afiliados WHERE ID = %s", (id,))
            afiliado = cur.fetchone()
        return render_template('editar_afiliado.html', afiliado=afiliado)
    except pymysql.MySQLError as e:
        return f"<h1>Error al obtener afiliado: {str(e)}</h1>"

# Ruta para avisos
@app.route('/avisos', methods=['GET'])
def avisos():
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT A.ID, A.Nombre, MAX(V.Fecha) AS UltimaCompra
                FROM Afiliados A
                INNER JOIN Ventas V ON A.ID = V.AfiliadoID
                WHERE A.Estatus = 'Cliente'
                GROUP BY A.ID, A.Nombre
                HAVING DATEDIFF(CURDATE(), MAX(V.Fecha)) >= 60
            """)
            clientes_avisos = cur.fetchall()

            cur.execute("""
                SELECT A.ID, A.Nombre, MIN(V.Fecha) AS PrimeraCompra,
                       DATEDIFF(DATE_ADD(MIN(V.Fecha), INTERVAL 5 DAY), CURDATE()) AS DiasRestantes
                FROM Afiliados A
                INNER JOIN Ventas V ON A.ID = V.AfiliadoID
                WHERE A.Estatus = 'Vendedora'
                GROUP BY A.ID, A.Nombre
                HAVING DiasRestantes <= 2 AND DiasRestantes > 0
            """)
            vendedoras_avisos = cur.fetchall()
        return render_template('avisos.html', clientes=clientes_avisos, vendedoras=vendedoras_avisos)
    except pymysql.MySQLError as e:
        return f"<h1>Error al obtener avisos: {str(e)}</h1>"

@app.route('/test_db_render', methods=['GET'])
def test_db_render():
    try:
        with db.cursor() as cur:
            cur.execute("SELECT DATABASE();")
            db_name = cur.fetchone()
            return f"Conexión exitosa a la base de datos desde Render: {db_name[0]}"
    except Exception as e:
        return f"Error al conectar desde Render: {str(e)}"


# Habilitar depuración
if __name__ == '__main__':
    app.run(debug=True)
