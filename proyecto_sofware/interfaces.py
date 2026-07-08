
import streamlit as st
from inventario import Inventario
from pedido import Pedido
from producto import Producto
from factura import Factura

if "inventario" not in st.session_state:
    st.session_state.inventario = Inventario()

if "gestor_pedidos" not in st.session_state:
    st.session_state.gestor_pedidos = Pedido(st.session_state.inventario)

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"
if "gestor_factura" not in st.session_state:
    st.session_state.gestor_factura = Factura()

if "pedido_a_facturar" not in st.session_state:
    st.session_state.pedido_a_facturar = None


inventario = st.session_state.inventario
gestor_pedidos = st.session_state.gestor_pedidos
gestor_factura = st.session_state.gestor_factura

def ir_a(pagina: str):
    st.session_state.pagina = pagina

st.set_page_config(page_title="El Refugio", page_icon="🍔", layout="wide")

with st.sidebar:
    st.title("🍔 El Refugio")
    st.button("🏠 Inicio", use_container_width=True, on_click=ir_a, args=("inicio",))
    st.button("➕ Nuevo pedido", use_container_width=True, on_click=ir_a, args=("nuevo",))
    st.button("⏳ Pedidos pendientes", use_container_width=True, on_click=ir_a, args=("pendientes",))
    st.button("📦 Inventario", use_container_width=True, on_click=ir_a, args=("inventario",))
    st.button("📦 Productos", use_container_width=True, on_click=ir_a, args=("Productos",))
    st.button("💵 Ingresos del día", use_container_width=True, on_click=ir_a, args=("ingresos",))
    st.divider()
    st.metric("💵 Ingresos de hoy", f"${gestor_pedidos.obtener_ingresos_hoy():,.0f}")

def pantalla_inicio():
    st.title("👋 Bienvenido al Refugio")
    st.write("Sistema de gestión de pedidos e inventario del local.")
    st.divider()

    st.subheader("¿Qué deseas hacer?")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### ➕ Nuevo pedido")
            st.write("Registra un pedido nuevo y descuenta automáticamente del inventario.")
            st.button("Ir a Nuevo pedido", key="btn_nuevo", on_click=ir_a, args=("nuevo",))

        with st.container(border=True):
            st.markdown("### 📦 Inventario")
            st.write("Consulta el stock actual y reabastece productos.")
            st.button("Ir a Inventario", key="btn_inventario", on_click=ir_a, args=("inventario",))

        with st.container(border=True):
            st.markdown("### 🏷️ Productos y Categorias")
            st.write("Agregar nuevos productos y ctegorias de estos.")
            st.button("Ir a Productos", key="btn_Productos", on_click=ir_a, args=("Productos",))

    with col2:
        with st.container(border=True):
            st.markdown("### ⏳ Pedidos pendientes")
            st.write("Revisa, completa o cancela los pedidos en curso.")
            st.button("Ir a Pendientes", key="btn_pendientes", on_click=ir_a, args=("pendientes",))

        with st.container(border=True):
            st.markdown("### 💵 Ingresos del día")
            st.write("Consulta cuánto se ha acumulado hoy en ventas.")
            st.button("Ir a Ingresos", key="btn_ingresos", on_click=ir_a, args=("ingresos",))


