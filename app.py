import os
import sqlite3
import urllib.parse
from datetime import datetime
import pandas as pd
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

      ticket_path = "ticket_generado.png"
      ticket_img.save(ticket_path)

      st.session_state["ticket_generado"] = ticket_path
      st.session_state["telefono_cliente"] = telefono
      st.session_state["total_venta"] = total
      st.session_state["folio_venta"] = folio_nota

      st.success("¡Venta registrada y ticket generado con éxito!")

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
  st.title("📊 Historial de Ventas y Corte de Caja")

  try:
    conn = sqlite3.connect(DB_NAME)
    df_ventas = pd.read_sql_query(
        "SELECT * FROM ventas ORDER BY id DESC", conn
    )
    conn.close()

    if not df_ventas.empty:
      # --- CORTE DE CAJA DIARIO ---
      st.subheader("💵 Corte de Caja Diario (Hoy)")
      # Extraer fecha actual en formato YYYY-MM-DD
      hoy_str = datetime.now().strftime("%Y-%m-%d")

      # Filtrar ventas que coincidan con la fecha de hoy
      df_ventas["solo_fecha"] = df_ventas["fecha"].astype(str).str.slice(0, 10)
      df_hoy = df_ventas[df_ventas["solo_fecha"] == hoy_str]

      if not df_hoy.empty:
        total_hoy = df_hoy["total"].sum()
        efectivo_hoy = df_hoy[df_hoy["metodo_pago"] == "Efectivo"][
            "total"
        ].sum()
        tarjeta_hoy = df_hoy[df_hoy["metodo_pago"] == "Tarjeta"]["total"].sum()
        trans_hoy = df_hoy[df_hoy["metodo_pago"] == "Transferencia"][
            "total"
        ].sum()

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.metric("Total Hoy", f"${total_hoy:,.2f}")
        col_c2.metric("Efectivo", f"${efectivo_hoy:,.2f}")
        col_c3.metric("Tarjeta", f"${tarjeta_hoy:,.2f}")
        col_c4.metric("Transferencia", f"${trans_hoy:,.2f}")
      else:
        st.info("No hay ventas registradas el día de hoy todavía.")

      st.markdown("---")

      # --- BARRA DE BÚSQUEDA ---
      busqueda = st.text_input(
          "🔍 Buscar por Cliente o Folio de Nota",
          placeholder="Escribe el nombre o número...",
      )

      if busqueda:
        # Filtrar el dataframe donde el cliente o el folio contengan el texto buscado
        df_filtrado = df_ventas[
            df_ventas["cliente"].str.contains(busqueda, case=False, na=False)
            | df_ventas["folio_nota"].str.contains(
                busqueda, case=False, na=False
            )
        ]
      else:
        df_filtrado = df_ventas

      # --- BOTÓN EXCEL (CSV) ---
      csv_data = df_ventas.drop(columns=["solo_fecha"]).to_csv(
          index=False
      )  # Quitamos la columna temporal
      st.download_button(
          label="📥 Descargar Todo el Historial en Excel (CSV)",
          data=csv_data.encode("utf-8"),
          file_name=f"Historial_Ventas_{datetime.now().strftime('%Y-%m-%d')}.csv",
          mime="text/csv",
      )

      st.markdown("---")
      st.write(f"Mostrando {len(df_filtrado)} registro(s):")

      # --- MOSTRAR LISTADO E ITERAR PARA REIMPRESIÓN ---
      for index, row in df_filtrado.iterrows():
        with st.expander(
            f"Folio: {row['folio_nota']} | Cliente: {row['cliente']} | Total:"
            f" ${row['total']:.2f} ({row['fecha']})"
        ):
          st.write(f"**Fecha y Hora:** {row['fecha']}")
          st.write(f"**Núm. Servicio:** {row['num_servicio']}")
          st.write(f"**Teléfono:** {row['telefono']}")
          st.write(f"**Tipo de Gas:** {row['tipo_gas']}")
          st.write(
              f"**Cantidad:** {row['litros']} Litros/Kilos (Precio unitario:"
              f" ${row['precio_litro']:.2f})"
          )
          st.write(f"**Método de Pago:** {row['metodo_pago']}")
          st.write(f"**Usuario que registró:** {row['usuario']}")

          st.markdown("---")
          st.markdown("**Acciones de Ticket:**")

          # Botón único para reimprimir el ticket de este registro específico
          if st.button(
              f"🖨️ Generar Imagen de Ticket (Folio {row['folio_nota']})",
              key=f"reprint_{row['id']}",
          ):
            # Generar la imagen idéntica al ticket original
            img_w, img_h = 600, 850
            t_img = Image.new("RGB", (img_w, img_h), "white")
            d_draw = ImageDraw.Draw(t_img)

            try:
              f_path = "arial.ttf"
              ft_title = ImageFont.truetype(f_path, 26)
              ft_bold = ImageFont.truetype(f_path, 18)
              ft_reg = ImageFont.truetype(f_path, 16)
            except:
              ft_title = ImageFont.load_default()
              ft_bold = ImageFont.load_default()
              ft_reg = ImageFont.load_default()

            try:
              logo_img = Image.open("logo.jpg")
              logo_img = logo_img.resize((100, 100))
              t_img.paste(logo_img, (250, 20))
              y_off = 130
            except:
              y_off = 30

            d_draw.text(
                (img_w / 2, y_off),
                "NAUPAGAS",
                fill="black",
                anchor="mm",
                font=ft_title,
            )
            y_off += 35
            d_draw.text(
                (img_w / 2, y_off),
                "REIMPRESIÓN DE TICKET",
                fill="gray",
                anchor="mm",
                font=ft_bold,
            )
            y_off += 30

            sep = "-" * 50
            d_draw.text((30, y_off), sep, fill="black", font=ft_bold)
            y_off += 25

            reimp_datos = [
                f"Fecha: {row['fecha']}",
                f"Folio Nota: {row['folio_nota']}",
                f"Núm. Servicio: {row['num_servicio']}",
                f"Cliente: {row['cliente']}",
                f"Teléfono: {row['telefono']}",
                f"Tipo de Gas: {row['tipo_gas']}",
                f"Cantidad: {row['litros']:.2f} Litros/Kilos",
                f"Precio x Litro: ${row['precio_litro']:.2f}",
                f"Método de Pago: {row['metodo_pago']}",
            ]

            for d_dato in reimp_datos:
              d_draw.text((30, y_off), d_dato, fill="black", font=ft_reg)
              y_off += 25

            d_draw.text((30, y_off), sep, fill="black", font=ft_bold)
            y_off += 30

            d_draw.text(
                (30, y_off),
                f"TOTAL A PAGAR: ${row['total']:.2f}",
                fill="black",
                font=ft_title,
            )
            y_off += 50

            d_draw.text(
                (img_w / 2, y_off),
                "¡Gracias por su preferencia!",
                fill="gray",
                anchor="mm",
                font=ft_bold,
            )

            path_reimp = f"ticket_reimp_{row['folio_nota']}.png"
            t_img.save(path_reimp)

            st.success(f"¡Ticket del Folio {row['folio_nota']} generado!")
            st.image(path_reimp, use_container_width=True)

            with open(path_reimp, "rb") as f_down:
              st.download_button(
                  label=f"📥 Descargar Ticket Folio {row['folio_nota']}",
                  data=f_down,
                  file_name=f"Ticket_{row['folio_nota']}.png",
                  mime="image/png",
                  key=f"down_{row['id']}",
              )
    else:
      st.info("Aún no hay ventas registradas en el sistema.")
  except Exception as e:
    st.info("Aún no hay registros en la base de datos.")
