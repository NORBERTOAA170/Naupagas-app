import os
import sqlite3
import urllib.parse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="NAUPAGAS - Sistema de Ventas", page_icon="⛽", layout="centered"
)

# Base de datos local
DB_NAME = "gasera_historial.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  # Creamos la tabla con la estructura limpia
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_nota TEXT,
            num_servicio TEXT,
            fecha TEXT,
            cliente TEXT,
            telefono TEXT,
            tipo_gas TEXT,
            litros REAL,
            precio_litro REAL,
            total REAL,
            metodo_pago TEXT,
            usuario TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

# Control de Sesión (Login simple)
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  st.title("⛽ NAUPAGAS - Iniciar Sesión")
  usuario_input = st.text_input("Usuario")
  password_input = st.text_input("Contraseña", type="password")

  if st.button("Entrar", type="primary"):
    if usuario_input == "NAUPA" and password_input == "NAUPAGAS2026":
      st.session_state.logged_in = True
      st.rerun()
    else:
      st.error("Usuario o contraseña incorrectos")
  st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("Menú Principal")
menu = st.sidebar.radio("Ir a:", ["Nueva Venta", "Historial de Ventas"])

if st.sidebar.button("Cerrar Sesión"):
  st.session_state.logged_in = False
  st.rerun()

