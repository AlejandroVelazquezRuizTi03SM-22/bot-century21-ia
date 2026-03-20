from supabase import create_client, Client
import config
import utils
from datetime import datetime
import random
import whatsapp_notifier

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
COLUMNAS_PERMITIDAS = "id,clave,nombre,municipio,colonia,precio,subtipoPropiedad,tipoOperacion,descripcion,m2T," \
                        "m2C,recamaras,banios,mapa_url,latitud,longitud,url_ficha"

# ==============================================================================
# FUNCIONES DE CLIENTES (CRM)
# ==============================================================================
def obtener_cliente(telefono: str):
    try:
        res = supabase.table("clientes").select("*").eq("telefono", telefono).execute()
        if res.data: return res.data[0]
        return None
    except Exception as e:
        print(f"[ERROR DB OBTENER CLIENTE] {e}")
        return None

async def guardar_cliente(mensaje_usuario, respuesta_bot, telefono, datos_extraidos, cliente_existente=None, asesor_asignado_nombre=None):
    try:
        observaciones_actuales = cliente_existente.get("observaciones_generales", "") if cliente_existente else ""
        nuevo_historial = f"{observaciones_actuales}\nCliente: {mensaje_usuario}\nBot: {respuesta_bot}"
        
        ahora = datetime.now()
        datos_guardar = {
            "telefono": telefono, 
            "observaciones_generales": nuevo_historial,
            "fecha_contacto": ahora.strftime("%Y-%m-%d"),
            "hora_contacto": ahora.strftime("%H:%M:%S")
        }

        if datos_extraidos.get("nombre_cliente"): datos_guardar["nombre_cliente"] = datos_extraidos["nombre_cliente"]
        
        if datos_extraidos.get("tipo_inmueble"): datos_guardar["tipo_inmueble"] = datos_extraidos["tipo_inmueble"]
        if datos_extraidos.get("zona_municipio"): datos_guardar["zona_municipio"] = datos_extraidos["zona_municipio"]
        if datos_extraidos.get("presupuesto"): datos_guardar["presupuesto"] = str(datos_extraidos["presupuesto"])
        if datos_extraidos.get("origen"): datos_guardar["origen"] = datos_extraidos["origen"]
        if datos_extraidos.get("clave_propiedad"): datos_guardar["id_propiedad_opcional"] = datos_extraidos["clave_propiedad"]

        if asesor_asignado_nombre: datos_guardar["seguimiento"] = asesor_asignado_nombre

        if cliente_existente:
            supabase.table("clientes").update(datos_guardar).eq("telefono", telefono).execute()
        else:
            supabase.table("clientes").insert(datos_guardar).execute()
    except Exception as e:
        print(f"[ERROR DB GUARDAR CLIENTE] {e}")

# ==============================================================================
# FUNCIONES DE PROPIEDADES (INVENTARIO Y MAPAS)
# ==============================================================================
def buscar_por_clave(clave):
    try:
        clave_limpia = str(clave).strip()
        res = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS).or_(f"clave.eq.{clave_limpia},id.eq.{utils.limpiar_numero(clave_limpia)}").execute()
        return res.data
    except Exception as e:
        print(f"[ERROR BUSQUEDA CLAVE] {e}")
        return []

