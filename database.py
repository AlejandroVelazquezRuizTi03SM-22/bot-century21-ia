from supabase import create_client, Client
import config
import utils

# Inicializar cliente de Supabase
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def obtener_cliente(telefono: str):
    """Busca si el cliente ya existe por su teléfono"""
    try:
        res = supabase.table("clientes").select("*").eq("telefono", telefono).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        print(f"[ERROR DB OBTENER CLIENTE] {e}")
        return None

async def guardar_cliente(mensaje_usuario, respuesta_bot, telefono, datos_extraidos, cliente_existente=None):
    """Guarda la interacción y actualiza el perfil del cliente con los nombres EXACTOS de tu tabla"""
    try:
        observaciones_actuales = ""
        if cliente_existente and cliente_existente.get("observaciones_generales"):
            observaciones_actuales = cliente_existente["observaciones_generales"]

        # 1. Preparamos el historial de chat
        nuevo_historial = f"{observaciones_actuales}\nCliente: {mensaje_usuario}\nBot: {respuesta_bot}"
        
        # 2. Datos base (Siempre se actualizan/insertan)
        datos_guardar = {
            "telefono": telefono,
            "observaciones_generales": nuevo_historial,
            # Si es nuevo, ponemos fecha/hora por default (Supabase lo hace, pero aseguramos)
            # No enviamos fecha_contacto ni hora_contacto para dejar que el DEFAULT de SQL funcione
        }

        # 3. Mapeo de Datos IA -> Tus Columnas SQL Exactas 🗺️
        # Aquí estaba el error antes. Ahora usamos tus nombres correctos:
        
        if datos_extraidos.get("nombre_cliente"): 
            datos_guardar["nombre_cliente"] = datos_extraidos["nombre_cliente"] # Antes decía "nombre"
            
        if datos_extraidos.get("tipo_inmueble"): 
            datos_guardar["tipo_inmueble"] = datos_extraidos["tipo_inmueble"]   # Antes decía "tipo_interes"
            
        if datos_extraidos.get("zona_municipio"): 
            datos_guardar["zona_municipio"] = datos_extraidos["zona_municipio"] # Antes decía "zona_interes"
            
        if datos_extraidos.get("presupuesto"): 
            datos_guardar["presupuesto"] = str(datos_extraidos["presupuesto"])  # Tu tabla pide TEXT, lo convertimos a string
            
        if datos_extraidos.get("origen"): 
            datos_guardar["origen"] = datos_extraidos["origen"]
            
        if datos_extraidos.get("clave_propiedad"):
            datos_guardar["id_propiedad_opcional"] = datos_extraidos["clave_propiedad"] # Mapeamos ID a tu columna

        # 4. Ejecutar Update o Insert
        if cliente_existente:
            # Si ya existe, actualizamos solo lo nuevo
            datos_guardar["ultima_interaccion"] = "now()" # Si tienes esta columna, si no, bórrala
            supabase.table("clientes").update(datos_guardar).eq("telefono", telefono).execute()
        else:
            # Si es nuevo, insertamos
            supabase.table("clientes").insert(datos_guardar).execute()
            
    except Exception as e:
        print(f"[ERROR DB GUARDAR CLIENTE] {e}")

# ==============================================================================
# FUNCIONES DE BÚSQUEDA DE PROPIEDADES (Se mantienen igual que antes)
# ==============================================================================

def buscar_por_clave(clave):
    try:
        clave_limpia = str(clave).strip()
        res = supabase.table("propiedades").select("*").or_(f"clave.eq.{clave_limpia},id.eq.{utils.limpiar_numero(clave_limpia)}").execute()
        return res.data
    except Exception as e:
        print(f"[ERROR BUSQUEDA CLAVE] {e}")
        return []

def buscar_propiedades(tipo_inmueble, zona, presupuesto, mostrar_mix_general=False):
    try:
        # Buscamos propiedades "enPromocion" como dice tu Excel
        query = supabase.table("propiedades").select("*").ilike("status", "%Promocion%")

        # Filtro: Tipo de Inmueble (Respetando mayúscula de tu Excel)
        if tipo_inmueble:
            query = query.ilike("subtipoPropiedad", f"%{tipo_inmueble}%")

        # Filtro: Zona
        if zona and zona.lower() != "sugerencias":
            query = query.ilike("municipio", f"%{zona}%")

        # Filtro: Presupuesto (+/- 20%)
        if presupuesto:
            min_p = presupuesto * 0.8
            max_p = presupuesto * 1.2
            query = query.gte("precio", min_p).lte("precio", max_p)

        res = query.execute()
        propiedades = res.data

        # Mix si no hay resultados
        if not propiedades and mostrar_mix_general:
            res_mix = supabase.table("propiedades").select("*").ilike("status", "%Promocion%").limit(3).execute()
            propiedades = res_mix.data

        return propiedades[:4]

    except Exception as e:
        print(f"[ERROR DB BUSQUEDA] {e}")
        return []