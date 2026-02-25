from supabase import create_client, Client
import config
import utils

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
COLUMNAS_PERMITIDAS = "id,clave,nombre,municipio,colonia,precio,subtipoPropiedad,tipoOperacion,descripcion,m2T,m2C,recamaras,banios,mapa_url,latitud,longitud"

# ==============================================================================
# FUNCIONES VIP (ASESORES)
# ==============================================================================
def obtener_asesor_por_telefono(telefono: str):
    try:
        res = supabase.table("asesores").select("nombre").eq("telefono", telefono).execute()
        if res.data: return res.data[0]["nombre"]
        return None
    except Exception as e:
        print(f"[ERROR CHECK ASESOR] {e}")
        return None

def obtener_propiedades_por_asesor(nombre_asesor: str):
    try:
        res = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS).ilike("nombre", f"%{nombre_asesor}%").execute()
        return res.data
    except Exception as e:
        print(f"[ERROR REPORTES] {e}")
        return []

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

async def guardar_cliente(mensaje_usuario, respuesta_bot, telefono, datos_extraidos, cliente_existente=None):
    try:
        observaciones_actuales = cliente_existente.get("observaciones_generales", "") if cliente_existente else ""
        nuevo_historial = f"{observaciones_actuales}\nCliente: {mensaje_usuario}\nBot: {respuesta_bot}"
        
        datos_guardar = {"telefono": telefono, "observaciones_generales": nuevo_historial}

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

def buscar_propiedades(tipo_inmueble, tipo_operacion, zona, presupuesto, mostrar_mix_general=False):
    """Búsqueda Escalonada: De estricta a flexible para nunca dejar la lista vacía."""
    try:
        # FASE 1: BÚSQUEDA IDEAL
        query = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
        if tipo_operacion: query = query.ilike("tipoOperacion", f"%{tipo_operacion}%")
        if tipo_inmueble: query = query.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%") 
        
        if zona and zona.lower() != "sugerencias":
            zona_busqueda = f"municipio.ilike.*{zona}*,colonia.ilike.*{zona}*,nombre.ilike.*{zona}*"
            query = query.or_(zona_busqueda)

        if presupuesto: query = query.lte("precio", presupuesto * 1.2).order("precio", desc=True)

        res = query.execute()
        propiedades = res.data

        # FASE 2: BÚSQUEDA FLEXIBLE (Sin Zona)
        if not propiedades:
            print("[DB] Búsqueda 1 vacía. Intentando Fase 2 (Sin Zona)...")
            query_f2 = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
            if tipo_operacion: query_f2 = query_f2.ilike("tipoOperacion", f"%{tipo_operacion}%")
            if tipo_inmueble: query_f2 = query_f2.ilike("subtipoPropiedad", f"%{tipo_inmueble[:4]}%")
            if presupuesto: query_f2 = query_f2.lte("precio", presupuesto * 1.2).order("precio", desc=True)
            res_f2 = query_f2.execute()
            propiedades = res_f2.data

        # FASE 3: MODO SUPERVIVENCIA (Solo Operación y Presupuesto)
        if not propiedades:
            print("[DB] Búsqueda 2 vacía. Intentando Fase 3 (Modo Supervivencia)...")
            query_f3 = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)
            if tipo_operacion: query_f3 = query_f3.ilike("tipoOperacion", f"%{tipo_operacion}%")
            if presupuesto: query_f3 = query_f3.lte("precio", presupuesto * 1.2).order("precio", desc=True)
            if not presupuesto and not tipo_operacion: query_f3 = query_f3.order("id", desc=True)
            res_f3 = query_f3.execute()
            propiedades = res_f3.data
        
        return propiedades[:4] if propiedades else []
    except Exception as e:
        print(f"[ERROR DB BUSQUEDA] {e}")
        return []

def guardar_mapa_generado(id_propiedad, url_mapa):
    try:
        supabase.table("propiedades").update({"mapa_url": url_mapa}).eq("id", id_propiedad).execute()
    except Exception as e:
        print(f"[ERROR GUARDANDO MAPA] {e}")