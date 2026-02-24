from supabase import create_client, Client
import config
import utils

# Inicializar cliente de Supabase
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# 🛡️ SEGURIDAD: LISTA BLANCA DE COLUMNAS
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

def buscar_propiedades(tipo_inmueble, zona, presupuesto, mostrar_mix_general=False):
    try:
        query = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS)

        if tipo_inmueble: query = query.ilike("subtipoPropiedad", f"%{tipo_inmueble}%")

        if zona and zona.lower() != "sugerencias":
            zona_busqueda = f"municipio.ilike.*{zona}*,colonia.ilike.*{zona}*,nombre.ilike.*{zona}*"
            query = query.or_(zona_busqueda)

        # 🧠 PRESUPUESTO: Funciona como TOPE y ordena de mayor a menor
        if presupuesto:
            max_p = presupuesto * 1.2
            query = query.lte("precio", max_p).order("precio", desc=True)

        res = query.execute()
        propiedades = res.data

        # 🚨 RED DE SEGURIDAD
        if not propiedades:
            print(f"[DB] Búsqueda específica vacía. Activando Red de Seguridad.")
            query_mix = supabase.table("propiedades").select(COLUMNAS_PERMITIDAS).limit(4)
            if presupuesto:
                query_mix = query_mix.lte("precio", presupuesto * 1.2).order("precio", desc=True)
            res_mix = query_mix.execute()
            propiedades = res_mix.data
        
        return propiedades[:4]
    except Exception as e:
        print(f"[ERROR DB BUSQUEDA] {e}")
        return []

def guardar_mapa_generado(id_propiedad, url_mapa):
    try:
        supabase.table("propiedades").update({"mapa_url": url_mapa}).eq("id", id_propiedad).execute()
    except Exception as e:
        print(f"[ERROR GUARDANDO MAPA] {e}")