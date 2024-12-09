from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
from email.mime.application import MIMEApplication  # Importación de MIMEApplication
import pandas as pd
from flask import request, jsonify
#from send_email import send_email_with_excel

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Permitir acceso desde cualquier origen para rutas de la API

def get_db_connection():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=ESADC01;DATABASE=GestionTarifas;UID=sa;PWD=ESA.2008')
    return conn


# Ruta para obtener todas las tarifas con filtros
@app.route('/api/tarifario', methods=['GET'])
def get_tarifario():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Construir la consulta base
    query = '''
        SELECT t.id, cl.nombre as cliente,
                c.nombre as categoria, 
                u.nombre as unidad,  
                i.nombre as item, 
                t.precio, 
                t.minimo, 
                t.Incremento as incremento, 
                t.fecha_vigencia_inicio, 
                t.fecha_vigencia_final
            FROM tarifariogeneral_1 t 
            INNER JOIN item i ON i.id = t.item_id
            INNER JOIN Categoria c ON i.categoria = c.id
            INNER JOIN cliente cl ON t.cliente_id = cl.id
            INNER JOIN Unidades u ON t.unidad_id = u.id
    '''
    
    conditions = []
    params = []

    # Agregar filtros basados en parámetros de consulta
    if 'cliente' in request.args and request.args['cliente']:
        conditions.append('t.cliente_id = ?')
        params.append(int(request.args['cliente']))  # Convertir a entero si es necesario

    if 'item' in request.args and request.args['item']:
        conditions.append('t.item_id = ?')
        params.append(int(request.args['item']))  # Convertir a entero si es necesario

    if 'unidad' in request.args and request.args['unidad']:
        conditions.append('t.unidad_id = ?')
        params.append(int(request.args['unidad']))  # Convertir a entero si es necesario

    if 'categoria' in request.args and request.args['categoria']:
        conditions.append('i.categoria = ?')
        params.append(int(request.args['categoria']))  # Convertir a entero si es necesario

    if 'fechaInicio' in request.args and 'fechaFin' in request.args:
        if request.args['fechaInicio'] and request.args['fechaFin']:
            conditions.append('t.fecha_vigencia_inicio >= ? AND t.fecha_vigencia_final <= ?')
            params.append(request.args['fechaInicio'])
            params.append(request.args['fechaFin'])

    # Si hay condiciones, agregarlas a la consulta
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    # Debugging: imprime la consulta y los parámetros
    print("Consulta SQL:", query)
    print("Parámetros:", params)

    cursor.execute(query, params)
    tarifariogeneral = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tarifariogeneral)


@app.route('/api/tarifario', methods=['POST'])
def TarifasRango():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No se proporcionaron datos"}), 400

        required_fields = ['cliente_id', 'unidad_id', 'item_id', 'precio', 'incremento', 'fecha_vigencia_inicio']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Faltan campos obligatorios"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT * FROM tarifariogeneral_1 
            WHERE cliente_id = ? AND unidad_id = ? AND item_id = ?
        '''
        params = (data['cliente_id'], data['unidad_id'], data['item_id'])
        cursor.execute(query, params)
        existing_tarifa = cursor.fetchone()

        # Convertir valores y verificar tipo
        precio = float(data['precio'])
        incremento = float(data['incremento'])
        
        print("Tipo de precio:", type(precio), "Valor de precio:", precio)
        print("Tipo de incremento:", type(incremento), "Valor de incremento:", incremento)

        query = '''
            INSERT INTO tarifariogeneral_1 (cliente_id, unidad_id, item_id, precio, minimo, incremento, fecha_vigencia_inicio, fecha_vigencia_final) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data['cliente_id'],
            data['unidad_id'],
            data['item_id'],
            precio,
            data.get('minimo', None),  # Minimo puede ser opcional
            incremento,
            data['fecha_vigencia_inicio'],
            data.get('fecha_vigencia_final', None)
        )

        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return jsonify({"message": "Tarifa agregada exitosamente"}), 201
    except Exception as e:
        return jsonify({"message": "Error al agregar la tarifa", "error": str(e)}), 500




