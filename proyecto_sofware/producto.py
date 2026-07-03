class Producto:

    def __init__(
        self,
        id_producto=None,
        nombre="",
        categoria="",
        precio_unitario=0,
        stock=0,
        cantidad=0
    ):

        self.id_producto = id_producto
        self.nombre = nombre
        self.categoria = categoria
        self.precio_unitario = precio_unitario
        self.stock = stock
        self.cantidad = cantidad

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def to_dict(self):

        return {

            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio_unitario": self.precio_unitario,
            "stock": self.stock,
            "cantidad": self.cantidad
        }

    @staticmethod
    def from_dict(data):

        return Producto(

            id_producto=data["id_producto"],
            nombre=data["nombre"],
            categoria=data["categoria"],
            precio_unitario=data["precio_unitario"],
            stock=data["stock"],
            cantidad=data["cantidad"]
        )