def buscar_propiedades(tipo_inmueble, tipo_operacion, zona, presupuesto, mostrar_mix_general=False, tipo_credito=None):
    """Búsqueda literal: Obedece exactamente el tipo de operación sin hacer suposiciones por precio."""
    try:
     
        if not presupuesto:
            presupuesto_busqueda = 1000000000
            orden_descendente = False  
        else:
            presupuesto_busqueda = presupuesto * 1.2 
            orden_descendente = True   

        # =========================================================
        # CONSTRUCCIÓN DE LA QUERY BASE
        # =========================================================
        query = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
        
        # CANDADO ESTRICTO DE OPERACIÓN: Solo filtra si la IA detectó "Venta" o "Renta"
        if tipo_operacion: 
            query = query.ilike("tipoOperacion", f"%{tipo_operacion}%")
            
        if tipo_inmueble: 
            query = query.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%") 
        
        # 💳 CANDADO DE CRÉDITO (Corregido con comodín %)
        if tipo_credito == "infonavit":
            query = query.ilike("descripcion", "%infonavit%")
        elif tipo_credito == "fovissste":
            query = query.ilike("descripcion", "%fovissste%")
        elif tipo_credito == "bancario":
            query = query.or_("descripcion.ilike.%bancario%,descripcion.ilike.%credito%,descripcion.ilike.%crédito%")
        elif tipo_credito == "general":
            query = query.or_("descripcion.ilike.%infonavit%,descripcion.ilike.%fovissste%,descripcion.ilike.%bancario%,descripcion.ilike.%credito%,descripcion.ilike.%crédito%")

        # =========================================================
        # 🌟 FILTRO DE ZONA (BÚSQUEDA PROFUNDA: Municipio, Colonia, Nombre y Descripción)
        # =========================================================
        if zona and zona.lower() != "sugerencias":
            zona_limpia = str(zona).strip()
            # Le pedimos que busque esa frase exacta en cualquiera de estas 4 columnas
            zona_busqueda = f"municipio.ilike.%{zona_limpia}%,colonia.ilike.%{zona_limpia}%,nombre.ilike.%{zona_limpia}%,descripcion.ilike.%{zona_limpia}%"
            query = query.or_(zona_busqueda)

        query = query.lte("precio", presupuesto_busqueda).order("precio", desc=orden_descendente)
        res = query.execute()
        propiedades = res.data

        # FASE 2: BÚSQUEDA FLEXIBLE (Mismos candados, pero le perdonamos la Zona para que no se trabe)
        if not propiedades:
            print("[DB] Búsqueda 1 vacía. Intentando Fase 2 (Sin Zona)...")
            query_f2 = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
            
            if tipo_operacion: query_f2 = query_f2.ilike("tipoOperacion", f"%{tipo_operacion}%")
            if tipo_inmueble: query_f2 = query_f2.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%")
            
            # (Corregido con comodín %)
            if tipo_credito == "infonavit": query_f2 = query_f2.ilike("descripcion", "%infonavit%")
            elif tipo_credito == "fovissste": query_f2 = query_f2.ilike("descripcion", "%fovissste%")
            elif tipo_credito == "bancario": query_f2 = query_f2.or_("descripcion.ilike.%bancario%,descripcion.ilike.%credito%,descripcion.ilike.%crédito%")
            elif tipo_credito == "general": query_f2 = query_f2.or_("descripcion.ilike.%infonavit%,descripcion.ilike.%fovissste%,descripcion.ilike.%bancario%,descripcion.ilike.%credito%,descripcion.ilike.%crédito%")
            
            query_f2 = query_f2.lte("precio", presupuesto_busqueda).order("precio", desc=orden_descendente)
            res_f2 = query_f2.execute()
            propiedades = res_f2.data

        return propiedades[:4] if propiedades else []
    except Exception as e:
        print(f"[ERROR DB BUSQUEDA] {e}")
        return []

def guardar_mapa_generado(id_propiedad, url_mapa):
    try:
        supabase.table("propiedades").update({"mapa_url": url_mapa}).eq("id", id_propiedad).execute()
    except Exception as e:
        print(f"[ERROR GUARDANDO MAPA] {e}")

def obtener_asesor_aleatorio():
    try:
        res = supabase.table("asesores").select("id, nombre, correo, telefono").eq("activo", True).execute()
        asesores_activos = res.data

        if not asesores_activos:
            print("[ALERTA] No hay ningún asesor con activo=TRUE en Supabase.")
            return None
        asesor_ganador = random.choice(asesores_activos)
        print(f"[ASIGNACIÓM] La ruleta eligio a: {asesor_ganador['nombre']} ({asesor_ganador['correo']})")

        return asesor_ganador
    except Exception as e:
        print(f"[ERROR DB OBTENER ASESOR] {e}")
    return None