def pantalla_nuevo_pedido():
    st.title("➕ Registrar nuevo pedido")

    if "carrito" not in st.session_state:
        st.session_state.carrito = []

    if "confirmar" not in st.session_state:
        st.session_state.confirmar = False

    nombre = st.text_input("Nombre del cliente")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        productos = inventario.obtener_productos()

        if not productos:
            st.warning("No hay productos registrados.")
            return
        producto = st.selectbox(
                    "Producto",
                    productos,
                    format_func=lambda p:
                    f"{p.nombre} | Stock: {p.stock} | ${p.precio_unitario:,.0f}")

    with col2:
        cantidad = st.number_input(
                               "Cantidad",
                               min_value=1,
                               max_value=producto.stock,
                               value=1
                                      )             

    if st.button("➕ Agregar al pedido"):

        encontrado = False

        for p in st.session_state.carrito:
            if p.id_producto == producto.id_producto:
                p.cantidad += cantidad
                encontrado = True
                break

        if not encontrado:
            st.session_state.carrito.append(
                Producto(
                        id_producto=producto.id_producto,
                        nombre=producto.nombre,
                        categoria=producto.categoria,
                        precio_unitario=producto.precio_unitario,
                        stock=producto.stock,
                        cantidad=cantidad
                        )
            )

        st.rerun()

    st.divider()

    st.subheader("🛒 Pedido actual")

    if len(st.session_state.carrito) == 0:
        st.info("Todavía no hay productos.")
    else:

        total = 0

        for i, prod in enumerate(st.session_state.carrito):

            c1, c2, c3, c4 = st.columns([4,2,2,1])

            with c1:
                st.write(prod.nombre)

            with c2:
                st.write(f"x{prod.cantidad}")

            with c3:
                st.write(f"${prod.subtotal:,.0f}")

            with c4:
                if st.button("❌", key=f"elim{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()

            total += prod.subtotal

        st.divider()

        st.metric("Total", f"${total:,.0f}")

    if st.button("✅ Registrar pedido", type="primary"):

        if not nombre:
            st.error("Ingrese el nombre del cliente.")

        elif len(st.session_state.carrito) == 0:
            st.error("Debe agregar al menos un producto.")

        else:
            st.session_state.confirmar = True

    if st.session_state.confirmar:

        st.warning("### ¿Confirmar pedido?")

        st.write(f"**Cliente:** {nombre}")

        for prod in st.session_state.carrito:
            st.write(f"- {prod.nombre} x{prod.cantidad}")

        total = sum(p.subtotal for p in st.session_state.carrito)

        st.write(f"### Total: ${total:,.0f}")

        col1, col2 = st.columns(2)

        with col1:

            if st.button("✔ Confirmar"):

                try:

                    id_pedido = gestor_pedidos.agregar_pedido(
                        nombre,
                        st.session_state.carrito
                    )

                    st.success(f"Pedido #{id_pedido} registrado correctamente.")

                    st.session_state.carrito = []
                    st.session_state.confirmar = False

                    st.rerun()

                except ValueError as e:
                    st.error(e)

        with col2:

            if st.button("Cancelar"):
                st.session_state.confirmar = False
                st.rerun()

def pantalla_productos():

    st.title("🏷️ Gestión de Productos y Categorías")

    st.subheader("📁 Gestión de Categorías")
    
    col_crear, col_lista = st.columns([1, 1])
    
    with col_crear:
        st.markdown("##### Crear nueva categoría")
        nueva_cat = st.text_input("Nombre de la categoría", key="nueva_cat_input")
        if st.button("Guardar categoría"):
            try:
                inventario.agregar_categoria(nueva_cat)
                st.success(f"Categoría '{nueva_cat}' agregada.")
                st.rerun()
            except ValueError as e:
                st.error(e)
                
    with col_lista:
        st.markdown("##### Categorías existentes")
        categorias_actuales = inventario.obtener_categorias()
        
        for cat in categorias_actuales:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"• {cat}")
            with c2:
                if st.button("🗑", key=f"del_cat_{cat}"):
                    try:
                        inventario.eliminar_categoria(cat)
                        st.success(f"Categoría '{cat}' eliminada.")
                        st.rerun()
                    except ValueError as e:
                        st.error(e)
            
    st.divider()

    st.subheader("Agregar nuevo producto")

    nombre = st.text_input("Nombre")

    categorias_disponibles = inventario.obtener_categorias()

    categoria = st.selectbox(
        "Categoría",
        categorias_disponibles
    )

    precio = st.number_input(
        "Precio",
        min_value=0.0,
        step=1000.0
    )

    stock = st.number_input(
        "Stock inicial",
        min_value=0,
        step=1
    )

    if st.button("Guardar producto"):

        if not nombre.strip():

            st.error("Debe ingresar un nombre.")

        elif not categoria:
            st.error("Debe seleccionar o crear una categoría primero.")

        else:

            try:

                inventario.agregar_producto(
                    nombre,
                    categoria,
                    precio,
                    stock
                )

                st.success("Producto agregado correctamente.")

                st.rerun()

            except Exception as e:

                st.error(e)

    st.divider()

    st.subheader("Productos registrados")

    productos = inventario.obtener_productos()

    if not productos:

        st.info("No hay productos registrados.")

    else:

        for producto in productos:

            col1, col2, col3, col4, col5 = st.columns([3,2,2,2,1])

            with col1:
                st.write(producto.nombre)

            with col2:
                st.write(producto.categoria)

            with col3:
                st.write(f"${producto.precio_unitario:,.0f}")

            with col4:
                st.write(f"Stock: {producto.stock}")

            with col5:

                if st.button(
                    "🗑",
                    key=f"eliminar_{producto.id_producto}"
                ):

                    inventario.eliminar_producto(
                        producto.id_producto
                    )

                    st.rerun()

