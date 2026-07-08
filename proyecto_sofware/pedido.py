import json
import sqlite3
from datetime import datetime

from inventario import Inventario
from producto import Producto


class Pedido:

    DB_NAME = "pedidos.db"

    def __init__(self, inventario: Inventario, db_name: str = None):
        self.inventario = inventario
        if db_name:
            self.DB_NAME = db_name
        self._crear_tablas()

    def _conectar(self):
        return sqlite3.connect(self.DB_NAME)

    def _crear_tablas(self):
        """Crea las tablas 'Pedido' e 'Ingresos' si no existen."""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Pedido (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    productos TEXT NOT NULL,
                    total REAL NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    metodo_pago TEXT,          -- <-- Aquí se guardará al completarse
                    fecha TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ingresos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pedido INTEGER,
                    monto REAL NOT NULL,
                    origen TEXT NOT NULL,   -- 'completado' o 'eliminado'
                    fecha TEXT NOT NULL     -- fecha/hora del movimiento (reloj del sistema)
                )
            """)
            conn.commit()

    @staticmethod
    def _productos_a_json(productos: list) -> str:
        return json.dumps([p.to_dict() for p in productos])

    @staticmethod
    def _json_a_productos(texto: str) -> list:
        data = json.loads(texto) if texto else []
        return [Producto.from_dict(item) for item in data]

    @staticmethod
    def _productos_a_dict_cantidades(productos: list) -> dict:
        """Convierte lista de Producto a {nombre: cantidad}, útil para el Inventario."""
        return {p.nombre: p.cantidad for p in productos}

    def agregar_pedido(self, nombre: str, productos: list) -> int:
        """
        Registra un nuevo pedido:
        1. Descuenta del inventario según las cantidades de cada Producto.
        2. Calcula el total sumando el subtotal de cada Producto.
        3. Guarda el pedido en SQLite con estado 'pendiente'.

        nombre     -> nombre del cliente (str)
        productos  -> lista de objetos Producto

        Retorna el id (numérico único) del pedido generado.
        """

        for producto in productos:
            self.inventario.descontar(
                          producto.id_producto,
                          producto.cantidad
                                            )


        total = sum(p.subtotal for p in productos)

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        productos_json = self._productos_a_json(productos)

        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Pedido (nombre, productos, total, estado, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, productos_json, total, "pendiente", fecha))
            conn.commit()
            id_pedido = cursor.lastrowid

        print(f"✅ Pedido #{id_pedido} registrado para '{nombre}' - Total: ${total:,.0f}")
        return id_pedido

    def consultar_pendientes(self) -> list:
        """Retorna una lista de dicts (id, nombre, productos, total, estado, fecha) en estado 'pendiente'."""
        return self._consultar(where="estado = 'pendiente'")

    def consultar_todos(self) -> list:
        """Retorna todos los pedidos (pendientes y completados)."""
        return self._consultar()

    def _consultar(self, where: str = "") -> list:
        query = "SELECT id, nombre, productos, total, estado, fecha FROM Pedido"
        if where:
            query += f" WHERE {where}"
        query += " ORDER BY fecha ASC"

        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            filas = cursor.fetchall()

        return [
            {
                "id": f[0],
                "nombre": f[1],
                "productos": self._json_a_productos(f[2]),
                "total": f[3],
                "estado": f[4],
                "fecha": f[5],
            }
            for f in filas
        ]

    def _registrar_ingreso(self, id_pedido: int, monto: float, origen: str):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Ingresos (id_pedido, monto, origen, fecha)
                VALUES (?, ?, ?, ?)
            """, (id_pedido, monto, origen, fecha))
            conn.commit()


    def completar_pedido(self, id_pedido: int, metodo_pago: str) -> bool:
        """Marca un pedido como completado, registra el método de pago y acumula el ingreso."""
        
        # 1. Primero buscamos si el pedido existe para saber el total del dinero
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT total, estado FROM Pedido WHERE id = ?", (id_pedido,))
            fila = cursor.fetchone()

        if not fila:
            print(f"❌ Pedido #{id_pedido} no encontrado.")
            return False

        total, estado_actual = fila

        if estado_actual != 'pendiente':
            print(f"⚠️ El pedido #{id_pedido} ya no está pendiente (Estado: {estado_actual}).")
            return False

        # 2. Si todo está bien, abrimos una nueva conexión para actualizar los datos
        hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # COMANDO SQL UPDATE: Modificamos el estado y el metodo_pago DEL pedido con el id indicado
            cursor.execute("""
                UPDATE Pedido
                SET estado = 'completado',
                    metodo_pago = ?
                WHERE id = ?
            """, (metodo_pago, id_pedido))   # Pasamos las variables en orden para los '?'
            
            # También lo registramos en la tabla de Ingresos del día
            cursor.execute("""
                INSERT INTO Ingresos (id_pedido, monto, origen, fecha)
                VALUES (?, ?, 'completado', ?)
            """, (id_pedido, total, hoy))
            
            # ¡CRUCIAL! Confirmamos que se guarden ambos cambios en el archivo físico pedidos.db
            conn.commit()

        print(f"✅ Pedido #{id_pedido} pagado con [{metodo_pago}]. Ingreso acumulado: ${total:,.0f}")
        return True

    def eliminar_pedido(self, id_pedido: int, devolver_stock: bool = False) -> bool:
        """
        Borra el pedido de la base de datos, acumulando igualmente su total
        en los ingresos.
        """
        import json # Aseguramos que json esté disponible
        
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT productos, total FROM Pedido WHERE id = ?", (id_pedido,))
            fila = cursor.fetchone()

            if not fila:
                print(f"⚠️ Pedido #{id_pedido} no encontrado.")
                return False

            productos_json, total = fila

            if devolver_stock:
                # 1. Convertimos el texto JSON de vuelta a una lista de diccionarios
                lista_dicts = json.loads(productos_json)
                
                # 2. Reconstruimos los objetos Producto mapeando sus datos
                productos = [
                    Producto(
                        id_producto=d["id_producto"],
                        nombre=d["nombre"],
                        categoria=d["categoria"],
                        precio_unitario=d["precio_unitario"],
                        stock=d["stock"],
                        cantidad=d["cantidad"]
                    ) for d in lista_dicts
                ]
                
                # 3. Ahora sí, el ciclo for funcionará sin fallas porque 'productos' ya existe
                for prod in productos:
                    self.inventario.devolver(prod.id_producto, prod.cantidad)
                
            cursor.execute("DELETE FROM Pedido WHERE id = ?", (id_pedido,))
            conn.commit()

        if not devolver_stock:
            self._registrar_ingreso(id_pedido, total, "eliminado")
            print(f"🗑️ Pedido #{id_pedido} eliminado. Ingreso acumulado: ${total:,.0f}")
        else:
            print(f"🗑️ Pedido #{id_pedido} cancelado y eliminado (stock devuelto, no cuenta como ingreso).")

        return True


    def obtener_ingresos_hoy(self) -> float:
        """
        Suma los montos de la tabla Ingresos (completados + eliminados)
        cuya fecha corresponde al día actual del computador.
        """
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM Ingresos
                WHERE date(fecha) = ?
            """, (hoy,))
            resultado = cursor.fetchone()[0]
        return float(resultado)

    def obtener_movimientos_hoy(self) -> list:
        """Detalle de los movimientos de ingreso (completados/eliminados) del día actual."""
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, id_pedido, monto, origen, fecha
                FROM Ingresos
                WHERE date(fecha) = ?
                ORDER BY fecha ASC
            """, (hoy,))
            filas = cursor.fetchall()

        return [
            {"id": f[0], "id_pedido": f[1], "monto": f[2], "origen": f[3], "fecha": f[4]}
            for f in filas
        ]