from datetime import datetime
import os
import sqlite3
import urllib.parse
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="NAUPAGAS - Sistema de Ventas", page_icon="logo.jpg", layout="centered"
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

# Control de Sesión (Login simple con Logo)
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
  with col_l2:
    try:
      st.image("logo.jpg", width=150)
    except:
      st.write("⛽")

  st.markdown(
      "<h2 style='text-align: center;'>NAUPAGAS</h2>", unsafe_allow_html=True
  )
  st.markdown(
      "<p style='text-align: center; color: gray;'>Sistema de Control de"
      " Ventas</p>",
      unsafe_allow_html=True,
  )

  usuario_input = st.text_input("Usuario")
  password_input = st.text_input("Contraseña", type="password")

  if st.button("Entrar", type="primary", use_container_width=True):
    if usuario_input == "NAUPA" and password_input == "NAUPA2026":
      st.session_state.logged_in = True
      st.rerun()
    else:
      st.error("Usuario o contraseña incorrectos")
  st.stop()

# --- MENÚ LATERAL CON LOGO ---
st.sidebar.image("logo.jpg", use_container_width=True)
st.sidebar.title("NAUPAGAS")
menu = st.sidebar.radio("Ir a:", ["Nueva Venta", "Historial de Ventas"])

st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
  st.session_state.logged_in = False
  st.rerun()

