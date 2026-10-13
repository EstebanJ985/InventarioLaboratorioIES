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

                # VALIDAR STOCK ANTES DE CREAR EL PEDIDO
        for material in materiales:

            id_material = material.get("productoId")
            cantidad_solicitada = material.get("cantidad", 0)

            if cantidad_solicitada <= 0:
                return jsonify({
                    "error": "La cantidad solicitada debe ser mayor a 0"
                }), 400

            consulta_stock = """
                SELECT
                    materiales.nombre,
                    stock.cantidad
                FROM stock
                JOIN materiales
                    ON stock.id_material = materiales.id_material
                WHERE materiales.id_material = %s
            """

            cursor.execute(
                consulta_stock,
                (id_material,)
            )

            resultado_stock = cursor.fetchone()

            if resultado_stock is None:
                return jsonify({
                    "error": "El material solicitado no existe"
                }), 404

            nombre_material = resultado_stock[0]
            stock_disponible = resultado_stock[1]

            if cantidad_solicitada > stock_disponible:
                return jsonify({
                    "error":
                        f"Stock insuficiente para {nombre_material}. "
                        f"Disponible: {stock_disponible}"
                }), 400

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


@app.route(
    "/api/pedidos/<int:id_pedido>/preparar",
    methods=["PATCH"]
)
def preparar_pedido(id_pedido):

    cursor = conexion.cursor()

    try:

        consulta = """
            UPDATE pedidos
            SET estado = 'Preparado'
            WHERE id_pedido = %s
            AND estado = 'Pendiente'
        """

        cursor.execute(
            consulta,
            (id_pedido,)
        )

        if cursor.rowcount == 0:

            return jsonify({
                "error":
                    "El pedido no existe o ya no está pendiente"
            }), 400

        conexion.commit()

        return jsonify({
            "mensaje":
                "Pedido preparado correctamente"
        }), 200

    except mysql.connector.Error as error:

        conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        cursor.close()


