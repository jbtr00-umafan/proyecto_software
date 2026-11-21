# Sistema POS y Gestión Administrativa — Café-Bar El Refugio

🌐 **Aplicación desplegada en vivo:** [Abrir Demo en Streamlit](https://proyectosoftware-cbdukhrsxh9xptztdgzljh.streamlit.app/)

Sistema de Punto de Venta (POS) y control operativo desarrollado en **Python**, **Streamlit** y **SQLite** para el café-bar *El Refugio* (Urrao, Antioquia). El proyecto digitaliza la operación diaria del negocio, reemplazando el registro manual en cuadernos y eliminando los descuadres de caja, las faltas de stock imprevistas y la ausencia de trazabilidad en pedidos y créditos.

---

## Módulos del Sistema

De acuerdo con la interfaz principal de la aplicación, el sistema se organiza en los siguientes módulos operativos:

* **Inicio (Panel Principal):** Accesos directos a las operaciones críticas del turno y visualización en tiempo real del acumulado de **Ingresos de hoy**.
* **+ Nuevo Pedido:** Registro ágil de órdenes asociando cliente, productos disponibles en stock y cálculo automático del total a cobrar.
* **Pedidos Pendientes:** Seguimiento de órdenes en curso con soporte para confirmación de pago (**Efectivo** o **Transferencia**), cancelación con devolución de stock y emisión/validación de factura con consecutivo (`FAC-...`).
* **Inventario:** Consulta de existencias por categoría y módulo de **Reabastecimiento** para actualizar cantidades y precios de venta tras la llegada de proveedores.
* **Productos:** Administración CRUD completa de artículos y gestión de **Categorías** (*Bebidas*, *Entradas*, *Adiciones*, etc.).
* **Ingresos del Día:** Consolidación automática de ventas completadas y despachadas con fecha, hora y origen del movimiento para facilitar el cuadre y relevo de turnos.
* **Libreta de Deudas («Fiados»):** Registro y consulta de clientes frecuentes con control de saldo pendiente, abonos y validación automática de tope máximo de crédito ($200.000 COP).

---

## Stack Técnico

* **Lenguaje:** Python 3
* **Framework Web / Interfaz:** Streamlit
* **Base de Datos:** SQLite (`sqlite3`)
* **Metodología y Modelado:** Scrum (Product Backlog, Historias de Usuario), BPMN y Diagramas UML (Casos de Uso, Clases y Dominio).

---

## Instalación y Ejecución Local

1. Clona el repositorio e ingresa a la carpeta del proyecto:
   ```bash
   git clone [https://github.com/quits666/SistemaPOS-ELRefugio.git](https://github.com/quits666/SistemaPOS-ELRefugio.git)
   cd SistemaPOS-ELRefugio