# Ruta para editar una tarifa existente
@app.route('/api/tarifario/<int:id>', methods=['PUT'])
def editar_tarifa(id):
    data = request.json
    print(data)
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        UPDATE tarifariogeneral_1 
        SET cliente_id = ?, unidad_id = ?, item_id = ?, precio = ?, minimo = ?, fecha_vigencia_inicio = ?, fecha_vigencia_final = ? 
        WHERE id = ?
    '''
    params = (
        data['cliente_id'],
        data['unidad_id'],
        data['item_id'],
        data['precio'],
        data.get('minimo', None),
        data['fecha_vigencia_inicio'],
        data.get('fecha_vigencia_final', None),
        id
    )

    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return jsonify({"message": "Tarifa actualizada exitosamente"})

# Ruta para eliminar una tarifa existente
@app.route('/api/tarifario/<int:id>', methods=['DELETE'])
def eliminar_tarifa(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'DELETE FROM tarifariogeneral_1 WHERE id = ?'
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Tarifa eliminada exitosamente"})

# Ruta para filtrar tarifas por fecha de vigencia y unidad
@app.route('/api/tarifario/filtrar', methods=['POST'])
def filtrar_tarifas():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT t.*, i.categoria 
        FROM tarifariogeneral_1 t 
        LEFT JOIN item i ON t.item_id = i.id
        WHERE t.unidad_id = ? AND t.fecha_vigencia_inicio >= ? AND t.fecha_vigencia_final <= ?
    '''
    params = (
        data['unidad_id'],
        data['fecha_inicio'],
        data['fecha_final']
    )

    cursor.execute(query, params)
    tarifas_filtradas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return jsonify(tarifas_filtradas)
#--------------------------------TARIFARIO_CON_RANGOS---------------------------
# Ruta para obtener todas las tarifas con filtros
@app.route('/api/tarifarioRango', methods=['GET'])
def get_tarifarioRango():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Construir la consulta base
    query = '''
        SELECT t.id, cl.nombre AS cliente,
               c.nombre AS categoria, 
               u.nombre AS unidad,  
               i.nombre AS item, 
               t.precio, 
               t.desde, 
               t.hasta, 
               t.incremento, 
               t.fecha_vigencia_inicio, 
               t.fecha_vigencia_final
          FROM TarifarioGeneral_2 t 
          INNER JOIN item i ON i.id = t.item_id
          INNER JOIN Categoria c ON i.categoria = c.id
          INNER JOIN cliente cl ON t.cliente_id = cl.id
          INNER JOIN Unidades u ON t.unidad_id = u.id
    '''
    conditions = []
    params = []

    # Agregar filtros basados en parámetros de consulta
    if 'cliente' in request.args:
        conditions.append('t.cliente_id = ?')
        params.append(request.args.get('cliente'))
    if 'item' in request.args:
        conditions.append('t.item_id = ?')
        params.append(request.args.get('item'))
    if 'unidad' in request.args:
        conditions.append('t.unidad_id = ?')
        params.append(request.args.get('unidad'))
    if 'categoria' in request.args:
        conditions.append('i.categoria = ?')
        params.append(request.args.get('categoria'))
    if 'fechaInicio' in request.args and 'fechaFin' in request.args:
        conditions.append('t.fecha_vigencia_inicio >= ? AND t.fecha_vigencia_final <= ?')
        params.append(request.args.get('fechaInicio'))
        params.append(request.args.get('fechaFin'))

    # Si hay condiciones, agregarlas a la consulta
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    tarifariogeneral = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tarifariogeneral)

