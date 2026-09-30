import streamlit as st
import sqlite3
from datetime import datetime
import os
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(page_title="NAUPAGAS - Ventas", page_icon="🔥", layout="centered")

# --- SISTEMA DE LOGIN (ESTRICTO) ---
def verificar_password():
    def password_entered():
        if st.session_state["username"] == "NAUPA" and st.session_state["password"] == "NAUPAGAS2026":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
        
        if "password" in st.session_state:
            del st.session_state["password"]
        if "username" in st.session_state:
            del st.session_state["username"]

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.subheader("🔒 Acceso Restringido - NAUPAGAS")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Iniciar Sesión", on_click=password_entered)
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Usuario o contraseña incorrectos")
        return False
    else:
        return True

if not verificar_password():
    st.stop()

# --- CARPETA DE RESPALDO ---
CARPETA_IMAGENES = "tickets_guardados"
if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

# --- BASE DE DATOS ---
DB_FILE = "gasera_historial.db"

def inicializar_bd():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT,
            telefono TEXT,
            num_nota TEXT UNIQUE,
            num_servicio TEXT,
            tipo_venta TEXT,
            detalle TEXT,
            cantidad REAL,
            precio_unitario REAL,
            total REAL,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_bd()

# --- GENERAR IMAGEN DEL TICKET ---
def generar_imagen_ticket(datos):
    try:
        try:
            fuente_titulo = ImageFont.truetype("arialbd.ttf", 18)
            fuente_negrita = ImageFont.truetype("arialbd.ttf", 13)
            fuente_normal = ImageFont.truetype("arial.ttf", 13)
        except IOError:
            fuente_titulo = ImageFont.load_default()
            fuente_negrita = ImageFont.load_default()
            fuente_normal = ImageFont.load_default()

        ancho = 450
        alto = 620
        img = Image.new("RGB", (ancho, alto), color="white")
        draw = ImageDraw.Draw(img)

        y_inicial_texto = 30
        if os.path.exists("logo.jpg"):
            try:
                logo = Image.open("logo.jpg")
                logo_ancho = 130
                logo_alto = int((logo_ancho / float(logo.size[0])) * logo.size[1])
                logo = logo.resize((logo_ancho, logo_alto), Image.Resampling.LANCZOS)
                pos_x = (ancho - logo_ancho) // 2
                pos_y = 15
                draw.rectangle([pos_x - 10, pos_y - 5, pos_x + logo_ancho + 10, pos_y + logo_alto + 5], fill="white")
                img.paste(logo, (pos_x, pos_y))
                y_inicial_texto = pos_y + logo_alto + 15
            except Exception:
                pass

        header_alto = y_inicial_texto + 50
        draw.rectangle([0, y_inicial_texto, ancho, header_alto], fill="#002147")
        draw.text((225, y_inicial_texto + 15), "NAUPAGAS", fill="white", font=fuente_titulo, anchor="mm")
        draw.text((225, y_inicial_texto + 35), "COMPROBANTE DE VENTA", fill="#FFD700", font=fuente_negrita, anchor="mm")
        y = header_alto + 20
        margen_izq = 30

        elementos = [
            ("Fecha y Hora:", datos['fecha']),
            ("Nota N°:", str(datos['num_nota'])),
            ("Servicio N°:", str(datos['num_servicio'])),
            ("Cliente:", datos['nombre']),
            ("Teléfono:", datos['telefono']),
            ("----------------------------------------", ""),
            ("Tipo de Venta:", datos['tipo']),
            ("Desglose:", datos['detalle']),
            ("Precio Unitario:", f"${datos['precio_unitario']:.2f}"),
            ("----------------------------------------", "")
        ]

        for etiqueta, valor in elementos:
            if "---" in etiqueta:
                draw.line([(margen_izq, y + 5), (ancho - margen_izq, y + 5)], fill="#cccccc", width=2)
                y += 22
            else:
                draw.text((margen_izq, y), etiqueta, fill="#555555", font=fuente_normal)
                draw.text((ancho - margen_izq, y), str(valor), fill="#000000", font=fuente_negrita, anchor="rt")
                y += 26
        y += 5
        draw.rectangle([margen_izq, y, ancho - margen_izq, y + 48], outline="#002147", width=2, fill="#f4f6f9")
        draw.text((margen_izq + 15, y + 14), "TOTAL A PAGAR:", fill="#002147", font=fuente_negrita)
        draw.text((ancho - margen_izq - 15, y + 11), f"${datos['total']:.2f}", fill="#008000", font=fuente_titulo, anchor="rt")
        y += 65
        draw.text((225, y), "¡Gracias por su preferencia!", fill="#666666", font=fuente_normal, anchor="mm")
        
        ruta_png = os.path.join(CARPETA_IMAGENES, f"Nota_{datos['num_nota']}.png")
        img.save(ruta_png)
        return ruta_png
    except Exception as e:
        st.error(f"Error al generar imagen: {e}")
        return None