@app.route(
    "/api/pedidos/<int:id_pedido>/entregar",
    methods=["PATCH"]
)
def entregar_pedido(id_pedido):

    cursor = conexion.cursor()

    try:

        # =========================================
        # 1. VERIFICAR QUE EL PEDIDO ESTÉ PREPARADO
        # =========================================

        consulta_pedido = """
            SELECT
                responsable,
                practica,
                estado
            FROM pedidos
            WHERE id_pedido = %s
        """

        cursor.execute(
            consulta_pedido,
            (id_pedido,)
        )

        pedido = cursor.fetchone()

        if pedido is None:

            return jsonify({
                "error": "El pedido no existe"
            }), 404


        responsable = pedido[0]
        practica = pedido[1]
        estado = pedido[2]


        if estado != "Preparado":

            return jsonify({
                "error":
                    "Solo se pueden entregar pedidos preparados"
            }), 400


        # =========================================
        # 2. OBTENER LOS MATERIALES DEL PEDIDO
        # =========================================

        consulta_materiales = """
            SELECT
                detalle_pedido.id_material,
                detalle_pedido.cantidad_solicitada,
                materiales.nombre
            FROM detalle_pedido

            JOIN materiales
                ON detalle_pedido.id_material =
                   materiales.id_material

            WHERE detalle_pedido.id_pedido = %s
        """

        cursor.execute(
            consulta_materiales,
            (id_pedido,)
        )

        materiales_pedido = cursor.fetchall()


        # =========================================
        # 3. VALIDAR STOCK
        # =========================================

        for material in materiales_pedido:

            id_material = material[0]
            cantidad = material[1]
            nombre = material[2]

            consulta_stock = """
                SELECT
                    id_stock,
                    cantidad,
                    id_ubicacion
                FROM stock
                WHERE id_material = %s
            """

            cursor.execute(
                consulta_stock,
                (id_material,)
            )

            stock_actual = cursor.fetchone()

            if stock_actual is None:

                return jsonify({
                    "error":
                        f"No existe stock para {nombre}"
                }), 400


            cantidad_disponible = stock_actual[1]


            if cantidad > cantidad_disponible:

                return jsonify({
                    "error":
                        f"Stock insuficiente para {nombre}. "
                        f"Disponible: {cantidad_disponible}"
                }), 400


        # =========================================
        # 4. DESCONTAR STOCK
        # =========================================

        for material in materiales_pedido:

            id_material = material[0]
            cantidad = material[1]

            consulta_stock = """
                SELECT
                    id_stock,
                    cantidad,
                    id_ubicacion
                FROM stock
                WHERE id_material = %s
            """

            cursor.execute(
                consulta_stock,
                (id_material,)
            )

            stock_actual = cursor.fetchone()


            id_stock = stock_actual[0]

            id_ubicacion = stock_actual[2]


            actualizar_stock = """
                UPDATE stock
                SET cantidad = cantidad - %s
                WHERE id_stock = %s
            """

            cursor.execute(
                actualizar_stock,
                (
                    cantidad,
                    id_stock
                )
            )


            # =====================================
            # 5. REGISTRAR MOVIMIENTO DE SALIDA
            # =====================================

            registrar_movimiento = """
                INSERT INTO movimientos (
                id_material,
                id_ubicacion,
                tipo,
                cantidad,
                responsable,
                motivo,
                id_pedido
            )
            VALUES (
                %s,
                %s,
                'Salida',
                %s,
                %s,
                %s,
                %s
            )
        """

            cursor.execute(
                registrar_movimiento,
                (
                    id_material,
                    id_ubicacion,
                    cantidad,
                    responsable,
                    f"Entrega de pedido - {practica}",
                    id_pedido
                )
            )


            # =====================================
            # 6. MARCAR CANTIDAD ENTREGADA
            # =====================================

            actualizar_detalle = """
                UPDATE detalle_pedido
                SET cantidad_entregada =
                    cantidad_solicitada
                WHERE id_pedido = %s
                AND id_material = %s
            """

            cursor.execute(
                actualizar_detalle,
                (
                    id_pedido,
                    id_material
                )
            )


        # =========================================
        # 7. CAMBIAR ESTADO DEL PEDIDO
        # =========================================

        actualizar_pedido = """
            UPDATE pedidos
            SET estado = 'Entregado'
            WHERE id_pedido = %s
        """

        cursor.execute(
            actualizar_pedido,
            (id_pedido,)
        )


        # =========================================
        # 8. CONFIRMAR TODO
        # =========================================

        conexion.commit()


        return jsonify({
            "mensaje":
                "Pedido entregado correctamente"
        }), 200


    except mysql.connector.Error as error:

        conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500


    finally:

        cursor.close()


    # ======================================================
# OBTENER MOVIMIENTOS
# ======================================================

@app.route(
    "/api/movimientos",
    methods=["GET"]
)
def obtener_movimientos():

    cursor = conexion.cursor(
        dictionary=True
    )

    try:

        consulta = """
            SELECT
                movimientos.id_movimiento,
                movimientos.tipo,
                movimientos.cantidad,
                movimientos.fecha,
                movimientos.responsable,
                movimientos.motivo,
                movimientos.id_pedido,

                materiales.codigo,
                materiales.nombre AS material,

                armarios.numero AS armario,
                ubicaciones.estante,
                ubicaciones.sector

            FROM movimientos

            JOIN materiales
                ON movimientos.id_material =
                   materiales.id_material

            JOIN ubicaciones
                ON movimientos.id_ubicacion =
                   ubicaciones.id_ubicacion

            JOIN armarios
                ON ubicaciones.id_armario =
                   armarios.id_armario

            ORDER BY
                movimientos.fecha DESC,
                movimientos.id_movimiento DESC
        """

        cursor.execute(
            consulta
        )

        movimientos = cursor.fetchall()

        for movimiento in movimientos:

            if movimiento["fecha"]:

                movimiento["fecha"] = (
                    movimiento["fecha"]
                    .isoformat()
                )

        return jsonify(
            movimientos
        ), 200

    except mysql.connector.Error as error:

        return jsonify({
            "error": str(error)
        }), 500

    finally:

        cursor.close()