# --- OPCIÓN 1: NUEVA VENTA ---
if menu == "Nueva Venta":
  st.title("⛽ NAUPAGAS - Registro de Venta")

  with st.form("form_venta"):
    st.subheader("Datos del Servicio")

    folio_nota = st.text_input(
        "Folio de Nota (Solo números)",
        placeholder="Ej. 1024",
        help="Escribe únicamente dígitos",
    )
    num_servicio = st.text_input(
        "Número de Servicio / Orden (Solo números)",
        placeholder="Ej. 5842",
        help="Escribe únicamente dígitos",
    )

    st.subheader("Datos del Cliente")
    cliente = st.text_input("Nombre del Cliente", placeholder="Juan Pérez")
    telefono = st.text_input(
        "Teléfono a 10 dígitos (Sin espacios ni guiones)",
        max_chars=10,
        placeholder="5512345678",
    )

    st.subheader("Detalles del Gas")
    tipo_gas = st.selectbox(
        "Tipo de Gas", ["Gas Estacionario", "Cilindro Portátil"]
    )
    litros = st.number_input(
        "Litros / Kilos Suministrados", min_value=0.1, format="%.2f"
    )
    precio_litro = st.number_input(
        "Precio por Litro ($)", min_value=0.1, value=10.50, format="%.2f"
    )

    metodo_pago = st.selectbox(
        "Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"]
    )

    submitted = st.form_submit_button("Generar Ticket y Registrar Venta")

  if submitted:
    # Validaciones estrictas antes de procesar
    errores = []
    if not folio_nota.isdigit():
      errores.append("El Folio de Nota debe contener únicamente números.")
    if not num_servicio.isdigit():
      errores.append("El Número de Servicio debe contener únicamente números.")
    if not telefono.isdigit() or len(telefono) != 10:
      errores.append(
          "El teléfono debe ser un número válido de exactamente 10 dígitos."
      )
    if not cliente.strip():
      errores.append("El nombre del cliente no puede estar vacío.")

    if errores:
      for err in errores:
        st.error(err)
    else:
      total = litros * precio_litro
      fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      try:
        # Guardar en base de datos de forma segura
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
                    INSERT INTO ventas (folio_nota, num_servicio, fecha, cliente, telefono, tipo_gas, litros, precio_litro, total, metodo_pago, usuario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                folio_nota,
                num_servicio,
                fecha_actual,
                cliente,
                telefono,
                tipo_gas,
                litros,
                precio_litro,
                total,
                metodo_pago,
                "NAUPA",
            ),
        )
        conn.commit()
        conn.close()
      except Exception as e:
        # Si por algo la tabla vieja sigue causando conflicto, la recreamos limpiamente
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS ventas")
        cursor.execute("""
                    CREATE TABLE ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        folio_nota TEXT,
                        num_servicio TEXT,
                        fecha TEXT,
                        cliente TEXT,
                        telefono TEXT,
                        tipo_gas TEXT,
                        litros REAL,
                        precio_litro REAL,
                        total REAL,
                        metodo_pago TEXT,
                        usuario TEXT
                    )
                """)
        cursor.execute(
            """
                    INSERT INTO ventas (folio_nota, num_servicio, fecha, cliente, telefono, tipo_gas, litros, precio_litro, total, metodo_pago, usuario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                folio_nota,
                num_servicio,
                fecha_actual,
                cliente,
                telefono,
                tipo_gas,
                litros,
                precio_litro,
                total,
                metodo_pago,
                "NAUPA",
            ),
        )
        conn.commit()
        conn.close()

      # Crear Imagen del Ticket
      img_width, img_height = 600, 850
      ticket_img = Image.new("RGB", (img_width, img_height), "white")
      draw = ImageDraw.Draw(ticket_img)

      try:
        font_path = "arial.ttf"
        font_title = ImageFont.truetype(font_path, 26)
        font_bold = ImageFont.truetype(font_path, 18)
        font_regular = ImageFont.truetype(font_path, 16)
      except:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_regular = ImageFont.load_default()

      # Intentar poner logo si existe
      try:
        logo = Image.open("logo.jpg")
        logo = logo.resize((100, 100))
        ticket_img.paste(logo, (250, 20))
        y_offset = 130
      except:
        y_offset = 30

      draw.text(
          (img_width / 2, y_offset),
          "NAUPAGAS",
          fill="black",
          anchor="mm",
          font=font_title,
      )
      y_offset += 35
      draw.text(
          (img_width / 2, y_offset),
          "COMPROBANTE DE VENTA",
          fill="gray",
          anchor="mm",
          font=font_bold,
      )
      y_offset += 30

      linea_separadora = "-" * 50
      draw.text((30, y_offset), linea_separadora, fill="black", font=font_bold)
      y_offset += 25

      datos_ticket = [
          f"Fecha: {fecha_actual}",
          f"Folio Nota: {folio_nota}",
          f"Núm. Servicio: {num_servicio}",
          f"Cliente: {cliente}",
          f"Teléfono: {telefono}",
          f"Tipo de Gas: {tipo_gas}",
          f"Cantidad: {litros:.2f} Litros/Kilos",
          f"Precio x Litro: ${precio_litro:.2f}",
          f"Método de Pago: {metodo_pago}",
      ]

      for dato in datos_ticket:
        draw.text((30, y_offset), dato, fill="black", font=font_regular)
        y_offset += 25

      draw.text((30, y_offset), linea_separadora, fill="black", font=font_bold)
      y_offset += 30

      draw.text(
          (30, y_offset),
          f"TOTAL A PAGAR: ${total:.2f}",
          fill="black",
          font=font_title,
      )
      y_offset += 50

      draw.text(
          (img_width / 2, y_offset),
          "¡Gracias por su preferencia!",
          fill="gray",
          anchor="mm",
          font=font_bold,
      )

      # Guardar archivo temporal para descarga
      ticket_path = "ticket_generado.png"
      ticket_img.save(ticket_path)

      # Guardar en Session State para que no desaparezca al interactuar
      st.session_state["ticket_generado"] = ticket_path
      st.session_state["telefono_cliente"] = telefono
      st.session_state["total_venta"] = total
      st.session_state["folio_venta"] = folio_nota

      st.success("¡Venta registrada y ticket generado con éxito!")

  # Mostrar opciones de ticket generado si existe en memoria
  if "ticket_generado" in st.session_state:
    st.image(
        st.session_state["ticket_generado"],
        caption="Vista previa del Ticket",
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
      with open(st.session_state["ticket_generado"], "rb") as file:
        st.download_button(
            label="📥 Descargar Ticket",
            data=file,
            file_name=f"Ticket_{st.session_state['folio_venta']}.png",
            mime="image/png",
        )

    with col2:
      mensaje_wa = (
          f"Hola {cliente}, le enviamos su comprobante de venta de NAUPAGAS."
          f" Folio: {st.session_state['folio_venta']}, Total: $"
          f"{st.session_state['total_venta']:.2f}. ¡Gracias por su compra!"
      )
      mensaje_codificado = urllib.parse.quote(mensaje_wa)
      link_whatsapp = (
          f"https://wa.me/52{st.session_state['telefono_cliente']}?text={mensaje_codificado}"
      )

      st.link_button(
          "💬 Enviar por WhatsApp", link_whatsapp, use_container_width=True
      )

# --- OPCIÓN 2: HISTORIAL DE VENTAS ---
elif menu == "Historial de Ventas":
  st.title("📊 Historial de Ventas Registradas")

  try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT folio_nota, num_servicio, fecha, cliente, telefono, tipo_gas,"
        " total, metodo_pago FROM ventas ORDER BY id DESC"
    )
    registros = cursor.fetchall()
    conn.close()

    if registros:
      for reg in registros:
        with st.expander(
            f"Folio: {reg[0]} | Cliente: {reg[3]} | Total: ${reg[6]:.2f}"
        ):
          st.write(f"**Fecha:** {reg[2]}")
          st.write(f"**Núm. Servicio:** {reg[1]}")
          st.write(f"**Teléfono:** {reg[4]}")
          st.write(f"**Tipo de Gas:** {reg[5]}")
          st.write(f"**Método de Pago:** {reg[7]}")
    else:
      st.info("Aún no hay ventas registradas en el sistema.")
  except:
    st.info("Aún no hay registros en la base de datos.")