def formatear_telefono(tel_sucio):
    digitos = "".join(filter(str.isdigit, tel_sucio))
    if len(digitos) == 10:
        return "52" + digitos
    return digitos

# --- INTERFAZ WEB DEL SISTEMA ---
st.title("🔥 NAUPAGAS - Control de Ventas 🔥")

with st.form("formulario_venta", clear_on_submit=True):
    st.subheader("1. Datos Generales")
    col1, col2 = st.columns(2)
    nombre_cliente = col1.text_input("Nombre del Cliente")
    telefono_cliente = col2.text_input("Teléfono (10 dígitos)")
    
    col3, col4 = st.columns(2)
    num_nota = col3.text_input("Número de Nota (ÚNICO)")
    num_servicio = col4.text_input("Número de Servicio")

    st.divider()
    st.subheader("2. Detalle de la Venta")
    tipo_venta = st.radio("Selecciona el tipo de venta:", ["Litros (Estacionario)", "Cilindro"], horizontal=True)

    # --- CAMPOS DINÁMICOS SEGÚN EL TIPO DE VENTA ---
    if tipo_venta == "Litros (Estacionario)":
        cant_litros = st.number_input("Litros cargados", min_value=0.0, step=0.5, format="%.1f")
        precio_litro = st.number_input("Precio por Litro ($)", min_value=0.0, step=0.1, format="%.2f")
        total = cant_litros * precio_litro
        detalle = f"{cant_litros} Lts"
        cantidad = cant_litros
        precio_unitario = precio_litro
    else:
        # Selección exclusiva mediante menú desplegable (sin permitir escritura manual)
        capacidad_cil = st.selectbox("Capacidad del cilindro", ["10 kg", "20 kg", "30 kg"])
        cant_cilindros = st.number_input("¿Cuántos cilindros?", min_value=1, step=1)
        precio_cil = st.number_input("Precio por Cilindro ($)", min_value=0.0, step=1.0, format="%.2f")
        total = cant_cilindros * precio_cil
        detalle = f"{int(cant_cilindros)} cilindro(s) de {capacidad_cil}"
        cantidad = cant_cilindros
        precio_unitario = precio_cil

    st.info(f"Total a Pagar: **${total:.2f}**")
    
    submitted = st.form_submit_button("REGISTRAR VENTA Y GUARDAR IMAGEN")

if submitted:
    if not nombre_cliente or not telefono_cliente or not num_nota or not num_servicio:
        st.error("Por favor completa todos los datos generales.")
    elif not num_nota.isdigit() or not num_servicio.isdigit():
         st.error("Nota y Servicio deben ser números.")
    else:
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id FROM ventas WHERE num_nota = ?", (num_nota,))
            if c.fetchone():
                st.error(f"Error: La Nota #{num_nota} ya existe.")
            else:
                c.execute("""
                    INSERT INTO ventas (nombre_cliente, telefono, num_nota, num_servicio, tipo_venta, detalle, cantidad, precio_unitario, total, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nombre_cliente, formatear_telefono(telefono_cliente), num_nota, num_servicio, tipo_venta, detalle, cantidad, precio_unitario, total, fecha_actual))
                conn.commit()
                conn.close()
                
                datos_ticket = {
                    "nombre": nombre_cliente,
                    "telefono": telefono_cliente,
                    "num_nota": num_nota,
                    "num_servicio": num_servicio,
                    "tipo": tipo_venta,
                    "detalle": detalle,
                    "precio_unitario": precio_unitario,
                    "total": total,
                    "fecha": fecha_actual
                }
                
                ruta_imagen = generar_imagen_ticket(datos_ticket)
                if ruta_imagen and os.path.exists(ruta_imagen):
                    st.success(f"¡Venta #{num_nota} registrada correctamente!")
                    st.balloons()
                    with open(ruta_imagen, "rb") as file:
                        st.download_button(
                            label="⬇ Descargar IMAGEN del Ticket",
                            data=file,
                            file_name=f"Ticket_Nota_{num_nota}.png",
                            mime="image/png"
                        )
                    mensaje_wsp = (
                        f"NAUPAGAS - COMPROBANTE DE VENTA\n"
                        f"Nota: {num_nota}\n"
                        f"Cliente: {nombre_cliente}\n"
                        f"Total: ${total:.2f}"
                    )
                    mensaje_codificado = urllib.parse.quote(f"```\n{mensaje_wsp}\n```")
                    link_whatsapp = f"https://wa.me/{formatear_telefono(telefono_cliente)}?text={mensaje_codificado}"
                    st.link_button("💬 Enviar Ticket por WhatsApp al Cliente", link_whatsapp)
                else:
                    st.error("La venta se guardó en la BD pero falló la generación de la imagen.")
        except Exception as e:
            st.error(f"Error general al guardar: {e}")