import sqlite3
from producto import Producto


class Inventario:

    DB_NAME = "pedidos.db"

    def __init__(self, db_name=None):

        if db_name:
            self.DB_NAME = db_name

        self._crear_tabla()


    def _conectar(self):
        return sqlite3.connect(self.DB_NAME)


    def _crear_tabla(self):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Producto(

                    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    categoria TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL

                )
            """)

            conn.commit()

    def agregar_producto(self,
                         nombre,
                         categoria,
                         precio,
                         stock):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Producto
                (nombre,categoria,precio,stock)

                VALUES(?,?,?,?)
            """, (nombre, categoria, precio, stock))

            conn.commit()

    def obtener_productos(self):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id_producto,
                    nombre,
                    categoria,
                    precio,
                    stock
                FROM Producto
                ORDER BY nombre
            """)

            filas = cursor.fetchall()

        productos = []

        for fila in filas:

            productos.append(
                Producto(
                    id_producto=fila[0],
                    nombre=fila[1],
                    categoria=fila[2],
                    precio_unitario=fila[3],
                    stock=fila[4]
                )
            )

        return productos

    def buscar_por_nombre(self, nombre):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id_producto,
                    nombre,
                    categoria,
                    precio,
                    stock
                FROM Producto
                WHERE nombre=?
            """, (nombre,))

            fila = cursor.fetchone()

        if fila is None:
            return None

        return Producto(
            id_producto=fila[0],
            nombre=fila[1],
            categoria=fila[2],
            precio_unitario=fila[3],
            stock=fila[4]
        )

    def buscar_por_id(self, id_producto):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id_producto,
                    nombre,
                    categoria,
                    precio,
                    stock
                FROM Producto
                WHERE id_producto=?
            """, (id_producto,))

            fila = cursor.fetchone()

        if fila is None:
            return None

        return Producto(
            id_producto=fila[0],
            nombre=fila[1],
            categoria=fila[2],
            precio_unitario=fila[3],
            stock=fila[4]
        )

    def actualizar_stock(self, id_producto, nuevo_stock):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Producto
                SET stock=?
                WHERE id_producto=?
            """, (nuevo_stock, id_producto))

            conn.commit()

    def descontar(self, id_producto, cantidad):

        producto = self.buscar_por_id(id_producto)

        if producto is None:
            raise ValueError("Producto no encontrado.")

        if producto.stock < cantidad:
            raise ValueError(
                f"No hay suficiente stock de {producto.nombre}"
            )

        self.actualizar_stock(
            id_producto,
            producto.stock - cantidad
        )

    def devolver(self, id_producto, cantidad):

        producto = self.buscar_por_id(id_producto)

        if producto is None:
            raise ValueError("Producto no encontrado.")

        self.actualizar_stock(
            id_producto,
            producto.stock + cantidad
        )

    def eliminar_producto(self, id_producto):

        with self._conectar() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM Producto
                WHERE id_producto=?
            """, (id_producto,))

            conn.commit()