@app.route(
    "/api/pedidos/<int:id_pedido>/devolver",
    methods=["PATCH"]
)
def devolver_pedido(id_pedido):
    cursor = conexion.cursor()

    try:

        # =========================================
        # 1. VERIFICAR PEDIDO
        # =========================================

        consulta_pedido = """
            SELECT
                responsable,
                practica,
                estado
            FROM pedidos
            WHERE id_pedido = %s
        """

        cursor.execute(
            consulta_pedido,
            (id_pedido,)
        )

        pedido = cursor.fetchone()

        if pedido is None:

            return jsonify({
                "error": "El pedido no existe"
            }), 404


        responsable = pedido[0]
        practica = pedido[1]
        estado = pedido[2]


        if estado != "Entregado":

            return jsonify({
                "error":
                    "Solo se pueden devolver pedidos entregados"
            }), 400


        # =========================================
        # 2. OBTENER MATERIALES ENTREGADOS
        # =========================================

        consulta_materiales = """
            SELECT
                detalle_pedido.id_material,
                detalle_pedido.cantidad_entregada,
                materiales.nombre
            FROM detalle_pedido

            JOIN materiales
                ON detalle_pedido.id_material =
                   materiales.id_material

            WHERE detalle_pedido.id_pedido = %s
        """

        cursor.execute(
            consulta_materiales,
            (id_pedido,)
        )

        materiales_pedido = cursor.fetchall()


        # =========================================
        # 3. DEVOLVER STOCK
        # =========================================

        for material in materiales_pedido:

            id_material = material[0]
            cantidad_devuelta = material[1]
            nombre = material[2]


            if cantidad_devuelta <= 0:

                continue


            consulta_stock = """
                SELECT
                    id_stock,
                    id_ubicacion
                FROM stock
                WHERE id_material = %s
            """

            cursor.execute(
                consulta_stock,
                (id_material,)
            )

            stock_actual = cursor.fetchone()


            if stock_actual is None:

                return jsonify({
                    "error":
                        f"No existe stock para {nombre}"
                }), 400


            id_stock = stock_actual[0]
            id_ubicacion = stock_actual[1]


            actualizar_stock = """
                UPDATE stock
                SET cantidad = cantidad + %s
                WHERE id_stock = %s
            """

            cursor.execute(
                actualizar_stock,
                (
                    cantidad_devuelta,
                    id_stock
                )
            )


            # =====================================
            # 4. REGISTRAR MOVIMIENTO
            # =====================================

            registrar_movimiento = """
                INSERT INTO movimientos (
                    id_material,
                    id_ubicacion,
                    tipo,
                    cantidad,
                    responsable,
                    motivo,
                    id_pedido
                )
                VALUES (
                    %s,
                    %s,
                    'Devolucion',
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                registrar_movimiento,
                (
                    id_material,
                    id_ubicacion,
                    cantidad_devuelta,
                    responsable,
                    f"Devolución de pedido - {practica}",
                    id_pedido
                )
            )


            # =====================================
            # 5. ACTUALIZAR DETALLE
            # =====================================

            actualizar_detalle = """
                UPDATE detalle_pedido
                SET cantidad_devuelta =
                    cantidad_entregada
                WHERE id_pedido = %s
                AND id_material = %s
            """

            cursor.execute(
                actualizar_detalle,
                (
                    id_pedido,
                    id_material
                )
            )


        # =========================================
        # 6. CAMBIAR ESTADO
        # =========================================

        actualizar_pedido = """
            UPDATE pedidos
            SET estado = 'Devuelto'
            WHERE id_pedido = %s
        """

        cursor.execute(
            actualizar_pedido,
            (id_pedido,)
        )


        conexion.commit()


        return jsonify({
            "mensaje":
                "Pedido devuelto correctamente"
        }), 200


    except mysql.connector.Error as error:

        conexion.rollback()

        return jsonify({
            "error": str(error)
        }), 500


    finally:

        cursor.close()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=False
    )