# Ruta para agregar una tarifa
@app.route('/api/tarifarioRango', methods=['POST'])
def agregar_tarifaRango():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No se proporcionaron datos"}), 400

        required_fields = ['cliente_id', 'unidad_id', 'item_id', 'precio', 'incremento', 'fecha_vigencia_inicio']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Faltan campos obligatorios"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Convertir valores y verificar tipo
        precio = float(data['precio'])
        incremento = float(data['incremento'])
        desde = float(data.get('desde', 0))
        hasta = float(data.get('hasta', 0))

        query = '''
            INSERT INTO TarifarioGeneral_2 (cliente_id, unidad_id, item_id, precio, desde, hasta, incremento, fecha_vigencia_inicio, fecha_vigencia_final) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data['cliente_id'],
            data['unidad_id'],
            data['item_id'],
            precio,
            desde,
            hasta,
            incremento,
            data['fecha_vigencia_inicio'],
            data.get('fecha_vigencia_final', None)
        )

        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return jsonify({"message": "Tarifa agregada exitosamente"}), 201
    except Exception as e:
        return jsonify({"message": "Error al agregar la tarifa", "error": str(e)}), 500

# Ruta para editar una tarifa existente
@app.route('/api/tarifarioRango/<int:id>', methods=['PUT'])
def editar_tarifaRango(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        UPDATE TarifarioGeneral_2 
        SET cliente_id = ?, unidad_id = ?, item_id = ?, precio = ?, desde = ?, hasta = ?, incremento = ?, fecha_vigencia_inicio = ?, fecha_vigencia_final = ? 
        WHERE id = ?
    '''
    params = (
        data['cliente_id'],
        data['unidad_id'],
        data['item_id'],
        data['precio'],
        data.get('desde', None),
        data.get('hasta', None),
        data['incremento'],
        data['fecha_vigencia_inicio'],
        data.get('fecha_vigencia_final', None),
        id
    )

    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return jsonify({"message": "Tarifa actualizada exitosamente"})

