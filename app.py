from flask import Flask, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)

# Configuración de la base de datos MySQL (PlanetScale)
app.config['MYSQL_HOST'] = 'aws.connect.psdb.cloud'
app.config['MYSQL_USER'] = 'aqtup814u7543vka5ljg'  # Reemplaza con tu usuario de PlanetScale
app.config['MYSQL_PASSWORD'] = 'ppscale_pw_3aQ2k0qF4KdiAf0e86ffKOmsz1zbfojMioKyXwFvwAX'  # Reemplaza con tu contraseña
app.config['MYSQL_DB'] = 'sistema_afiliados'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuración de SSL
app.config['MYSQL_SSL_CA'] = '/etc/ssl/certs/ca-certificates.crt'  # Ruta del certificado SSL



mysql = MySQL(app)

@app.route('/test-db-connection', methods=['GET'])
def test_db_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE();")
        db_name = cur.fetchone()
        return f"Conexión exitosa a la base de datos: {db_name['DATABASE()']}"
    except Exception as e:
        return f"Error de conexión: {str(e)}<br>Verifica la configuración de SSL y las credenciales de PlanetScale."


# Función para generar una barra de navegación con el color personalizado
def generar_navbar():
    return '''
    <nav class="navbar navbar-expand-lg" style="background-color: #eb7042;">
        <div class="container-fluid">
            <a class="navbar-brand text-white" href="/">Sistema de Afiliados</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item"><a class="nav-link text-white" href="/formulario">Agregar Afiliado</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/afiliados">Listar Afiliados</a></li>
                    <li class="nav-item"><a class="nav-link text-white" href="/test-db">Test Conexión</a></li>
                </ul>
            </div>
        </div>
    </nav>
    '''

@app.route('/')
def home():
    return redirect(url_for('listar_afiliados'))

@app.route('/formulario', methods=['GET'])
def formulario():
    navbar = generar_navbar()
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agregar Afiliado</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        {navbar}
        <h1 class="text-center">Agregar Afiliado</h1>
        <form action="/agregar_afiliado" method="POST" class="mt-4">
            <div class="mb-3">
                <label for="nombre" class="form-label">Nombre:</label>
                <input type="text" id="nombre" name="nombre" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="estatus" class="form-label">Estatus:</label>
                <select id="estatus" name="estatus" class="form-select" required>
                    <option value="Vendedora">Vendedora</option>
                    <option value="Cliente">Cliente</option>
                </select>
            </div>
            <button type="submit" class="btn" style="background-color: #eb7042; color: white;">Agregar</button>
        </form>
    </body>
    </html>
    '''



@app.route('/afiliados', methods=['GET'])
def listar_afiliados():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Afiliados")
        afiliados = cur.fetchall()
        navbar = generar_navbar()
        tabla = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lista de Afiliados</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                function filtrar() {{
                    var input = document.getElementById("filtro").value.toLowerCase();
                    var filas = document.querySelectorAll("#tabla-afiliados tbody tr");
                    filas.forEach(fila => {{
                        var texto = fila.textContent.toLowerCase();
                        fila.style.display = texto.includes(input) ? "" : "none";
                    }});
                }}
            </script>
        </head>
        <body>
            {navbar}
            <h1 class="text-center">Lista de Afiliados</h1>
            <div class="mb-3">
                <input type="text" id="filtro" class="form-control" placeholder="Filtrar afiliados" onkeyup="filtrar()">
            </div>
            <table class="table table-striped table-bordered mt-4" id="tabla-afiliados">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Estatus</th>
                        <th>Fecha Registro</th>
                        <th>Puntos</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for afiliado in afiliados:
            tabla += f'''
                <tr>
                    <td>{afiliado['ID']}</td>
                    <td>{afiliado['Nombre']}</td>
                    <td>{afiliado['Estatus']}</td>
                    <td>{afiliado['FechaRegistro']}</td>
                    <td>{afiliado['Puntos']}</td>
                    <td>
                        <a href="/editar_afiliado/{afiliado['ID']}" class="btn btn-warning btn-sm">Editar</a>
                        <a href="/eliminar_afiliado/{afiliado['ID']}" class="btn btn-danger btn-sm" onclick="return confirm('¿Estás seguro de eliminar este afiliado?');">Eliminar</a>
                        <a href="/registrar_venta/{afiliado['ID']}" class="btn btn-primary btn-sm">Registrar Venta</a>
                        <a href="/ventas/{afiliado['ID']}" class="btn btn-info btn-sm">Ver Ventas</a>
                    </td>
                </tr>
            '''
        tabla += '''
                </tbody>
            </table>
        </body>
        </html>
        '''
        return tabla
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"


@app.route('/registrar_venta/<int:afiliado_id>', methods=['GET', 'POST'])
def registrar_venta(afiliado_id):
    if request.method == 'POST':
        modelo = request.form['modelo']
        talla = request.form['talla']
        fecha = request.form['fecha']
        
        if not fecha:  # Si no se proporciona una fecha, usa la fecha y hora actual
            fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Ventas (AfiliadoID, Modelo, Talla, Fecha)
                VALUES (%s, %s, %s, %s)
            """, (afiliado_id, modelo, talla, fecha))
            mysql.connection.commit()
            return redirect(url_for('listar_afiliados'))
        except Exception as e:
            return f"<h1>Error: {str(e)}</h1>"

    navbar = generar_navbar()
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registrar Venta</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        {navbar}
        <h1 class="text-center">Registrar Venta</h1>
        <form action="/registrar_venta/{afiliado_id}" method="POST">
            <div class="mb-3">
                <label for="modelo" class="form-label">Modelo:</label>
                <input type="text" id="modelo" name="modelo" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="talla" class="form-label">Talla:</label>
                <input type="text" id="talla" name="talla" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="fecha" class="form-label">Fecha y Hora:</label>
                <input type="datetime-local" id="fecha" name="fecha" class="form-control">
            </div>
            <button type="submit" class="btn" style="background-color: #eb7042; color: white;">Registrar</button>
        </form>
    </body>
    </html>
    '''

