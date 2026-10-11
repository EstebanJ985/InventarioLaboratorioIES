import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, render_template, request
import mysql.connector

app = Flask(__name__)

# Conexión con MySQL
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="inventario_laboratorio"
)

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/inventario")
def obtener_inventario():

    cursor = conexion.cursor(dictionary=True)

    consulta = """
        SELECT
            materiales.id_material,
            materiales.codigo,
            materiales.nombre,
            armarios.numero AS armario,
            ubicaciones.estante,
            ubicaciones.sector,
            stock.cantidad AS stock,
            materiales.stock_minimo
        FROM stock
        JOIN materiales
            ON stock.id_material = materiales.id_material
        JOIN ubicaciones
            ON stock.id_ubicacion = ubicaciones.id_ubicacion
        JOIN armarios
            ON ubicaciones.id_armario = armarios.id_armario
    """

    cursor.execute(consulta)

    resultados = cursor.fetchall()

    cursor.close()

    return jsonify(resultados)


@app.route("/api/materiales", methods=["POST"])
def agregar_material():

    datos = request.get_json()

    codigo = datos.get("codigo")
    nombre = datos.get("nombre")
    categoria = datos.get("categoria")
    unidad_medida = datos.get("unidad_medida")
    stock_minimo = datos.get("stock_minimo", 0)
    descripcion = datos.get("descripcion")

    armario = datos.get("armario")
    estante = datos.get("estante")
    sector = datos.get("sector")
    cantidad = datos.get("cantidad", 0)

    cursor = conexion.cursor()

    try:

        # 1. Crear el material
        consulta_material = """
            INSERT INTO materiales (
                codigo,
                nombre,
                categoria,
                unidad_medida,
                stock_minimo,
                descripcion
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            consulta_material,
            (
                codigo,
                nombre,
                categoria,
                unidad_medida,
                stock_minimo,
                descripcion
            )
        )

        id_material = cursor.lastrowid


        # 2. Crear la ubicación
        consulta_ubicacion = """
            INSERT INTO ubicaciones (
                id_armario,
                estante,
                sector
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            consulta_ubicacion,
            (
                armario,
                estante,
                sector
            )
        )

        id_ubicacion = cursor.lastrowid


        # 3. Crear el stock inicial
        consulta_stock = """
            INSERT INTO stock (
                id_material,
                id_ubicacion,
                cantidad
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            consulta_stock,
            (
                id_material,
                id_ubicacion,
                cantidad
            )
        )


        conexion.commit()

        return jsonify({
            "mensaje": "Material registrado correctamente"
        }), 201


    except mysql.connector.Error as error:

        conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500


    finally:

        cursor.close()

@app.route("/api/pedidos", methods=["POST"])
def crear_pedido():

    datos = request.get_json()

    responsable = datos.get("responsable")
    practica = datos.get("practica")
    fecha_uso = datos.get("fecha")
    materiales = datos.get("materiales", [])

    cursor = conexion.cursor()

    try:

        consulta_pedido = """
            INSERT INTO pedidos (
                responsable,
                practica,
                fecha_uso
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            consulta_pedido,
            (
                responsable,
                practica,
                fecha_uso
            )
        )

        id_pedido = cursor.lastrowid

        consulta_detalle = """
            INSERT INTO detalle_pedido (
                id_pedido,
                id_material,
                cantidad_solicitada
            )
            VALUES (%s, %s, %s)
        """

        for material in materiales:

            cursor.execute(
                consulta_detalle,
                (
                    id_pedido,
                    material["productoId"],
                    material["cantidad"]
                )
            )

        conexion.commit()

        return jsonify({
            "mensaje": "Pedido creado correctamente",
            "id_pedido": id_pedido
        }), 201

    except mysql.connector.Error as error:

        conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        cursor.close()

@app.route("/api/pedidos", methods=["GET"])
def obtener_pedidos():

    cursor = conexion.cursor(dictionary=True)

    consulta = """
        SELECT
            p.id_pedido,
            p.responsable,
            p.practica,
            p.fecha_uso,
            p.estado,

            d.id_material,
            d.cantidad_solicitada,

            m.codigo,
            m.nombre,

            a.numero AS armario,
            u.estante,
            u.sector

        FROM pedidos AS p

        JOIN detalle_pedido AS d
            ON p.id_pedido = d.id_pedido

        JOIN materiales AS m
            ON d.id_material = m.id_material

        JOIN stock AS s
            ON m.id_material = s.id_material

        JOIN ubicaciones AS u
            ON s.id_ubicacion = u.id_ubicacion

        JOIN armarios AS a
            ON u.id_armario = a.id_armario

        ORDER BY
            p.id_pedido DESC,
            a.numero ASC,
            m.nombre ASC
    """

    cursor.execute(consulta)

    filas = cursor.fetchall()

    cursor.close()


    pedidos = {}


    for fila in filas:

        id_pedido = fila["id_pedido"]


        if id_pedido not in pedidos:

            pedidos[id_pedido] = {

                "id": id_pedido,

                "responsable":
                    fila["responsable"],

                "practica":
                    fila["practica"],

                "fecha":
                    fila["fecha_uso"].isoformat()
                    if fila["fecha_uso"]
                    else None,

                "estado":
                    fila["estado"],

                "materiales": []

            }


        pedidos[id_pedido]["materiales"].append({

            "productoId": fila["id_material"],

            "codigo": fila["codigo"],

            "nombre": fila["nombre"],

            "cantidad": fila["cantidad_solicitada"],

            "armario": fila["armario"],

            "estante": fila["estante"],

            "sector": fila["sector"]

    })


    return jsonify(list(pedidos.values()))

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=False
    )