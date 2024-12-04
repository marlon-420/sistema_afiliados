import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from config import Config  # Importar la configuración
from datetime import datetime

# Cargar .env solo si no estás en producción
if os.getenv("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Configuración de Flask
app = Flask(__name__)

app.config.from_object(Config)  # Cargar configuración desde el objeto Config

# Configuración de la conexión a la base de datos
try:
    db = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        ssl_ca=Config.MYSQL_SSL_CA
    )
    print("Conexión exitosa a la base de datos")
except Error as e:
    print(f"Error al conectar a la base de datos: {e}")
    db = None

# Ruta principal
@app.route('/')
def home():
    return redirect(url_for('listar_afiliados'))


@app.route('/test_ssl_file', methods=['GET'])
def test_ssl_certificate():
    ssl_path = Config.MYSQL_SSL_CA
    if os.path.isfile(ssl_path):
        return f"Certificado SSL encontrado en: {ssl_path}"
    else:
        return f"Certificado SSL no encontrado en: {ssl_path}"


@app.route('/test_render')
def test_render():
    return "¡Render está funcionando correctamente desde la rama main!"


# Ruta para probar la conexión
@app.route('/test_connection', methods=['GET'])
def test_connection():
    try:
        if db.is_connected():
            cur = db.cursor()
            cur.execute("SELECT DATABASE();")
            db_name = cur.fetchone()
            cur.close()
            return f"Conexión exitosa. Base de datos: {db_name[0]}"
        else:
            return "<h1>Error: No se pudo conectar a la base de datos</h1>"
    except Exception as e:
        return f"Error al conectar a la base de datos: {str(e)}"


# Ruta para formulario
@app.route('/formulario', methods=['GET'])
def formulario():
    return render_template('formulario.html')


# Ruta para listar afiliados
@app.route('/afiliados', methods=['GET'])
def listar_afiliados():
    try:
        if db.is_connected():
            cur = db.cursor()
            cur.execute("SELECT * FROM Afiliados")
            afiliados = cur.fetchall()
            cur.close()
            return render_template('listar_afiliados.html', afiliados=afiliados)
        else:
            return "<h1>Error: No se pudo conectar a la base de datos</h1>"
    except Exception as e:
        app.logger.error(f"Error al listar afiliados: {str(e)}")
        return f"<h1>Ha ocurrido un error: {str(e)}</h1>"


# Ruta para registrar una venta
from forms import VentaForm

@app.route('/registrar_venta/<int:afiliado_id>', methods=['GET', 'POST'])
def registrar_venta(afiliado_id):
    form = VentaForm(request.form)
    if request.method == 'POST' and form.validate():
        modelo = form.modelo.data
        talla = form.talla.data
        fecha = form.fecha.data or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cur = db.cursor()
            cur.execute("""
                INSERT INTO Ventas (AfiliadoID, Modelo, Talla, Fecha)
                VALUES (%s, %s, %s, %s)
            """, (afiliado_id, modelo, talla, fecha))
            db.commit()
            cur.close()
            return redirect(url_for('listar_afiliados'))
        except Exception as e:
            app.logger.error(f"Error al registrar venta: {str(e)}")
            return render_template('error.html', error_message="No se pudo registrar la venta.")
    return render_template('registrar_venta.html', form=form, afiliado_id=afiliado_id)


# Ruta para eliminar un afiliado
@app.route('/eliminar_afiliado/<int:id>', methods=['GET'])
def eliminar_afiliado(id):
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM Afiliados WHERE ID = %s", (id,))
        db.commit()
        cur.close()
        return redirect(url_for('listar_afiliados'))
    except Exception as e:
        app.logger.error(f"Error al eliminar afiliado: {str(e)}")
        return "<h1>Ha ocurrido un error. Inténtelo más tarde.</h1>"


# Ruta para editar un afiliado
@app.route('/editar_afiliado/<int:id>', methods=['GET', 'POST'])
def editar_afiliado(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        estatus = request.form.get('estatus')

        if not nombre or not estatus:
            return "<h1>Error: Todos los campos son obligatorios</h1>"

        try:
            cur = db.cursor()
            cur.execute("""
                UPDATE Afiliados
                SET Nombre = %s, Estatus = %s
                WHERE ID = %s
            """, (nombre, estatus, id))
            db.commit()
            cur.close()
            return redirect(url_for('listar_afiliados'))
        except Exception as e:
            app.logger.error(f"Error al editar afiliado: {str(e)}")
            return "<h1>Ha ocurrido un error. Inténtelo más tarde.</h1>"


# Ruta para avisos
@app.route('/avisos', methods=['GET'])
def avisos():
    try:
        cur = db.cursor()
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
    except Exception as e:
        app.logger.error(f"Error al obtener avisos: {str(e)}")
        return "<h1>Ha ocurrido un error. Inténtelo más tarde.</h1>"


if _name_ == '_main_':
    app.run(debug=True)