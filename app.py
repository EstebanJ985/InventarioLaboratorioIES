import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, render_template
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


if __name__ == "__main__":
    app.run(debug=True)