# Ruta para eliminar una tarifa existente
@app.route('/api/tarifarioRango/<int:id>', methods=['DELETE'])
def eliminar_tarifaRango(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'DELETE FROM TarifarioGeneral_2 WHERE id = ?'
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Tarifa eliminada exitosamente"})

# Ruta para filtrar tarifas por fecha de vigencia y unidad
@app.route('/api/tarifarioRango/filtrar', methods=['POST'])
def filtrar_tarifasRango():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT t.*, i.categoria 
        FROM TarifarioGeneral_2 t 
        LEFT JOIN item i ON t.item_id = i.id
        WHERE t.unidad_id = ? AND t.fecha_vigencia_inicio >= ? AND t.fecha_vigencia_final <= ?
    '''
    params = (
        data['unidad_id'],
        data['fecha_inicio'],
        data['fecha_final']
    )

    cursor.execute(query, params)
    tarifas_filtradas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return jsonify(tarifas_filtradas)
#---------------------------------------------Maestros
@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item')
    items = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/categorias', methods=['GET'])
def get_categoria():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Categoria')
    categoria = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(categoria)

@app.route('/api/unidades', methods=['GET'])
def get_unidades():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM unidades')
    unidades = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(unidades)

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cliente')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clientes)

@app.route('/api/actualizacion_masiva_tarifas', methods=['POST'])
def actualizacion_masiva_tarifas():
    datos = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        criterio = datos['criterio']
        seleccion_id = datos['seleccionId']
        incluir_cliente = datos['incluirCliente']
        cliente_id = datos['clienteId']
        fecha_inicio = datos['fechaInicio']
        fecha_fin = datos['fechaFin']
        porcentaje = float(str(datos['porcentaje']))  # Convertir a float
        usuario = datos['usuario']
        
        print(f"Criterio: {criterio}, Selección ID: {seleccion_id}")
        print(f"Incluir cliente: {incluir_cliente}, Cliente ID: {cliente_id}")
        print(f"Fechas: {fecha_inicio} - {fecha_fin}, Porcentaje: {porcentaje}")

        # Construir la consulta base
        query = '''
            SELECT t.* 
            FROM tarifariogeneral_1 t
            JOIN item i ON t.item_id = i.id
            WHERE 1=1
        '''
        params = []

        # Agregar condiciones según el criterio
        if criterio == 'cliente':
            query += ' AND t.cliente_id = ?'
            params.append(int(seleccion_id))
        elif criterio == 'item':
            query += ' AND t.item_id = ?'
            params.append(int(seleccion_id))
        elif criterio == 'unidad':
            query += ' AND t.unidad_id = ?'
            params.append(int(seleccion_id))
        elif criterio == 'categoria':
            query += ' AND i.categoria = ?'
            params.append(seleccion_id)

        if incluir_cliente:
            query += ' AND t.cliente_id = ?'
            params.append(int(cliente_id))

        print(f"Query: {query}")
        print(f"Params: {params}")

        # Obtener las tarifas afectadas
        cursor.execute(query, params)
        tarifas_afectadas = cursor.fetchall()

        print(f"Número de tarifas afectadas: {len(tarifas_afectadas)}")

        # Calcular el factor de aumento
        factor = float('1') + (porcentaje / float('100'))

        # Actualizar las tarifas
        for tarifa in tarifas_afectadas:
            # Insertar la tarifa actual en el histórico
            cursor.execute('''
                INSERT INTO tarifariogeneralhistorico 
                (id, item_id, unidad_id, cliente_id, minimo, precio, fecha_vigencia_inicio, fecha_vigencia_final, usuario, fecha_movimiento, accion, incremento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 1, ?)
            ''', (tarifa.id, tarifa.item_id, tarifa.unidad_id, tarifa.cliente_id, tarifa.minimo, 
                  tarifa.precio, tarifa.fecha_vigencia_inicio, tarifa.fecha_vigencia_final, 
                  usuario, tarifa.incremento))

            # Actualizar la tarifa en tarifariogeneral_1
            nuevo_precio = float(str(tarifa.precio)) * factor
            cursor.execute('''
                UPDATE tarifariogeneral_1
                SET precio = ?, fecha_vigencia_inicio = ?, fecha_vigencia_final = ?, incremento = ?
                WHERE id = ?
            ''', (nuevo_precio, fecha_inicio, fecha_fin, porcentaje, tarifa.id))

        conn.commit()
        return jsonify({'message': f'Se actualizaron {len(tarifas_afectadas)} tarifas correctamente'}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar tarifas: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/api/tarifas-vencidas', methods=['GET'])
def get_tarifas_vencidas():
    conn = get_db_connection()
    cursor = conn.cursor()    
    query = f'''
        SELECT DISTINCT 
            c.id, 
            c.nombre
        FROM tarifariogeneral_1 t
        JOIN cliente c ON t.cliente_id = c.id
        JOIN item i ON t.item_id = i.id
        WHERE t.fecha_vigencia_final <=getdate()+20
        
    '''
    
    cursor.execute(query)
    
    clientes_vencidos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clientes_vencidos)





@app.route('/api/tarifas_historicas', methods=['GET'])
def get_tarifas_historicas():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Diccionario para los filtros
    filters = {}
    if 'cliente' in request.args:
        filters['H.cliente_id'] = int(request.args['cliente'])
    if 'categoria' in request.args:
        filters['i.categoria'] = request.args['categoria']
    if 'unidad' in request.args:
        filters['H.unidad_id'] = int(request.args['unidad'])
    if 'item' in request.args:
        filters['H.item_id'] = int(request.args['item'])
    
    # Manejo de fechas
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    fecha_movimiento = request.args.get('fecha_movimiento')

    # Consulta base
    query = '''
    SELECT 
           cl.nombre as cliente, 
           c.nombre as categoria, 
           u.nombre as unidad, 
           i.nombre as item,
           H.minimo as minimo, 
           H.Incremento as incremento,
           H.precio as precio,
           H.fecha_vigencia_inicio as fechadesde, 
           H.fecha_vigencia_final as fechahasta,
           H.fecha_movimiento as movimiento   
    FROM tarifariogeneralhistorico H 
    JOIN item i ON H.item_id = i.id 
    JOIN categoria c ON i.categoria = c.id 
    JOIN cliente cl ON H.cliente_id = cl.id 
    JOIN Unidades u ON H.unidad_id = u.id
    '''

    # Construir las condiciones de la cláusula WHERE
    conditions = []
    params = []

    for field, value in filters.items():
        conditions.append(f"{field} = ?")  # Usamos "?" para marcadores de parámetros en pyodbc
        params.append(value)

    # Filtros de rango para fecha
    if fecha_inicio:
        conditions.append("H.fecha_vigencia_inicio >= ?")
        params.append(fecha_inicio)
    if fecha_fin:
        conditions.append("H.fecha_vigencia_final <= ?")
        params.append(fecha_fin)
    if fecha_movimiento:
        conditions.append("H.fecha_movimiento = ?")
        params.append(fecha_movimiento)

    # Agregar las condiciones a la consulta si existen
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
        cursor.execute(query, params)  # Ejecuta con parámetros solo si hay condiciones
    else:
        cursor.execute(query)  # Ejecuta sin parámetros si no hay condiciones

    # Obtener los resultados y cerrar la conexión
    tarifas_historicas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tarifas_historicas)



# Configuración del servidor SMTP
SMTP_SERVER = 'mail.esalogistica.com.ar'  # Servidor de correo saliente
SMTP_PORT = 465  # Puerto SMTP
USERNAME = 'dmartucci@esalogistica.com.ar'  # Tu correo
PASSWORD = 'Esalog.4414'  # Tu contraseña

@app.route('/api/tarifarioUnico', methods=['GET'])
def get_tarifas_unicas():
    cliente_id = request.args.get('cliente_id')  # Obtener el parámetro cliente_id de la URL
    
    if not cliente_id:
        return {"error": "cliente_id es requerido"}, 400  # Verificar si se pasó el parámetro

    print(f"Cliente ID recibido: {cliente_id}")  # Para depuración

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT cl.nombre,
                c.nombre, 
                u.nombre,  
                t.precio, 
                t.minimo, 
                t.Incremento, 
                t.fecha_vigencia_inicio, 
                t.fecha_vigencia_final
            FROM tarifariogeneral_1 t 
            INNER JOIN item i ON i.id = t.item_id
            INNER JOIN categoria c ON i.categoria = c.id
            INNER JOIN cliente cl ON t.cliente_id = cl.id
            INNER JOIN Unidades u ON t.unidad_id = u.id
            WHERE t.cliente_id = ?
        '''
        cursor.execute(query, (cliente_id,))
        tarifas = cursor.fetchall()

        resultado = [{"cliente": row[0], "categoria": row[1], "unidad": row[2], "precio": row[3], 
                      "minimo": row[4], "incremento": row[5], "fecha_vigencia_inicio": row[6], 
                      "fecha_vigencia_final": row[7]} for row in tarifas]

        return {"tarifas": resultado}, 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": "Ocurrió un error al procesar la solicitud."}, 500

    finally:
        cursor.close()
        conn.close()

def obtener_tarifario_filtrado(cliente_id):
    url = f"http://192.168.1.10:5000/api/tarifarioUnico?cliente_id={cliente_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data["tarifas"])
    else:
        raise Exception("Error al consultar la API de tarifarios")

def generar_archivo_excel(cliente_id):
    df = obtener_tarifario_filtrado(cliente_id)
    archivo_excel = f"tarifario_cliente_{cliente_id}.xlsx"
    df.to_excel(archivo_excel, index=False)
    return archivo_excel

@app.route('/api/reportes/valores_prep', methods=['GET'])
def valores_prep():
    conn=get_db_connection()
    cursor = conn.cursor()

    query='''select c.nombre, vp.* from ValPrepKilos vp inner join cliente c on vp.cliente=c.id'''

    cursor.execute(query)
    vpk = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(vpk)




@app.route('/api/reportes/valores_prep', methods=['POST'])
def  valores_prep_post():   
    data=request.json
    conn=get_db_connection()
    cursor = conn.cursor()
    query = '''
        INSERT INTO ValPrepKilos  (cliente, fecha_inicio, fecha_final, valor_kilo_prep)
        values(?,?,?,?)

    '''
    params = (
        data['cliente_id'],
        data['fecha_inicio'],
        data['fecha_final'],
        data['valor']
    )

    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return  jsonify({'message': 'Valor prep kilo agregado correctamente'}), 201
'''
@app.route('/api/send-tarifas-report', methods=['POST'])
def send_report():
    data = request.json
    email = data.get('email')
    client_id = data.get('clientId')

    if not email or not client_id:
        return jsonify({"error": "Email y clientId son requeridos"}), 400

    try:
        send_email_with_excel(email, client_id)
        return jsonify({"message": "Correo enviado con éxito"}), 200
    except Exception as e:
        print(f'Error al enviar el correo: {e}')
        return jsonify({"error": "Error al enviar el correo"}), 500
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)
