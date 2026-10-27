from datetime import datetime, time, date
import time as time_module
from zoneinfo import ZoneInfo
import os
import requests
import tempfile
import streamlit as st

# Supabase SDK para sincronización en la nube
try:
    from supabase import create_client
    SUPABASE_DISPONIBLE = True
except ImportError:
    SUPABASE_DISPONIBLE = False

# Librerías de QR y PDF
try:
    from fpdf import FPDF
    FPDF_DISPONIBLE = True
except ImportError:
    FPDF_DISPONIBLE = False

try:
    import qrcode
    QRCODE_DISPONIBLE = True
except ImportError:
    QRCODE_DISPONIBLE = False

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(
    page_title="NAUPAGAS - Módulo Carta Porte",
    page_icon="🔥",
    layout="wide"
)

MASTER_PASSWORD = "NAUPAGAS2026"

# ================= CREDENCIALES DE SUPABASE (NUBE) =================
SUPABASE_URL = "https://qikmlgbnwbdmuqziemia.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpa21sZ2Jud2JkbXVxemllbWlhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI1MTg0NzUsImV4cCI6MjEwODA5NDQ3NX0.s7J6uZxohN49BocGUwBqc02S7jZFbMOoeF9Om-DYTfQ"

@st.cache_resource
def init_supabase():
    if SUPABASE_DISPONIBLE and SUPABASE_KEY:
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            return None
    return None

supabase = init_supabase()

# ================= BASE DE DATOS INICIAL (SEED PARA SUPABASE) =================
DEFAULT_CATALOGO_NAUPA = [
    {
        "nombre": "ALFONSO GONZALEZ ORTIZ",
        "tipo": "Federal",
        "rfc": "GOOA900609TC5",
        "licencia": "LFD00008878",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "STERLING",
        "eco": "PIPA GRANDE 1",
        "capacidad_txt": "12900 Lts",
        "capacidad_num": 12900.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XF4354B",
        "aseguradora": "Qualitas",
        "poliza": "7150015853",
        "ruta": ""
    },
    {
        "nombre": "MARTIN GONZALEZ LEON",
        "tipo": "Estatal",
        "rfc": "GOLM751110157",
        "licencia": "UB003RH9Z",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CHRYSLER",
        "eco": "PIPA GRANDE 2",
        "capacidad_txt": "12900 Lts",
        "capacidad_num": 12900.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XV0965A",
        "aseguradora": "Qualitas",
        "poliza": "7150014122",
        "ruta": ""
    },
    {
        "nombre": "MARCO ANTONIO ALVARADO DURAN",
        "tipo": "Estatal",
        "rfc": "AADM6906159J4",
        "licencia": "MT123507",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "FREIGHTLINER M2 106 35K",
        "eco": "PIPA GRANDE 3",
        "capacidad_txt": "13900 Lts",
        "capacidad_num": 13900.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XX2879A",
        "aseguradora": "Qualitas",
        "poliza": "7150014122",
        "ruta": ""
    },
    {
        "nombre": "ALFONSO GONZALEZ ORTIZ (24,000 LTS)",
        "tipo": "Federal",
        "rfc": "GOOA900609TC5",
        "licencia": "LFD00008878",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "FREIGHTLINER M2 106 35K",
        "eco": "PIPA GRANDE 4",
        "capacidad_txt": "24000 Lts",
        "capacidad_num": 24000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "18AF4Y",
        "aseguradora": "Qualitas",
        "poliza": "7150014491",
        "ruta": ""
    },
    {
        "nombre": "RODRIGO LOPEZ ALCANTARA (NUEVA)",
        "tipo": "Estatal",
        "rfc": "LOAR9112225J2",
        "licencia": "UB0CKN1S4",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CHRYSLER RAM 4000",
        "eco": "S/N",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "YB8729B",
        "aseguradora": "Qualitas",
        "poliza": "7150015855",
        "ruta": "ECONOGAS"
    },
    {
        "nombre": "RODRIGO LOPEZ ALCANTARA",
        "tipo": "Estatal",
        "rfc": "LOAR9112225J2",
        "licencia": "UB0CKN1S4",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CS FORD F-500 CHASIS CABINA",
        "eco": "9",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XU91794",
        "aseguradora": "Qualitas",
        "poliza": "7150015083",
        "ruta": "Perote, Jalacingo, Orilla del Monte y San Juan"
    },
    {
        "nombre": "HERACLIO ARMANDO MACHUCA SILVA",
        "tipo": "Estatal",
        "rfc": "MASH580804",
        "licencia": "UB003R85C",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CHRYSLER RAM 4000",
        "eco": "5",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XF4338B",
        "aseguradora": "Qualitas",
        "poliza": "7150013784",
        "ruta": "Perote, Alchichica, Sierra de Agua, Molinos, Tenextepec, Magueyitos, Los Antos"
    },
    {
        "nombre": "CARLOS GONZALEZ ORTIZ",
        "tipo": "Estatal",
        "rfc": "GOOC820603QN0",
        "licencia": "UB0N3KX2K",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CHEVROLET SILVERADO",
        "eco": "6",
        "capacidad_txt": "4500 Lts",
        "capacidad_num": 4500.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XT4418B",
        "aseguradora": "Qualitas",
        "poliza": "7150015633",
        "ruta": "Perote, Libertad, Madero, Villa Aldama y Tenextepec"
    },
    {
        "nombre": "PORFIRIO HERNANDEZ CAMPUZANO",
        "tipo": "Estatal",
        "rfc": "HECP8606053H1",
        "licencia": "UBOCKQOY4",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CS CHRYSLER RAM 4000 5.7L",
        "eco": "23",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "YB8730B",
        "aseguradora": "Qualitas",
        "poliza": "7150013987",
        "ruta": "Perote, Sierra de agua, Madero, Tenextepec y alrededores"
    },
    {
        "nombre": "DAVID EUGENIO ROMERO",
        "tipo": "Estatal",
        "rfc": "EURD970221PQ0",
        "licencia": "UB0N3KQAQ",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CHRYSLER RAM 4000",
        "eco": "3",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XP3908B",
        "aseguradora": "Qualitas",
        "poliza": "7150015604",
        "ruta": "Perote, Las Vigas, La Joya, Banderilla, San Miguel, El Fresno, Xalapa, Alchichica"
    },
    {
        "nombre": "JOSE EUGENIO ROMERO",
        "tipo": "Estatal",
        "rfc": "EURJ040215KN5",
        "licencia": "UBOCKUCUH",
        "tipo_unidad_sat": "Autotanque (Pipa)",
        "marca": "CS FORD F-350 CHASIS CABINA",
        "eco": "10",
        "capacidad_txt": "4000 Lts",
        "capacidad_num": 4000.0,
        "cant_20": 0,
        "cant_30": 0,
        "placas": "XX9342A",
        "aseguradora": "Qualitas",
        "poliza": "7150014152",
        "ruta": "Totalco, Alchichica, Sarabia, Tepeyahualco, Perote"
    },
    {
        "nombre": "JUAN ADRIAN MOTA MARTINEZ",
        "tipo": "Estatal",
        "rfc": "MOMJ961029UJ0",
        "licencia": "UB0N3KZ7D",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX",
        "eco": "CILINDRERA 7",
        "capacidad_txt": "19 de 20 kg y 9 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 19,
        "cant_30": 9,
        "placas": "XP4212B",
        "aseguradora": "GNP SEGUROS",
        "poliza": "TFSM0003070351",
        "ruta": "Perote, Madero, Molinos"
    },
    {
        "nombre": "JOSÉ CALIXTO ISAEL MACHUCA ORTEGA",
        "tipo": "Estatal",
        "rfc": "MAOC681114US7",
        "licencia": "UB0N3LEMC",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX",
        "eco": "CILINDRERA 17",
        "capacidad_txt": "13 de 20 kg y 9 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 13,
        "cant_30": 9,
        "placas": "XP4211B",
        "aseguradora": "GNP SEGUROS",
        "poliza": "TFSM000307346",
        "ruta": "La joya, Las vigas, Cruz blanca, El cajete"
    },
    {
        "nombre": "SAUL UBIRACI GALLARDO",
        "tipo": "Estatal",
        "rfc": "GAHS570419GB2",
        "licencia": "UB0N3L5GY",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX",
        "eco": "CILINDRERA 3",
        "capacidad_txt": "17 de 20 kg y 4 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 17,
        "cant_30": 4,
        "placas": "XX2756A",
        "aseguradora": "AXA",
        "poliza": "YBJ006730000",
        "ruta": "Guadalupe Victoria y alrededores"
    },
    {
        "nombre": "ROSENDO SESENA HERNANDEZ",
        "tipo": "Estatal",
        "rfc": "SEHR690624115",
        "licencia": "UBOCKMSYG",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX",
        "eco": "CILINDRERA 6",
        "capacidad_txt": "19 de 20 kg y 5 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 19,
        "cant_30": 5,
        "placas": "XX2755A",
        "aseguradora": "QUALITAS",
        "poliza": "7150013591",
        "ruta": "Totalco y Alchichica"
    },
    {
        "nombre": "JOSE ARMANDO HERNANDEZ MIRANDA",
        "tipo": "Estatal",
        "rfc": "HEMA970620NI4",
        "licencia": "UB0N3BE6L",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX 2 PUERTAS",
        "eco": "CILINDRERA 16",
        "capacidad_txt": "19 de 20 kg y 12 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 19,
        "cant_30": 12,
        "placas": "XH8078B",
        "aseguradora": "QUALITAS",
        "poliza": "7150013816",
        "ruta": "Altotonga y alrededores"
    },
    {
        "nombre": "JORGE ALFONSO SERRANO CORTINA (SAN MIGUEL)",
        "tipo": "Estatal",
        "rfc": "UA033PVAN",
        "licencia": "SECJ9201067D4",
        "tipo_unidad_sat": "Vehículo Repartidor (Cilindrera)",
        "marca": "TOYOTA HILUX",
        "eco": "CILINDRERA 8",
        "capacidad_txt": "10 de 20 kg y 10 de 30 kg",
        "capacidad_num": 0.0,
        "cant_20": 10,
        "cant_30": 10,
        "placas": "XH8079B",
        "aseguradora": "QUALITAS",
        "poliza": "7150015084",
        "ruta": "San Miguel, Tlacolula, El fresno"
    }
]