def pantalla_pendientes():
    st.title("⏳ Pedidos pendientes")

    pendientes = gestor_pedidos.consultar_pendientes()

    if not pendientes:
        st.info("No hay pedidos pendientes 🙌")
        return

    for p in pendientes:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])
            
            with c1:
                detalle = ", ".join(f"{prod.nombre} x{prod.cantidad}" for prod in p["productos"])
                st.write(f"**Pedido #{p['id']}** — {p['nombre']}")
                st.write(f"🧾 {detalle}")
                st.write(f"💰 Total: ${p['total']:,.0f}  |  🕐 {p['fecha']}")
                
            with c2:
                metodo_seleccionado = st.selectbox(
                    "Forma de pago", 
                    ["Físico (Efectivo)", "Transacción"], 
                    key=f"pago_{p['id']}"  
                )
                
                if st.button("✔️ Completar y Pagar", key=f"completar_{p['id']}", use_container_width=True):
                    gestor_pedidos.completar_pedido(p["id"], metodo_seleccionado)
                    
                    p["metodo_pago"] = metodo_seleccionado
                    
                    st.session_state.pedido_a_facturar = p
                    st.rerun()
                    
            with c3:
                st.write("")
                st.write("")
                if st.button("❌ Cancelar", key=f"cancelar_{p['id']}", use_container_width=True):
                    gestor_pedidos.eliminar_pedido(p["id"], devolver_stock=True)
                    st.rerun()


def pantalla_inventario():
    st.title("📦 Inventario")

    productos = inventario.obtener_productos()

    for producto in productos:

        st.write(
        f"**{producto.nombre}** | "
        f"Categoría: {producto.categoria} | "
        f"Stock: {producto.stock} | "
        f"${producto.precio_unitario:,.0f}"
                 )

    st.divider()
    st.subheader("Reabastecer producto")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        producto_reabastecer = st.selectbox(
                "Producto",
                productos,
                format_func=lambda p: p.nombre
        )
    with col2:
        cantidad_reabastecer = st.number_input("Cantidad a agregar", min_value=1, step=1)
    with col3:
        st.write("")
        st.write("")
        if st.button("📥 Agregar stock"):
            inventario.actualizar_stock(producto_reabastecer.id_producto, producto_reabastecer.stock + cantidad_reabastecer)
            st.success(f"Se agregaron {cantidad_reabastecer} unidades de {producto_reabastecer}")
            st.rerun()


def pantalla_ingresos():
    st.title("💵 Ingresos del día")

    total_hoy = gestor_pedidos.obtener_ingresos_hoy()
    st.metric("Total acumulado hoy", f"${total_hoy:,.0f}")

    movimientos = gestor_pedidos.obtener_movimientos_hoy()

    if not movimientos:
        st.info("Todavía no hay pedidos completados o eliminados hoy.")
    else:
        st.dataframe(
            [
                {
                    "ID movimiento": m["id"],
                    "ID pedido": m["id_pedido"],
                    "Monto": m["monto"],
                    "Origen": m["origen"],
                    "Fecha": m["fecha"],
                }
                for m in movimientos
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Los ingresos se acumulan cuando un pedido se marca como **completado** "
        "o se **elimina como despachado** (no aplica a cancelaciones con devolución de stock). "
        "Solo se muestran los movimientos del día actual según el reloj del sistema."
    )

@st.dialog("Validación de Factura - El Refugio", width="large")
def mostrar_interfaz_facturacion():
    if st.session_state.pedido_a_facturar is None:
        return
        
    pedido = st.session_state.pedido_a_facturar
    
    st.write(f"### Comprobar Datos de Facturación")
    st.write(f"**Pedido ID:** #{pedido['id']} | **Cliente:** {pedido['nombre']}")
    st.write(f"**Método de Pago Seleccionado:** {pedido['metodo_pago']}")
    st.divider()

    st.write("**Desglose de Ítems:**")
    for prod in pedido["productos"]:
        st.write(f"- {prod.nombre} × {prod.cantidad} (${prod.precio_unitario:,.0f} c/u) → **Subtotal: ${prod.subtotal:,.0f}**")
    st.divider()
    
    total_real = sum(p.subtotal for p in pedido["productos"])

    st.metric("TOTAL A COBRAR", f"${total_real:,.0f}")
    st.divider()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Confirmar y Emitir Factura", type="primary", use_container_width=True):
            factura_emitida = gestor_factura.generar_factura(
                pedido_dict=pedido,
                metodo_pago=pedido["metodo_pago"]
            )
            st.success(f"🎉 ¡Factura {factura_emitida['nro_factura']} guardada con éxito!")
            st.session_state.pedido_a_facturar = None  
            st.button("Terminar y Actualizar Vista", on_click=st.rerun)
            
    with col_btn2:
        if st.button("Omitir / Cancelar Factura", use_container_width=True):
            st.session_state.pedido_a_facturar = None
            st.rerun()

PANTALLAS = {
    "inicio": pantalla_inicio,
    "nuevo": pantalla_nuevo_pedido,
    "pendientes": pantalla_pendientes,
    "Productos": pantalla_productos,
    "inventario": pantalla_inventario,
    "ingresos": pantalla_ingresos,
}

if st.session_state.pedido_a_facturar is not None:
    mostrar_interfaz_facturacion()

PANTALLAS[st.session_state.pagina]()