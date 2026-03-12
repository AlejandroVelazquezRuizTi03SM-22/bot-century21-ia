from supabase import create_client, Client
import config
import utils
from datetime import datetime
import random
import whatsapp_notifier

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
COLUMNAS_PERMITIDAS = "id,clave,nombre,municipio,colonia,precio,subtipoPropiedad,tipoOperacion,descripcion,m2T,m2C,recamaras,banios,mapa_url,latitud,longitud,url_ficha"

# ==============================================================================
# FUNCIONES VIP (ASESORES)
# ==============================================================================
def obtener_asesor_por_telefono(telefono: str):
    try:
        res = supabase.table("asesores").select("id, nombre, correo, telefono").eq("activo", True).execute()
        if res.data: return res.data[0]["nombre"]
        return None
    except Exception as e:
        print(f"[ERROR CHECK ASESOR] {e}")
        return None

def obtener_propiedades_por_asesor(nombre_asesor: str):
    try:
        print(f"\n[DB REPORTES] 1. Buscando ID para el asesor: '{nombre_asesor}'")
        asesor_res = supabase.table("asesores").select("id, nombre").ilike("nombre", f"%{nombre_asesor}%").execute()
        
        if not asesor_res.data:
            print(f"[DB REPORTES] ERROR: No existe ningún asesor llamado '{nombre_asesor}' en la tabla 'asesores'.")
            return []
            
        id_del_asesor = asesor_res.data[0]["id"]
        nombre_real = asesor_res.data[0]["nombre"]
        
        print(f"[DB REPORTES] 2. Buscando casas donde asesor_id == {id_del_asesor}")
        res = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS).eq("asesor_id", id_del_asesor).execute()
        
        if not res.data:
            print(f"[DB REPORTES] ERROR: El ID {id_del_asesor} no tiene casas asignadas.")
            return []
            
        print(f"[DB REPORTES] EXITO: Se encontraron {len(res.data)} propiedades para {nombre_real}.")
        return res.data
    except Exception as e:
        print(f"[ERROR REPORTES OCURRIDO] {e}")
        return []

# ==============================================================================
# FUNCIONES DE CLIENTES (CRM Y TIMESTAMPS)
# ==============================================================================
def obtener_cliente(telefono: str):
    try:
        res = supabase.table("clientes").select("*").eq("telefono", telefono).execute()
        if res.data: return res.data[0]
        return None
    except Exception as e:
        print(f"[ERROR DB OBTENER CLIENTE] {e}")
        return None

async def guardar_cliente(mensaje_usuario, respuesta_bot, telefono, datos_extraidos, cliente_existente=None):
    try:
        ahora = datetime.now()
        fecha_str = ahora.strftime("%Y-%m-%d") 
        hora_str = ahora.strftime("%H:%M:%S")
        hora_corta = ahora.strftime("%H:%M") # Formato visual [14:30]
        
        observaciones_actuales = cliente_existente.get("observaciones_generales", "") if cliente_existente else ""
        prefijo = "\n" if observaciones_actuales else ""
        
        # INYECCIÓN DE TIMESTAMP EN EL HISTORIAL
        nuevo_historial = f"{observaciones_actuales}{prefijo}[{hora_corta}] Cliente: {mensaje_usuario}\n[{hora_corta}] Bot: {respuesta_bot}"
        
        datos_guardar = {
            "telefono": telefono, 
            "observaciones_generales": nuevo_historial,
            "fecha_contacto": fecha_str,
            "hora_contacto": hora_str
        }

        if datos_extraidos.get("nombre_cliente"): datos_guardar["nombre_cliente"] = datos_extraidos["nombre_cliente"]
        if datos_extraidos.get("tipo_inmueble"): datos_guardar["tipo_inmueble"] = datos_extraidos["tipo_inmueble"]
        if datos_extraidos.get("zona_municipio"): datos_guardar["zona_municipio"] = datos_extraidos["zona_municipio"]
        if datos_extraidos.get("presupuesto"): datos_guardar["presupuesto"] = str(datos_extraidos["presupuesto"])
        if datos_extraidos.get("origen"): datos_guardar["origen"] = datos_extraidos["origen"]
        if datos_extraidos.get("clave_propiedad"): datos_guardar["id_propiedad_opcional"] = datos_extraidos["clave_propiedad"]

        if cliente_existente:
            supabase.table("clientes").update(datos_guardar).eq("telefono", telefono).execute()
        else:
            supabase.table("clientes").insert(datos_guardar).execute()
    except Exception as e:
        print(f"[ERROR DB GUARDAR CLIENTE] {e}")

# ==============================================================================
# FUNCIONES DE PROPIEDADES
# ==============================================================================
def buscar_por_clave(clave):
    try:
        clave_limpia = str(clave).strip()
        res = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS).or_(f"clave.eq.{clave_limpia},id.eq.{utils.limpiar_numero(clave_limpia)}").execute()
        return res.data
    except Exception as e:
        print(f"[ERROR BUSQUEDA CLAVE] {e}")
        return []

def buscar_propiedades(tipo_inmueble, tipo_operacion, zona, presupuesto, mostrar_mix_general=False):
    try:
        if not tipo_operacion:
            if presupuesto and presupuesto > 150000: tipo_operacion = "Venta"
            elif presupuesto and presupuesto <= 150000: tipo_operacion = "Renta"
            else: tipo_operacion = "Venta"

        if not presupuesto:
            presupuesto_busqueda = 1000000000
            orden_descendente = False  
        else:
            presupuesto_busqueda = presupuesto * 1.2 
            orden_descendente = True   

        query = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
        if tipo_operacion: query = query.ilike("tipoOperacion", f"%{tipo_operacion}%")
        if tipo_inmueble: query = query.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%") 
        
        if zona and zona.lower() != "sugerencias":
            zona_busqueda = f"municipio.ilike.*{zona}*,colonia.ilike.*{zona}*,nombre.ilike.*{zona}*"
            query = query.or_(zona_busqueda)

        query = query.lte("precio", presupuesto_busqueda).order("precio", desc=orden_descendente)
        res = query.execute()
        propiedades = res.data

        if not propiedades:
            print("[DB] Búsqueda 1 vacía. Intentando Fase 2 (Sin Zona)...")
            query_f2 = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
            if tipo_operacion: query_f2 = query_f2.ilike("tipoOperacion", f"%{tipo_operacion}%")
            if tipo_inmueble: query_f2 = query_f2.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%")
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
        pass

def obtener_asesor_aleatorio():
    try:
        res = supabase.table("asesores").select("id, nombre, correo, telefono").eq("activo", True).execute()
        asesores_activos = res.data
        if not asesores_activos: return None
        return random.choice(asesores_activos)
    except Exception as e:
        print(f"[ERROR DB OBTENER ASESOR] {e}")
    return None