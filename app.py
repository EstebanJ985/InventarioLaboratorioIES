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

if __name__ == "__main__":
    app.run(debug=True)