# --- OPCIÓN 1: NUEVA VENTA (CON MODO OFFLINE) ---
if menu == "Nueva Venta":
  col_t1, col_t2 = st.columns([1, 4])
  with col_t1:
    try:
      st.image("logo.jpg", width=60)
    except:
      pass
  with col_t2:
    st.title("Registro de Venta")

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

      # Modo Offline / Respaldo de seguridad ante fallas de red
      try:
        conn = sqlite3.connect(DB_NAME, timeout=10)
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
        st.success(
            "¡Venta registrada exitosamente en la base de datos y lista para"
            " la calle!"
        )
      except Exception as e:
        try:
          fallback_db = "respaldo_emergencia_ventas.db"
          conn_fb = sqlite3.connect(fallback_db)
          cursor_fb = conn_fb.cursor()
          cursor_fb.execute("""
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
          cursor_fb.execute(
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
          conn_fb.commit()
          conn_fb.close()
          st.warning(
              "⚠️ Sin conexión estable con la nube, pero la venta se guardó"
              " de forma segura en el **Modo Offline Local** de respaldo."
          )
        except Exception as err_fb:
          st.error(f"Error crítico al guardar la venta: {err_fb}")

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

# --- OPCIÓN 2: HISTORIAL DE VENTAS Y FILTRO POR FECHAS ---
elif menu == "Historial de Ventas":
  col_th1, col_th2 = st.columns([1, 4])
  with col_th1:
    try:
      st.image("logo.jpg", width=60)
    except:
      pass
  with col_th2:
    st.title("Historial y Corte de Caja")

  try:
    conn = sqlite3.connect(DB_NAME)
    df_ventas = pd.read_sql_query(
        "SELECT * FROM ventas ORDER BY id DESC", conn
    )
    conn.close()

    if not df_ventas.empty:
      df_ventas["solo_fecha"] = df_ventas["fecha"].astype(str).str.slice(0, 10)

      # --- FILTRO POR RANGO DE FECHAS ---
      st.subheader("📅 Filtrar Historial por Rango de Fechas")
      min_fecha = datetime.strptime(
          df_ventas["solo_fecha"].min(), "%Y-%m-%d"
      ).date()
      max_fecha = datetime.strptime(
          df_ventas["solo_fecha"].max(), "%Y-%m-%d"
      ).date()

      col_f1, col_f2 = st.columns(2)
      with col_f1:
        fecha_inicio = st.date_input(
            "Desde la fecha:", value=min_fecha, max_value=max_fecha
        )
      with col_f2:
        fecha_fin = st.date_input(
            "Hasta la fecha:", value=max_fecha, min_value=fecha_inicio
        )

      df_ventas["date_obj"] = pd.to_datetime(
          df_ventas["solo_fecha"]
      ).dt.date
      df_filtrado_fechas = df_ventas[
          (df_ventas["date_obj"] >= fecha_inicio)
          & (df_ventas["date_obj"] <= fecha_fin)
      ]

      st.markdown("---")

      # --- CORTE DE CAJA ---
      st.subheader(
          f"💵 Corte de Caja del {fecha_inicio} al {fecha_fin}"
      )

      if not df_filtrado_fechas.empty:
        total_periodo = df_filtrado_fechas["total"].sum()
        efectivo_periodo = df_filtrado_fechas[
            df_filtrado_fechas["metodo_pago"] == "Efectivo"
        ]["total"].sum()
        tarjeta_periodo = df_filtrado_fechas[
            df_filtrado_fechas["metodo_pago"] == "Tarjeta"
        ]["total"].sum()
        trans_periodo = df_filtrado_fechas[
            df_filtrado_fechas["metodo_pago"] == "Transferencia"
        ]["total"].sum()

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.metric("Total Periodo", f"${total_periodo:,.2f}")
        col_c2.metric("Efectivo", f"${efectivo_periodo:,.2f}")
        col_c3.metric("Tarjeta", f"${tarjeta_periodo:,.2f}")
        col_c4.metric("Transferencia", f"${trans_periodo:,.2f}")
      else:
        st.info("No hay ventas registradas en este rango de fechas.")

      st.markdown("---")

      # --- BÚSQUEDA ---
      busqueda = st.text_input(
          "🔍 Buscar por Cliente o Folio de Nota en este periodo",
          placeholder="Escribe el nombre o número...",
      )

      if busqueda:
        df_final = df_filtrado_fechas[
            df_filtrado_fechas["cliente"].str.contains(busqueda, case=False, na=False)
            | df_filtrado_fechas["folio_nota"].str.contains(
                busqueda, case=False, na=False
            )
        ]
      else:
        df_final = df_filtrado_fechas

      # --- EXCEL ---
      csv_data = df_ventas.drop(columns=["solo_fecha", "date_obj"]).to_csv(
          index=False
      )
      st.download_button(
          label="📥 Descargar Todo el Historial en Excel (CSV)",
          data=csv_data.encode("utf-8"),
          file_name=f"Historial_Ventas_Completo_{datetime.now().strftime('%Y-%m-%d')}.csv",
          mime="text/csv",
      )

      st.markdown("---")
      st.write(f"Mostrando {len(df_final)} registro(s):")

      for index, row in df_final.iterrows():
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
          st.markdown("**Acciones:**")

          if st.button(
              f"🖨️ Generar Imagen de Ticket (Folio {row['folio_nota']})",
              key=f"reprint_{row['id']}",
          ):
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

          st.markdown("<br>", unsafe_allow_html=True)
          with st.expander(
              f"⚠️ Zona de Peligro: Borrar Folio {row['folio_nota']}"
          ):
            st.warning(
                "Estás a punto de eliminar este registro permanentemente."
            )
            pass_borrar = st.text_input(
                "Contraseña de Administrador para Borrar",
                type="password",
                key=f"pass_del_{row['id']}",
            )

            if st.button(
                f"🗑️ Confirmar Borrado de Venta {row['folio_nota']}",
                key=f"btn_del_{row['id']}",
            ):
              if pass_borrar == "NAUPA2026":
                conn_del = sqlite3.connect(DB_NAME)
                cursor_del = conn_del.cursor()
                cursor_del.execute(
                    "DELETE FROM ventas WHERE id = ?", (row["id"],)
                )
                conn_del.commit()
                conn_del.close()
                st.success(
                    f"¡Venta con Folio {row['folio_nota']} eliminada con"
                    " éxito!"
                )
                st.rerun()
              else:
                st.error("Contraseña incorrecta para eliminar el registro.")
    else:
      st.info("Aún no hay ventas registradas en el sistema.")
  except Exception as e:
    st.info("Aún no hay registros en la base de datos.")