# ================= FUNCIONES DE NUBE (SUPABASE) =================
def obtener_siguiente_folio_nube():
    if supabase is None:
        return "0000001"
    try:
        response = supabase.table("folios_naupagas").select("ultimo_folio").eq("id", 1).execute()
        if response.data and len(response.data) > 0:
            ultimo = response.data[0]["ultimo_folio"]
            nuevo_folio = ultimo + 1
            supabase.table("folios_naupagas").update({"ultimo_folio": nuevo_folio}).eq("id", 1).execute()
            return f"{nuevo_folio:07d}"
        else:
            supabase.table("folios_naupagas").insert({"id": 1, "ultimo_folio": 1}).execute()
            return "0000001"
    except Exception as e:
        st.error(f"⚠️ Error al obtener folio de Supabase: {e}")
        return "0000001"

def guardar_carta_en_nube(datos):
    if supabase is not None:
        try:
            supabase.table("cartas_naupagas").insert(datos).execute()
            return True
        except Exception as e:
            st.error(f"❌ Error al guardar en Supabase: {e}")
            return False
    else:
        st.error("⚠️ La conexión con Supabase no está activa.")
        return False

def cargar_historial_nube():
    if supabase is not None:
        try:
            response = supabase.table("cartas_naupagas").select("*").order("id", desc=True).execute()
            return response.data or []
        except Exception as e:
            st.error(f"⚠️ Error al cargar historial de Supabase: {e}")
            return []
    return []

def eliminar_carta_nube(carta_id):
    if supabase is not None:
        try:
            supabase.table("cartas_naupagas").delete().eq("id", carta_id).execute()
            return True
        except Exception as e:
            st.error(f"❌ Error al eliminar de Supabase: {e}")
            return False
    return False

# --- GESTIÓN DINÁMICA DEL CATÁLOGO EN SUPABASE ---
def cargar_catalogo_nube():
    if supabase is None:
        return DEFAULT_CATALOGO_NAUPA
    try:
        response = supabase.table("catalogo_choferes_naupagas").select("*").execute()
        if response.data and len(response.data) > 0:
            return response.data
        else:
            # Sembrar datos iniciales si la tabla está vacía
            for item in DEFAULT_CATALOGO_NAUPA:
                supabase.table("catalogo_choferes_naupagas").insert(item).execute()
            response = supabase.table("catalogo_choferes_naupagas").select("*").execute()
            return response.data or DEFAULT_CATALOGO_NAUPA
    except Exception as e:
        return DEFAULT_CATALOGO_NAUPA

