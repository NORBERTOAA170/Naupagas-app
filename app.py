import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(
    page_title="NAUPAGAS - Sistema de Ventas",
    page_icon="logo.jpg",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ================= FORZAR ICONO PARA PWA EN MÓVIL =================
st.markdown("""
    <link rel="manifest" href="data:application/manifest+json;charset=utf-8,{
        'name': 'NAUPAGAS',
        'short_name': 'NAUPAGAS',
        'start_url': '.',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': '#ffffff',
        'icons': [{'src': 'logo.jpg', 'sizes': '512x512', 'type': 'image/jpeg'}]
    }">
""", unsafe_allow_html=True)

# ================= CONFIGURACIÓN DE BASE DE DATOS (SQLite) =================
DB_NAME = "naupagas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente TEXT,
            tipo_cilindro TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            total REAL,
            metodo_pago TEXT,
            observaciones TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ================= AUTENTICACIÓN =================
MASTER_PASSWORD = "NAUPA2026"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center;'>⛽ NAUPAGAS - Acceso Operativo</h2>", unsafe_allow_html=True)
    
    try:
        st.image("logo.jpg", width=180)
    except:
        pass
        
    user_input = st.text_input("Usuario")
    pass_input = st.text_input("Contraseña (Master)", type="password")
    
    if st.button("Iniciar Sesión"):
        if user_input == "NAUPA" and pass_input == MASTER_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas. Verifícalas.")
    st.stop()

# ================= BARRA LATERAL (MENÚ Y CONFIGURACIÓN) =================
with st.sidebar:
    try:
        st.image("logo.jpg", width=140)
    except:
        pass
        
    st.markdown("### Menú Principal")
    menu = st.radio("Selecciona una opción", ["Nueva Venta", "Historial / Reportes", "Danger Zone (Eliminar)"])
    
    st.markdown("---")
    if st.button("Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.rerun()

# ================= MÓDULO 1: NUEVA VENTA =================
if menu == "Nueva Venta":
    st.markdown("<h2>🧾 Registro de Venta y Ticket</h2>", unsafe_allow_html=True)
    
    with st.form("form_venta"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nombre del Cliente")
            tipo_cilindro = st.selectbox("Tipo de Cilindro / Presentación", ["10 kg", "20 kg", "30 kg", "45 kg", "Estacionario (Litros)"])
        with col2:
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
            precio_unitario = st.number_input("Precio Unitario ($)", min_value=0.0, value=500.0)
            
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Crédito"])
        observaciones = st.text_area("Observaciones o Dirección de Entrega")
        
        submitted = st.form_submit_button("Generar Venta y Ticket")
        
        if submitted:
            if not cliente:
                st.warning("Por favor ingresa el nombre del cliente.")
            else:
                total = cantidad * precio_unitario
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Guardar en base de datos SQLite (Modo Offline persistente)
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ventas (fecha, cliente, tipo_cilindro, cantidad, precio_unitario, total, metodo_pago, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (fecha_actual, cliente, tipo_cilindro, cantidad, precio_unitario, total, metodo_pago, observaciones))
                conn.commit()
                conn.close()
                
                st.success("¡Venta registrada y guardada con éxito en el sistema!")
                
                # Generación de Ticket en Imagen con Fondo Blanco y Logo
                img_ticket = Image.new('RGB', (550, 750), color=(255, 255, 255))
                d = ImageDraw.Draw(img_ticket)
                
                try:
                    logo_img = Image.open("logo.jpg").resize((120, 70))
                    img_ticket.paste(logo_img, (215, 20))
                    y_offset = 100
                except:
                    y_offset = 30
                
                d.text((180, y_offset), "NAUPAGAS", fill=(0, 0, 0))
                y_offset += 35
                d.text((140, y_offset), "COMPROBANTE DE VENTA OFICIAL", fill=(80, 80, 80))
                y_offset += 35
                d.line([(30, y_offset), (520, y_offset)], fill=(200, 200, 200), width=2)
                y_offset += 20
                
                detalles_ticket = [
                    f"Fecha: {fecha_actual}",
                    f"Cliente: {cliente}",
                    f"Producto: {tipo_cilindro}",
                    f"Cantidad: {cantidad}",
                    f"Precio Unitario: ${precio_unitario:,.2f}",
                    f"Método de Pago: {metodo_pago}",
                    f"Observaciones: {observaciones if observaciones else 'Ninguna'}"
                ]
                
                for linea in detalles_ticket:
                    d.text((40, y_offset), linea, fill=(20, 20, 20))
                    y_offset += 30
                    
                y_offset += 10
                d.line([(30, y_offset), (520, y_offset)], fill=(200, 200, 200), width=2)
                y_offset += 25
                d.text((40, y_offset), f"TOTAL A PAGAR: ${total:,.2f}", fill=(0, 0, 0))
                y_offset += 50
                d.text((130, y_offset), "¡Gracias por su preferencia en NAUPAGAS!", fill=(100, 100, 100))
                
                buf = BytesIO()
                img_ticket.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.image(byte_im, caption="Vista previa del Ticket", use_container_width=True)
                
                st.download_button(
                    label="📥 Descargar Ticket en Imagen",
                    data=byte_im,
                    file_name=f"Ticket_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                    mime="image/png"
                )
                
                whatsapp_text = f"*NAUPAGAS - COMPROBANTE DE VENTA*%0A" \
                                f"----------------------------------------%0A" \
                                f"📅 *Fecha:* {fecha_actual}%0A" \
                                f"👤 *Cliente:* {cliente}%0A" \
                                f"📦 *Producto:* {tipo_cilindro} (x{cantidad})%0A" \
                                f"💲 *Precio Unit.:* ${precio_unitario:,.2f}%0A" \
                                f"💳 *Pago:* {metodo_pago}%0A" \
                                f"📝 *Notas:* {observaciones if observaciones else 'Ninguna'}%0A" \
                                f"----------------------------------------%0A" \
                                f"💰 *TOTAL:* *${total:,.2f}*%0A%0A" \
                                f"¡Gracias por su preferencia!"
                
                st.markdown(f"""
                    <a href="https://api.whatsapp.com/send?text={whatsapp_text}" target="_blank">
                        <button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer; width:100%;">
                            📲 Enviar Ticket por WhatsApp
                        </button>
                    </a>
                """, unsafe_allow_html=True)

# ================= MÓDULO 2: HISTORIAL Y REPORTES =================
elif menu == "Historial / Reportes":
    st.markdown("<h2>📊 Historial de Ventas y Corte</h2>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha, cliente, tipo_cilindro, cantidad, total, metodo_pago FROM ventas ORDER BY id DESC")
    registros = cursor.fetchall()
    conn.close()
    
    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Fecha", "Cliente", "Producto", "Cantidad", "Total ($)", "Pago"])
        st.dataframe(df, use_container_width=True)
        
        total_acumulado = df["Total ($)"].sum()
        st.metric(label="Ingresos Totales Registrados", value=f"${total_acumulado:,.2f}")
    else:
        st.info("Aún no hay ventas registradas en la base de datos.")

# ================= MÓDULO 3: DANGER ZONE (ELIMINAR) =================
elif menu == "Danger Zone (Eliminar)":
    st.markdown("<h2>⚠️ Danger Zone - Gestión de Registros</h2>", unsafe_allow_html=True)
    st.warning("Esta sección está protegida por seguridad para evitar errores operativos.")
    
    pass_entered = st.text_input("Introduce la contraseña Master para desbloquear acciones:", type="password")
    
    if pass_entered == MASTER_PASSWORD:
        st.success("Acceso concedido a la Zona de Riesgo.")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, cliente, total FROM ventas ORDER BY id DESC")
        ventas_raw = cursor.fetchall()
        conn.close()
        
        if ventas_raw:
            opciones_venta = {f"ID: {v[0]} | Fecha: {v[1]} | Cliente: {v[2]} | Total: ${v[3]:,.2f}": v[0] for v in ventas_raw}
            venta_seleccionada = st.selectbox("Selecciona la venta a eliminar:", list(opciones_venta.keys()))
            
            if st.button("🗑️ Eliminar Venta Seleccionada", type="primary"):
                id_a_borrar = opciones_venta[venta_seleccionada]
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ventas WHERE id = ?", (id_a_borrar,))
                conn.commit()
                conn.close()
                st.success(f"Venta con ID {id_a_borrar} eliminada correctamente.")
                st.rerun()
        else:
            st.info("No hay registros para eliminar.")
    elif pass_entered != "":
        st.error("Contraseña incorrecta.")
