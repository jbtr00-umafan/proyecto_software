import sqlite3
import json
from datetime import datetime

class Factura:
    DB_NAME = "pedidos.db"

    def __init__(self, db_name: str = None):
        if db_name:
            self.DB_NAME = db_name
        self._crear_tabla()

    def _conectar(self):
        return sqlite3.connect(self.DB_NAME)

    def _crear_tabla(self):
        """Crea la tabla Factura si no existe en la BD compartida."""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Factura (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pedido INTEGER NOT NULL UNIQUE,
                    nro_factura TEXT NOT NULL UNIQUE,
                    nombre_cliente TEXT NOT NULL,
                    productos_json TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    impuesto REAL NOT NULL,
                    total REAL NOT NULL,
                    metodo_pago TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    FOREIGN KEY (id_pedido) REFERENCES Pedido (id)
                )
            """)
            conn.commit()

    def generar_factura(self, pedido_dict: dict, metodo_pago: str) -> dict:
        """
        Calcula el monto neto real y registra la factura sin impuestos.
        """
        id_pedido = pedido_dict["id"]
        nombre_cliente = pedido_dict["nombre"]
        productos = pedido_dict["productos"]
        
        total_real = sum(p.subtotal for p in productos)
        impuesto = 0.0  
        
        ahora = datetime.now()
        nro_factura = f"FAC-{ahora.strftime('%Y%m%d')}-{id_pedido:04d}"
        fecha_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
        
        productos_json = json.dumps([
            {"nombre": p.nombre, "cantidad": p.cantidad, "precio_unitario": p.precio_unitario, "subtotal": p.subtotal}
            for p in productos
        ])

        with self._conectar() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Factura (id_pedido, nro_factura, nombre_cliente, productos_json, subtotal, impuesto, total, metodo_pago, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (id_pedido, nro_factura, nombre_cliente, productos_json, total_real, impuesto, total_real, metodo_pago, fecha_str))
                conn.commit()
                id_factura = cursor.lastrowid
            except sqlite3.IntegrityError:
                cursor.execute("SELECT id, nro_factura, total FROM Factura WHERE id_pedido = ?", (id_pedido,))
                fila = cursor.fetchone()
                return {
                    "id_factura": fila[0], "nro_factura": fila[1], "nombre_cliente": nombre_cliente,
                    "total": fila[2], "fecha": fecha_str
                }

        return {
            "id_factura": id_factura,
            "nro_factura": nro_factura,
            "nombre_cliente": nombre_cliente,
            "total": total_real,
            "fecha": fecha_str
        }