def guardar_chofer_nube(datos):
    if supabase is not None:
        try:
            supabase.table("catalogo_choferes_naupagas").insert(datos).execute()
            return True
        except Exception as e:
            st.error(f"Error al guardar chofer: {e}")
            return False
    return False

def actualizar_chofer_nube(chofer_id, datos):
    if supabase is not None:
        try:
            supabase.table("catalogo_choferes_naupagas").update(datos).eq("id", chofer_id).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar chofer: {e}")
            return False
    return False

def eliminar_chofer_nube(chofer_id):
    if supabase is not None:
        try:
            supabase.table("catalogo_choferes_naupagas").delete().eq("id", chofer_id).execute()
            return True
        except Exception as e:
            st.error(f"Error al eliminar chofer: {e}")
            return False
    return False

if "auth_naupagas" not in st.session_state:
    st.session_state.auth_naupagas = False

CATALOGO_LOCAL_CP = {
    "91400": {"colonia": "Perote Centro", "municipio": "Perote", "estado": "Veracruz", "pais": "México"},
    "91403": {"colonia": "El Sabinal", "municipio": "Perote", "estado": "Veracruz", "pais": "México"},
    "91405": {"colonia": "Fovissste", "municipio": "Perote", "estado": "Veracruz", "pais": "México"},
    "91285": {"colonia": "Tenextepec", "municipio": "Perote", "estado": "Veracruz", "pais": "México"},
    "91282": {"colonia": "El Limon", "municipio": "Perote", "estado": "Veracruz Llave", "pais": "México"},
    "91000": {"colonia": "Xalapa Enríquez Centro", "municipio": "Xalapa", "estado": "Veracruz", "pais": "México"},
    "91190": {"colonia": "Ánimas", "municipio": "Xalapa", "estado": "Veracruz", "pais": "México"},
    "91110": {"colonia": "Badillo", "municipio": "Xalapa", "estado": "Veracruz", "pais": "México"},
    "91700": {"colonia": "Veracruz Centro", "municipio": "Veracruz", "estado": "Veracruz", "pais": "México"},
    "72000": {"colonia": "Puebla Centro", "municipio": "Puebla", "estado": "Puebla", "pais": "México"},
    "72100": {"colonia": "La Paz", "municipio": "Puebla", "estado": "Puebla", "pais": "México"}
}

@st.cache_data(show_spinner=False)
def consultar_cp_mexico(cp):
    cp = str(cp).strip()
    if not cp or len(cp) != 5 or not cp.isdigit():
        return {"colonia": "", "municipio": "", "estado": "", "pais": "México"}
    if cp in CATALOGO_LOCAL_CP:
        return CATALOGO_LOCAL_CP[cp]
    try:
        url = f"https://api.zippopotam.us/MX/{cp}"
        resp = requests.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            places = data.get("places", [])
            if places:
                colonia = places[0].get("place name", "")
                estado = places[0].get("state", "")
                return {"colonia": colonia, "municipio": estado, "estado": estado, "pais": "México"}
    except Exception:
        pass
    return {"colonia": "", "municipio": "", "estado": "", "pais": "México"}

def safe_str(val):
    if val is None:
        return ""
    texto = str(val).replace("–", "-").replace("—", "-")
    return texto.encode('latin-1', 'replace').decode('latin-1')

def generar_qr_tempfile(contenido):
    if not QRCODE_DISPONIBLE:
        return None
    try:
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=1)
        qr.add_data(contenido)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(tmp.name, format='PNG')
        tmp.close()
        return tmp.name
    except Exception:
        return None