# Ruta para eliminar un afiliado
@app.route('/eliminar_afiliado/<int:id>', methods=['GET'])
def eliminar_afiliado(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Afiliados WHERE ID = %s", (id,))
        mysql.connection.commit()
        return redirect(url_for('listar_afiliados'))
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# Ruta para editar un afiliado
@app.route('/editar_afiliado/<int:id>', methods=['GET', 'POST'])
def editar_afiliado(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        estatus = request.form['estatus']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE Afiliados
                SET Nombre = %s, Estatus = %s
                WHERE ID = %s
            """, (nombre, estatus, id))
            mysql.connection.commit()
            return redirect(url_for('listar_afiliados'))
        except Exception as e:
            return f"<h1>Error: {str(e)}</h1>"

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Afiliados WHERE ID = %s", (id,))
        afiliado = cur.fetchone()
        navbar = generar_navbar()
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Editar Afiliado</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </head>
        <body>
            {navbar}
            <h1 class="text-center">Editar Afiliado</h1>
            <form action="/editar_afiliado/{id}" method="POST" class="mt-4">
                <div class="mb-3">
                    <label for="nombre" class="form-label">Nombre:</label>
                    <input type="text" id="nombre" name="nombre" class="form-control" value="{afiliado['Nombre']}" required>
                </div>
                <div class="mb-3">
                    <label for="estatus" class="form-label">Estatus:</label>
                    <select id="estatus" name="estatus" class="form-select" required>
                        <option value="Vendedora" {"selected" if afiliado['Estatus'] == "Vendedora" else ""}>Vendedora</option>
                        <option value="Cliente" {"selected" if afiliado['Estatus'] == "Cliente" else ""}>Cliente</option>
                    </select>
                </div>
                <button type="submit" class="btn" style="background-color: #eb7042; color: white;">Guardar</button>
            </form>
        </body>
        </html>
        '''
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

#Ruta para Ver Ventas de un Afiliado
@app.route('/ventas/<int:afiliado_id>', methods=['GET'])
def ver_ventas(afiliado_id):
    try:
        cur = mysql.connection.cursor()
        # Obtener la información del afiliado
        cur.execute("SELECT * FROM Afiliados WHERE ID = %s", (afiliado_id,))
        afiliado = cur.fetchone()

        if not afiliado:
            return f"<h1>Error: No se encontró al afiliado con ID {afiliado_id}</h1>"

        # Obtener las ventas del afiliado
        cur.execute("SELECT * FROM Ventas WHERE AfiliadoID = %s", (afiliado_id,))
        ventas = cur.fetchall()

        navbar = generar_navbar()
        ventas_tabla = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ventas de {afiliado['Nombre']}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </head>
        <body>
            {navbar}
            <h1 class="text-center">Ventas de {afiliado['Nombre']}</h1>
            <table class="table table-striped table-bordered mt-4">
                <thead>
                    <tr>
                        <th>ID Venta</th>
                        <th>Modelo</th>
                        <th>Talla</th>
                        <th>Fecha</th>
                        <th>Puntos MB</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for venta in ventas:
            ventas_tabla += f'''
                <tr>
                    <td>{venta['ID']}</td>
                    <td>{venta['Modelo']}</td>
                    <td>{venta['Talla']}</td>
                    <td>{venta['Fecha'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td>{venta['PuntosMB']}</td>
                </tr>
            '''
        ventas_tabla += '''
                </tbody>
            </table>
            <a href="/afiliados" class="btn btn-secondary">Regresar a la lista de afiliados</a>
        </body>
        </html>
        '''
        return ventas_tabla
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

#agregar afiliado
@app.route('/agregar_afiliado', methods=['POST'])
def agregar_afiliado():
    try:
        # Recibe los datos del formulario
        nombre = request.form['nombre']
        estatus = request.form['estatus']

        # Inserta el nuevo afiliado
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Afiliados (Nombre, Estatus) VALUES (%s, %s)", (nombre, estatus))
        mysql.connection.commit()

        # Redirige a la lista de afiliados
        return redirect(url_for('listar_afiliados'))
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"


#AVISOS
@app.route('/avisos', methods=['GET'])
def avisos():
    try:
        cur = mysql.connection.cursor()
        
        # Avisos para clientes: Última compra hace 2 meses
        cur.execute("""
            SELECT A.ID, A.Nombre, MAX(V.Fecha) AS UltimaCompra
            FROM Afiliados A
            INNER JOIN Ventas V ON A.ID = V.AfiliadoID
            WHERE A.Estatus = 'Cliente'
            GROUP BY A.ID, A.Nombre
            HAVING DATEDIFF(CURDATE(), MAX(V.Fecha)) >= 60
        """)
        clientes_avisos = cur.fetchall()

        # Avisos para vendedoras: Cronómetro desde la primera compra
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

        # Generar la vista
        navbar = generar_navbar()
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Avisos</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </head>
        <body>
            {navbar}
            <h1 class="text-center">Avisos</h1>
            <h2>Clientes con compras hace 2 meses</h2>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Última Compra</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for cliente in clientes_avisos:
            html += f'''
                <tr>
                    <td>{cliente['ID']}</td>
                    <td>{cliente['Nombre']}</td>
                    <td>{cliente['UltimaCompra']}</td>
                </tr>
            '''
        html += '''
                </tbody>
            </table>

            <h2>Vendedoras con menos de 2 días restantes para el cronómetro</h2>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Primera Compra</th>
                        <th>Días Restantes</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for vendedora in vendedoras_avisos:
            html += f'''
                <tr>
                    <td>{vendedora['ID']}</td>
                    <td>{vendedora['Nombre']}</td>
                    <td>{vendedora['PrimeraCompra']}</td>
                    <td>{vendedora['DiasRestantes']}</td>
                </tr>
            '''
        html += '''
                </tbody>
            </table>
        </body>
        </html>
        '''
        return html
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"


if __name__ == '__main__':
    app.run(debug=True)