def generar_pdf(d):
    qr_path = None
    try:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        logo_path = "logo.jpg"
        if os.path.exists(logo_path):
            try:
                pdf.image(logo_path, 10, 8, 38)
            except:
                pass

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 8, safe_str("NAUPAGAS S.A. DE C.V."), align="C", ln=True)
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 6, safe_str("CARTA PORTE"), align="C", ln=True)
        pdf.set_font("helvetica", "", 8)
        
        folio_val = d.get('folio', '0000001')
        pdf.cell(0, 5, safe_str(f"FOLIO: {folio_val} | Fecha de Emisión: {d.get('fecha_registro', '')}"), align="C", ln=True)
        pdf.ln(4)

        def seccion_pdf(titulo):
            pdf.set_fill_color(220, 225, 230)
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(0, 6, safe_str(f"  {titulo}"), fill=True, ln=True)
            pdf.ln(2)

        seccion_pdf("1. DATOS DEL EMISOR Y PERMISO DE DISTRIBUCIÓN")
        pdf.set_font("helvetica", "", 8)
        pdf.cell(95, 5, safe_str(f"Empresa / Razón Social: {d.get('nombre_emisor', '')}"), ln=0)
        pdf.cell(95, 5, safe_str(f"RFC Emisor: {d.get('rfc_emisor', '')}"), ln=1)
        pdf.cell(0, 5, safe_str(f"Permiso Distribución Gas LP: {d.get('num_permiso_sct', '')}"), ln=1)
        pdf.ln(3)

        seccion_pdf("2. DATOS DEL OPERADOR / CHOFER (FIGURA TRANSPORTE)")
        pdf.set_font("helvetica", "", 8)
        pdf.cell(95, 5, safe_str(f"Chofer: {d.get('nombre_chofer', '')}"), ln=0)
        pdf.cell(95, 5, safe_str(f"RFC Chofer: {d.get('rfc_chofer', '')}"), ln=1)
        pdf.cell(95, 5, safe_str(f"Tipo de Licencia: {d.get('tipo_licencia', '')}"), ln=0)
        pdf.cell(95, 5, safe_str(f"Número de Licencia: {d.get('num_licencia', '')}"), ln=1)
        pdf.ln(3)

        seccion_pdf("3. DATOS DE LA UNIDAD Y SEGURO DE RESPONSABILIDAD")
        pdf.set_font("helvetica", "", 8)
        pdf.cell(95, 5, safe_str(f"Unidad: {d.get('tipo_unidad', '')} - Eco: {d.get('eco_unidad', '')}"), ln=0)
        pdf.cell(95, 5, safe_str(f"Placas: {d.get('placas', '')}"), ln=1)
        pdf.cell(95, 5, safe_str(f"Marca/Modelo: {d.get('marca_modelo', '')} (Cap: {d.get('capacidad', '')})"), ln=0)
        pdf.cell(95, 5, safe_str(f"Aseguradora: {d.get('aseguradora', '')} | Póliza: {d.get('num_poliza', '')}"), ln=1)
        pdf.ln(3)

        seccion_pdf("4. RUTA DE TRÁNSITO (ORIGEN Y DESTINO)")
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(18, 5, safe_str("ORIGEN:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(100, 5, safe_str(f"{d.get('nombre_origen', '')}"), ln=0)
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(12, 5, safe_str("RFC:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 5, safe_str(f"{d.get('rfc_origen', '')}"), ln=1)
        
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(28, 5, safe_str("Fecha de Salida:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 5, safe_str(f"{d.get('fecha_salida', '')}"), ln=1)
        
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(18, 5, safe_str("Dirección:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.multi_cell(0, 5, safe_str(f"{d.get('dir_origen', '')}"))
        pdf.ln(2)

        pdf.set_font("helvetica", "B", 8)
        pdf.cell(18, 5, safe_str("DESTINO:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(100, 5, safe_str(f"{d.get('nombre_destino', '')}"), ln=0)
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(12, 5, safe_str("RFC:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        rfc_dest_val = d.get('rfc_destino', '') if str(d.get('rfc_destino', '')).strip() else "S/N (Público General)"
        pdf.cell(0, 5, safe_str(f"{rfc_dest_val}"), ln=1)
        
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(28, 5, safe_str("Llegada Estimada:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 5, safe_str(f"{d.get('fecha_llegada', '')}"), ln=1)
        
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(18, 5, safe_str("Dirección:"), ln=0)
        pdf.set_font("helvetica", "", 8)
        pdf.multi_cell(0, 5, safe_str(f"{d.get('dir_destino', '')}"))
        pdf.ln(3)

        seccion_pdf("5. DESCRIPCIÓN Y CLAVES DE LA MERCANCÍA")
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 5, safe_str(f"Producto: {d.get('desc_mercancia', '')} | Clave SAT: {d.get('clave_prod_sat', '')}"), ln=1)
        
        peso_val = d.get('peso_mercancia', '')
        if peso_val and peso_val != "N/A":
            pdf.cell(95, 5, safe_str(f"Cantidad: {d.get('cantidad_mercancia', '')} ({d.get('clave_unidad_sat', '')})"), ln=0)
            pdf.cell(95, 5, safe_str(f"Peso Total: {peso_val}"), ln=1)
        else:
            pdf.cell(0, 5, safe_str(f"Cantidad: {d.get('cantidad_mercancia', '')} ({d.get('clave_unidad_sat', '')})"), ln=1)
            
        pdf.ln(4)

        seccion_pdf("6. VALIDACIÓN Y VERIFICACIÓN OPERATIVA")
        enlace_qr = "https://l1nq.com/3aqpov5"
        qr_path = generar_qr_tempfile(enlace_qr)
        
        if qr_path and os.path.exists(qr_path):
            y_inicial = pdf.get_y()
            try:
                pdf.image(qr_path, x=15, y=y_inicial, w=38)
            except:
                pass
            pdf.set_x(56)
            pdf.set_font("helvetica", "B", 8)
            pdf.cell(0, 4, safe_str(f"Folio: {folio_val}"), ln=1)
            pdf.set_x(56)
            pdf.set_font("helvetica", "", 7)
            pdf.cell(0, 4, safe_str("Estatus de Verificación: ACCESO AL PORTAL DE CONSULTA"), ln=1)
            pdf.set_x(56)
            pdf.cell(0, 4, safe_str(f"Permiso Distribución Gas LP: {d.get('num_permiso_sct', '')}"), ln=1)
            pdf.set_x(56)
            pdf.multi_cell(0, 4, safe_str("Este documento ampara el traslado operado con las especificaciones técnicas requeridas."))

        y_actual = pdf.get_y()
        y_limite_qr = y_inicial + 40
        if y_actual < y_limite_qr:
            pdf.set_y(y_limite_qr)

        pdf.ln(4)
        pdf.set_font("helvetica", "B", 8)
        pdf.multi_cell(0, 4, safe_str("SI USTED TIENE UNA DUDA O PREGUNTA SOBRE ESTA CARTA PORTE, FAVOR DE CONTACTARNOS AL NÚMERO 282 - 103 - 3534"), align="C")

        out = pdf.output(dest='S')
        if isinstance(out, str):
            return out.encode('latin1')
        return bytes(out)
    except Exception as e:
        pdf_err = FPDF()
        pdf_err.add_page()
        pdf_err.set_font("helvetica", "B", 12)
        pdf_err.cell(0, 10, safe_str(f"Error técnico PDF: {str(e)[:45]}"), ln=True)
        out_err = pdf_err.output(dest='S')
        if isinstance(out_err, str):
            return out_err.encode('latin1')
        return bytes(out_err)
    finally:
        if qr_path and os.path.exists(qr_path):
            try:
                os.remove(qr_path)
            except:
                pass

if not st.session_state.auth_naupagas:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        logo_path = "logo.jpg" if os.path.exists("logo.jpg") else ""
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>🔥</h1>", unsafe_allow_html=True)
            
    st.markdown("<h2 style='text-align: center; color: #004080;'>NAUPAGAS S.A. DE C.V.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Módulo de Generación de Carta Porte</p>", unsafe_allow_html=True)
    
    col_a1, col_a2, col_a3 = st.columns([1, 1.2, 1])
    with col_a2:
        pass_input = st.text_input("Contraseña de Acceso", type="password")
        if st.button("Ingresar al Módulo", type="primary", use_container_width=True):
            if pass_input == MASTER_PASSWORD:
                st.session_state.auth_naupagas = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

with st.sidebar:
    logo_path = "logo.jpg" if os.path.exists("logo.jpg") else ""
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    st.markdown("### 🎛️ Menú de Navegación")
    accion = st.radio("Selecciona una opción:", ["Nueva Carta Porte", "Historial de Documentos", "⚙️ Administrar Catálogo"])
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.auth_naupagas = False
        st.rerun()

ahora_mx = datetime.now(ZoneInfo("America/Mexico_City"))
CATALOGO_CHOFERES_NAUPA = cargar_catalogo_nube()

if accion == "Nueva Carta Porte":
    st.title("📄 NAUPAGAS - Generador de Carta Porte")
    st.write("Complete los campos oficiales requeridos para el tránsito seguro de la unidad.")
    st.markdown("---")

    with st.container(border=True):
        st.subheader("1. 🏢 Datos del Emisor y Permiso de Distribución")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            nombre_emisor = st.text_input("Razón Social / Empresa Emisora", value="NAUPAGAS S.A. de C.V.")
        with col_e2:
            rfc_emisor = st.text_input("RFC del Emisor", value="NGA1608221S4")
        
        num_permiso_sct = st.text_input("Permiso de Distribución de Gas LP", value="LP/20474/DIST/PLA/2017")

    def_tipo_unidad_sat = "Autotanque (Pipa)"
    def_eco = ""
    def_placas = ""
    def_marca = ""
    def_capacidad_txt = "12,900 Lts"
    def_capacidad_num = 4000.0
    def_cant_20 = 19
    def_cant_30 = 9
    def_aseguradora = ""
    def_poliza = ""
    def_ruta = ""

    with st.container(border=True):
        st.subheader("2. 👤 Datos del Operador / Chofer (Figura Transporte)")
        
        modo_chofer = st.radio("Modo de Selección de Chofer:", ["Catálogo de Operadores", "Personalizado (Manual)"], horizontal=True)

        if modo_chofer == "Catálogo de Operadores" and CATALOGO_CHOFERES_NAUPA:
            nombres_choferes = [c["nombre"] for c in CATALOGO_CHOFERES_NAUPA]
            
            chofer_seleccionado = st.selectbox(
                "Seleccione al Chofer del Catálogo", 
                options=nombres_choferes
            )
            
            datos_chofer_actual = next((c for c in CATALOGO_CHOFERES_NAUPA if c["nombre"] == chofer_seleccionado), CATALOGO_CHOFERES_NAUPA[0])
            
            def_tipo_unidad_sat = datos_chofer_actual.get("tipo_unidad_sat", "Autotanque (Pipa)")
            def_eco = datos_chofer_actual.get("eco", "")
            def_placas = datos_chofer_actual.get("placas", "")
            def_marca = datos_chofer_actual.get("marca", "")
            def_capacidad_txt = datos_chofer_actual.get("capacidad_txt", "4000 Lts")
            def_capacidad_num = float(datos_chofer_actual.get("capacidad_num", 4000.0))
            def_cant_20 = int(datos_chofer_actual.get("cant_20", 0))
            def_cant_30 = int(datos_chofer_actual.get("cant_30", 0))
            def_aseguradora = datos_chofer_actual.get("aseguradora", "")
            def_poliza = datos_chofer_actual.get("poliza", "")
            def_ruta = datos_chofer_actual.get("ruta", "")

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                nombre_chofer = st.text_input("Nombre Seleccionado / Registrado", value=chofer_seleccionado, disabled=True)
                rfc_chofer = st.text_input("RFC del Chofer (Oficial)", value=datos_chofer_actual.get("rfc", ""), disabled=True)
            with col_c2:
                tipo_licencia = st.text_input("Tipo de Licencia (Oficial)", value=datos_chofer_actual.get("tipo", ""), disabled=True)
                num_licencia = st.text_input("Número de Licencia (Oficial)", value=datos_chofer_actual.get("licencia", ""), disabled=True)
        else:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                nombre_chofer = st.text_input("Nombre Completo del Chofer", placeholder="Nombre completo del chofer")
                rfc_chofer = st.text_input("RFC del Chofer", placeholder="XAXX010101000")
            with col_c2:
                tipo_licencia = st.selectbox("Tipo de Licencia", ["Federal", "Estatal", "Chofer / Vendedor"])
                num_licencia = st.text_input("Número de Licencia", placeholder="Número oficial de licencia")

    with st.container(border=True):
        st.subheader("3. ⛽ Datos de la Unidad")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            if modo_chofer == "Catálogo de Operadores":
                tipo_unidad = st.text_input("Tipo de Unidad (Oficial por Catálogo)", value=def_tipo_unidad_sat, disabled=True)
            else:
                tipo_unidad = st.selectbox("Tipo de Unidad", ["Autotanque (Pipa)", "Vehículo Repartidor (Cilindrera)"])
                
            eco_unidad = st.text_input("Número Económico", value=def_eco, placeholder="Ej. PIPA GRANDE 2 o CILINDRERA 7")
            placas = st.text_input("Placas", value=def_placas, placeholder="Ej. XX-00-XXX")
        with col_u2:
            marca_modelo = st.text_input("Marca / Modelo", value=def_marca, placeholder="Ej. FREIGHTLINER M2 106 35K")
            capacidad = st.text_input("Capacidad descriptiva de la unidad", value=def_capacidad_txt, placeholder="Ej. 12900 Lts o 17 de 20 kg y 4 de 30 kg")

    with st.container(border=True):
        st.subheader("4. 🛡️ Póliza de Seguro")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            aseguradora = st.text_input("Compañía Aseguradora", value=def_aseguradora, placeholder="Ej. Qualitas, AXA, GNP")
        with col_s2:
            num_poliza = st.text_input("Número de Póliza", value=def_poliza, placeholder="Ej. 7150014491")

    with st.container(border=True):
        st.subheader("5. 📍 Ruta de Tránsito (Origen y Destino)")
        col_origen, col_destino = st.columns(2)

        with col_origen:
            st.markdown("#### 🛫 ORIGEN")
            tipo_modo_origen = st.radio("Modalidad de Origen:", ["Planta NAUPAGAS (Oficial)", "Otro Origen (Manual)"], horizontal=False, key="radio_origen")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                f_salida_date = st.date_input("Fecha de Salida", value=ahora_mx.date())
            with col_f2:
                if "hora_salida_input" not in st.session_state:
                    st.session_state.hora_salida_input = ahora_mx.strftime("%H:%M")
                hora_salida_str = st.text_input("Hora de Salida (HH:MM)", key="hora_salida_input")

            if tipo_modo_origen == "Planta NAUPAGAS (Oficial)":
                rfc_origen = "NGA1608221S4"
                nombre_origen = "NAUPAGAS"
                cp_origen = "91282"
                colonia_origen = "El Limon"
                municipio_origen = "Perote"
                estado_origen = "Veracruz Llave"
                pais_origen = "México"
                calle_origen = "CARRETERA FEDERAL MÉXICO - VERACRUZ KM. 92.8"
                
                st.text_input("RFC Salida / Planta", value=rfc_origen, disabled=True)
                st.text_input("Nombre / Empresa de Salida", value=nombre_origen, disabled=True)
                st.text_input("CP Origen", value=cp_origen, disabled=True)
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    st.text_input("Colonia Origen", value=colonia_origen, disabled=True)
                    st.text_input("Municipio Origen", value=municipio_origen, disabled=True)
                with col_o2:
                    st.text_input("Estado Origen", value=estado_origen, disabled=True)
                    st.text_input("País Origen", value=pais_origen, disabled=True)
                st.text_input("Calle y Número de Salida", value=calle_origen, disabled=True)
            else:
                rfc_origen = st.text_input("RFC Salida / Planta", placeholder="RFC de origen")
                nombre_origen = st.text_input("Nombre / Empresa de Salida", placeholder="Ej. Proveedor o Bodega Alterna")
                cp_origen = st.text_input("CP Origen", max_chars=5, placeholder="Ej. 91400, 42188")
                info_o = consultar_cp_mexico(cp_origen)
                
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    colonia_origen = st.text_input("Colonia Origen", value=info_o["colonia"], placeholder="Colonia")
                    municipio_origen = st.text_input("Municipio Origen", value=info_o["municipio"], placeholder="Municipio")
                with col_o2:
                    estado_origen = st.text_input("Estado Origen", value=info_o["estado"], placeholder="Estado")
                    pais_origen = st.text_input("País Origen", value=info_o["pais"])
                    
                calle_origen = st.text_input("Calle y Número de Salida", placeholder="Ej. Carretera Principal Km 2")

            dir_origen_final = f"{calle_origen}, Col. {colonia_origen}, C.P. {cp_origen}, {municipio_origen}, {estado_origen}"

        with col_destino:
            st.markdown("#### 🛬 DESTINO")
            tipo_modo_destino = st.radio(
                "Modalidad de Destino:", 
                ["Cliente Específico (C.P. / Domicilio)", "Varios Clientes (Ruta General / Zona Libre)"], 
                index=1,
                horizontal=False, 
                key="radio_destino"
            )
            
            col_f3, col_f4 = st.columns(2)
            with col_f3:
                f_llegada_date = st.date_input("Fecha Estimada Llegada", value=ahora_mx.date())
            with col_f4:
                if "hora_llegada_input" not in st.session_state:
                    st.session_state.hora_llegada_input = "18:00"
                hora_llegada_str = st.text_input("Hora Estimada Llegada (HH:MM)", key="hora_llegada_input")

            if tipo_modo_destino == "Cliente Específico (C.P. / Domicilio)":
                rfc_destino = st.text_input("RFC Llegada / Cliente (Opcional)", placeholder="RFC de destino (Vacío si es público general)")
                nombre_destino = st.text_input("Nombre / Empresa de Llegada", placeholder="Ej. Cliente Destino")
                
                cp_destino = st.text_input("CP Destino", max_chars=5, placeholder="Ej. 54680, 91000")
                info_d = consultar_cp_mexico(cp_destino)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    colonia_destino = st.text_input("Colonia Destino", value=info_d["colonia"], placeholder="Colonia")
                    municipio_destino = st.text_input("Municipio Destino", value=info_d["municipio"], placeholder="Municipio")
                with col_d2:
                    estado_destino = st.text_input("Estado Destino", value=info_d["estado"], placeholder="Estado")
                    pais_destino = st.text_input("País Destino", value=info_d["pais"])
                    
                calle_destino = st.text_input("Calle y Número de Llegada", placeholder="Ej. Av. Principal #10")
                dir_destino_final = f"{calle_destino}, Col. {colonia_destino}, C.P. {cp_destino}, {municipio_destino}, {estado_destino}"
            else:
                rfc_destino = ""
                nombre_destino = "Ruta Varios Clientes"
                col_m_lib1, col_m_lib2 = st.columns(2)
                with col_m_lib1:
                    zona_libre_destino = st.text_input(
                        "Destinos / Zona de Reparto", 
                        value=def_ruta, 
                        key=f"ruta_zona_{nombre_chofer}", 
                        placeholder="Ej. Banderilla, Xalapa, Las Vigas"
                    )
                with col_m_lib2:
                    estado_libre_destino = st.text_input("Estado / Región", value="Veracruz", placeholder="Ej. Veracruz")
                    
                dir_destino_final = f"Ruta multi-cliente / Zona de entrega: {zona_libre_destino}"

    with st.container(border=True):
        st.subheader("6. 📦 Descripción y Claves de la Mercancía")
        if tipo_unidad == "Autotanque (Pipa)":
            st.markdown("#### ⛽ Configuración para Pipa")
            
            col_calc1, col_calc2 = st.columns(2)
            with col_calc1:
                capacidad_total_num = st.number_input(
                    "Capacidad Total de la Pipa (Litros)", 
                    min_value=0.0, 
                    value=def_capacidad_num, 
                    step=100.0,
                    key=f"cap_pipa_{nombre_chofer}"
                )
            with col_calc2:
                porcentaje_llenado = st.number_input("Porcentaje de Llenado (%)", min_value=0.0, max_value=100.0, value=70.0, step=0.5)

            volumen_calculado_lts = capacidad_total_num * (porcentaje_llenado / 100.0)
            cantidad_texto = f"{volumen_calculado_lts:,.2f} Litros (Porcentaje: {porcentaje_llenado:.1f}%)"
            st.info(f"📊 **Resultado Automático Pipa:** {cantidad_texto}")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.text_input("Cantidad Calculada", value=cantidad_texto, disabled=True)
                clave_unidad_sat = "LTR - Litros"
                peso_texto = "N/A"
            with col_m2:
                desc_mercancia = st.text_input("Descripción / Producto", value="Gas Licuado de Petróleo (Gas LP)")
                clave_prod_sat = st.text_input("Clave Producto", value="15111510 (Gas LP)")

        else:
            st.markdown("#### 🛢️ Configuración para Vehículo Repartidor (Cilindros)")
            col_cil1, col_cil2 = st.columns(2)
            with col_cil1:
                cant_cil_20 = st.number_input(
                    "Cantidad de Cilindros de 20 KG", 
                    min_value=0, 
                    value=def_cant_20, 
                    step=1,
                    key=f"cant_20_{nombre_chofer}"
                )
            with col_cil2:
                cant_cil_30 = st.number_input(
                    "Cantidad de Cilindros de 30 KG", 
                    min_value=0, 
                    value=def_cant_30, 
                    step=1,
                    key=f"cant_30_{nombre_chofer}"
                )

            total_piezas = cant_cil_20 + cant_cil_30
            peso_neto_gas = (cant_cil_20 * 20.0) + (cant_cil_30 * 30.0)
            cantidad_texto = f"{total_piezas} Piezas ({cant_cil_20} de 20kg, {cant_cil_30} de 30kg)"
            st.info(f"📊 **Total Envases:** {cantidad_texto} | **Peso Neto de Gas:** {peso_neto_gas:,.2f} KG")

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.text_input("Cantidad Calculada", value=cantidad_texto, disabled=True)
                clave_unidad_sat = "H87 - Pieza"
            with col_m2:
                desc_mercancia = st.text_input("Descripción / Producto", value="Gas Licuado de Petróleo (Gas LP en Cilindros)")
                clave_prod_sat = st.text_input("Clave Producto", value="15111510 (Gas LP)")
            with col_m3:
                peso_texto = f"{peso_neto_gas:,.2f} KG"
                st.text_input("Peso Total Neto Gas", value=peso_texto, disabled=True)

    st.markdown("---")
    
    if st.button("Generar y Registrar Carta Porte", type="primary", use_container_width=True):
        if not nombre_chofer or not num_poliza or not desc_mercancia:
            st.warning("⚠️ Por favor completa los datos obligatorios del chofer, póliza y mercancía.")
        else:
            str_salida = f"{f_salida_date.strftime('%d/%m/%Y')} {hora_salida_str}"
            str_llegada = f"{f_llegada_date.strftime('%d/%m/%Y')} {hora_llegada_str}"
            
            folio_generado = obtener_siguiente_folio_nube()

            datos_nueva_carta = {
                "folio": folio_generado,
                "nombre_emisor": nombre_emisor,
                "rfc_emisor": rfc_emisor,
                "num_permiso_sct": num_permiso_sct,
                "nombre_chofer": nombre_chofer,
                "rfc_chofer": rfc_chofer,
                "tipo_licencia": tipo_licencia,
                "num_licencia": num_licencia,
                "tipo_unidad": tipo_unidad,
                "eco_unidad": eco_unidad or "S/N",
                "placas": placas,
                "marca_modelo": marca_modelo,
                "capacidad": capacidad,
                "aseguradora": aseguradora,
                "num_poliza": num_poliza,
                "rfc_origen": rfc_origen,
                "nombre_origen": nombre_origen,
                "fecha_salida": str_salida,
                "dir_origen": dir_origen_final,
                "rfc_destino": rfc_destino,
                "nombre_destino": nombre_destino,
                "fecha_llegada": str_llegada,
                "dir_destino": dir_destino_final,
                "cantidad_mercancia": cantidad_texto,
                "clave_unidad_sat": clave_unidad_sat,
                "desc_mercancia": desc_mercancia,
                "clave_prod_sat": clave_prod_sat,
                "peso_mercancia": peso_texto,
                "fecha_registro": ahora_mx.strftime("%d/%m/%Y %H:%M")
            }

            exito = guardar_carta_en_nube(datos_nueva_carta)
            if exito:
                st.success(f"¡Carta Porte con Folio {folio_generado} generada y guardada con éxito en la nube para Naupagas!")
                st.balloons()

elif accion == "Historial de Documentos":
    st.title("📁 NAUPAGAS - Historial de Cartas Generadas")
    st.write("Consulta, filtra por fechas y administra los registros almacenados en la nube.")
    st.markdown("---")

    col_f_1, col_f_2 = st.columns(2)
    with col_f_1:
        filtro_inicio = st.date_input("Filtrar desde la fecha:", value=None)
    with col_f_2:
        filtro_fin = st.date_input("Filtrar hasta la fecha:", value=None)

    historial_nube = cargar_historial_nube()

    if not historial_nube:
        st.info("No hay cartas registradas en la base de datos para Naupagas.")
    else:
        cartas_filtradas = []
        for carta in historial_nube:
            f_reg_str = carta.get('fecha_registro', '')
            try:
                f_reg_date = datetime.strptime(f_reg_str.split()[0], "%d/%m/%Y").date()
                incluir = True
                if filtro_inicio and f_reg_date < filtro_inicio:
                    incluir = False
                if filtro_fin and f_reg_date > filtro_fin:
                    incluir = False
                if incluir:
                    cartas_filtradas.append(carta)
            except Exception:
                cartas_filtradas.append(carta)

        if not cartas_filtradas:
            st.warning("⚠️ No se encontraron cartas en el rango de fechas seleccionado.")
        else:
            st.write(f"Mostrando **{len(cartas_filtradas)}** registro(s):")
            
            for idx, carta in enumerate(cartas_filtradas):
                with st.container(border=True):
                    col_h1, col_h2, col_h3 = st.columns([2.5, 3, 2.5])
                    with col_h1:
                        st.write(f"🔢 **Folio Nube:** {carta.get('folio', 'N/A')}")
                        st.write(f"📅 **Fecha:** {carta.get('fecha_registro', 'N/A')}")
                        st.write(f"⛽ **Unidad:** {carta.get('tipo_unidad', '')} ({carta.get('eco_unidad', '')})")
                    with col_h2:
                        st.write(f"👤 **Chofer:** {carta.get('nombre_chofer', '')}")
                        st.write(f"🛣️ **Ruta:** {carta.get('nombre_origen', '')} ➔ {carta.get('nombre_destino', '')}")
                    with col_h3:
                        pdf_hist_bytes = generar_pdf(carta)
                        st.download_button(
                            label="📄 Descargar PDF",
                            data=pdf_hist_bytes,
                            file_name=f"Naupagas_Folio_{carta.get('folio', '0000001')}.pdf",
                            mime="application/pdf",
                            key=f"dl_naupagas_{idx}"
                        )
                        
                        with st.expander("🗑️ Eliminar este registro"):
                            pass_borrar = st.text_input("Contraseña de autorización", type="password", key=f"pass_del_{carta.get('id')}")
                            if st.button("Confirmar Eliminación", key=f"btn_del_{carta.get('id')}", type="primary"):
                                if pass_borrar == MASTER_PASSWORD:
                                    if eliminar_carta_nube(carta.get('id')):
                                        st.success(f"Carta Folio {carta.get('folio')} eliminada.")
                                        st.rerun()
                                    else:
                                        st.error("Error al eliminar en Supabase.")
                                else:
                                    st.error("❌ Contraseña incorrecta. No se pudo eliminar.")

elif accion == "⚙️ Administrar Catálogo":
    st.title("⚙️ NAUPAGAS - Administración de Choferes y Unidades")
    st.write("Agrega, edita o elimina choferes y unidades de la base de datos en la nube sin modificar el código.")
    st.markdown("---")

    tab_nuevo, tab_editar = st.tabs(["➕ Agregar Nuevo Operador", "✏️ Modificar / Eliminar Operador Existente"])

    with tab_nuevo:
        st.subheader("Registrar Nuevo Chofer y Unidad")
        with st.form("form_nuevo_chofer"):
            c1, c2 = st.columns(2)
            with c1:
                n_nombre = st.text_input("Nombre Completo del Chofer")
                n_rfc = st.text_input("RFC del Chofer")
                n_tipo_lic = st.selectbox("Tipo de Licencia", ["Estatal", "Federal"])
                n_num_lic = st.text_input("Número de Licencia")
                n_tipo_unidad = st.selectbox("Tipo de Unidad SAT", ["Autotanque (Pipa)", "Vehículo Repartidor (Cilindrera)"])
                n_marca = st.text_input("Marca / Modelo de la Unidad")
                n_eco = st.text_input("Número Económico")
            with c2:
                n_cap_txt = st.text_input("Capacidad Descriptiva", placeholder="Ej. 12900 Lts o 19 de 20 kg y 9 de 30 kg")
                n_cap_num = st.number_input("Capacidad Numérica (Litros - 0 si es cilindrera)", value=0.0)
                n_placas = st.text_input("Placas")
                n_aseg = st.text_input("Aseguradora", value="Qualitas")
                n_pol = st.text_input("Número de Póliza")
                n_ruta = st.text_input("Zonas de Reparto / Ruta", placeholder="Ej. Perote, Madero, Molinos")

            btn_guardar_nuevo = st.form_submit_button("Guardar Nuevo Operador en Nube", type="primary")
            if btn_guardar_nuevo:
                if not n_nombre or not n_polizas := n_pol:
                    st.warning("⚠️ Por favor completa al menos el nombre y la póliza.")
                else:
                    nuevo_registro = {
                        "nombre": n_nombre.strip().upper(),
                        "tipo": n_tipo_lic,
                        "rfc": n_rfc.strip().upper(),
                        "licencia": n_num_lic.strip().upper(),
                        "tipo_unidad_sat": n_tipo_unidad,
                        "marca": n_marca.strip().upper(),
                        "eco": n_eco.strip().upper(),
                        "capacidad_txt": n_cap_txt.strip(),
                        "capacidad_num": float(n_cap_num),
                        "cant_20": 0,
                        "cant_30": 0,
                        "placas": n_placas.strip().upper(),
                        "aseguradora": n_aseg.strip().upper(),
                        "poliza": n_pol.strip().upper(),
                        "ruta": n_ruta.strip()
                    }
                    if guardar_chofer_nube(nuevo_registro):
                        st.success(f"¡Operador {n_nombre} agregado correctamente al catálogo!")
                        st.rerun()

    with tab_editar:
        st.subheader("Editar o Dar de Baja Operadores")
        if not CATALOGO_CHOFERES_NAUPA:
            st.info("No hay operadores en el catálogo.")
        else:
            nombres_edit = [c["nombre"] for c in CATALOGO_CHOFERES_NAUPA]
            sel_edit = st.selectbox("Seleccione al operador a modificar", options=nombres_edit, key="sel_op_edit")
            datos_sel = next((c for c in CATALOGO_CHOFERES_NAUPA if c["nombre"] == sel_edit), None)

            if datos_sel:
                with st.form("form_edicion_chofer"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_nombre = st.text_input("Nombre Completo", value=datos_sel.get("nombre", ""))
                        e_rfc = st.text_input("RFC", value=datos_sel.get("rfc", ""))
                        e_tipo_lic = st.text_input("Tipo Licencia", value=datos_sel.get("tipo", ""))
                        e_num_lic = st.text_input("Número Licencia", value=datos_sel.get("licencia", ""))
                        e_eco = st.text_input("Número Económico", value=datos_sel.get("eco", ""))
                        e_marca = st.text_input("Marca / Modelo", value=datos_sel.get("marca", ""))
                    with ec2:
                        e_cap_txt = st.text_input("Capacidad Descriptiva", value=datos_sel.get("capacidad_txt", ""))
                        e_placas = st.text_input("Placas", value=datos_sel.get("placas", ""))
                        e_aseg = st.text_input("Aseguradora", value=datos_sel.get("aseguradora", ""))
                        e_pol = st.text_input("Número de Póliza", value=datos_sel.get("poliza", ""))
                        e_ruta = st.text_input("Zonas de Reparto / Ruta", value=datos_sel.get("ruta", ""))

                    col_btn_1, col_btn_2 = st.columns(2)
                    with col_btn_1:
                        btn_actualizar = st.form_submit_button("Actualizar Datos", type="primary")
                    with col_btn_2:
                        btn_borrar = st.form_submit_button("Eliminar Operador", type="secondary")

                    if btn_actualizar:
                        datos_actualizados = {
                            "nombre": e_nombre.strip().upper(),
                            "rfc": e_rfc.strip().upper(),
                            "tipo": e_tipo_lic.strip(),
                            "licencia": e_num_lic.strip().upper(),
                            "eco": e_eco.strip().upper(),
                            "marca": e_marca.strip().upper(),
                            "capacidad_txt": e_cap_txt.strip(),
                            "placas": e_placas.strip().upper(),
                            "aseguradora": e_aseg.strip().upper(),
                            "poliza": e_pol.strip().upper(),
                            "ruta": e_ruta.strip()
                        }
                        if actualizar_chofer_nube(datos_sel["id"], datos_actualizados):
                            st.success(f"¡Operador {e_nombre} actualizado con éxito!")
                            st.rerun()

                    if btn_borrar:
                        if eliminar_chofer_nube(datos_sel["id"]):
                            st.success(f"¡Operador {sel_edit} eliminado del catálogo!")
                            st.rerun()
