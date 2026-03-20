import re
import os
import requests
from openai import OpenAI
import config

# Inicializamos el cliente oficial de OpenAI para usar Whisper
cliente_openai = OpenAI(api_key=config.OPENAI_API_KEY)

def limpiar_texto(valor):
    if not valor: return None
    valor = str(valor).strip()
    if valor.lower() in ["none", "null", "", "desconocido", "no definido", "sugerencias", "cliente"]:
        return None 
    return valor

def limpiar_numero(valor):
    if not valor: return 0
    limpio = re.sub(r"[^\d]", "", str(valor))
    return int(limpio) if limpio else 0

def detectar_intencion_ver_propiedades(texto: str) -> bool:
    # Agregamos términos de campañas, zonas y formas coloquiales de pedir informes
    claves = [
        "ver", "mostrar", "qué tienes", "que tienes", "opciones", 
        "inventario", "catálogo", "catalogo", "info", "información", 
        "precio", "fotos", "enviar", "mandame", "interesa", 
        "busco", "quiero", "rentar", "comprar", "venta",
        "tienes casas", "tienen depas", "propiedad", "inmueble",
        "fraccionamiento", "colonia", "zona", "ubicación", "ubicacion",
        "anuncio", "publicación", "publicacion", "club de golf", "campestre", "san gil"
    ]
    texto_lower = texto.lower()
    return any(c in texto_lower for c in claves)

# ==============================================================================
# LÓGICA DE AUDIO (WHISPER) CON AUTENTICACIÓN DE TWILIO 🎤🔐
# ==============================================================================
def descargar_y_transcribir_audio(media_url: str) -> str:
    """Descarga el audio de Twilio (con autenticación) y lo transcribe a texto con Whisper"""
    try:
        # 1. Descargar el archivo de Twilio USANDO TUS CREDENCIALES 🔐
        respuesta = requests.get(
            media_url, 
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        )
        respuesta.raise_for_status() # Lanza error si algo sale mal (ej. Error 401)

        # 2. Guardarlo temporalmente
        archivo_temporal = "audio_temporal.ogg"
        with open(archivo_temporal, "wb") as f:
            f.write(respuesta.content)

        # 3. Enviarlo a OpenAI (Whisper) para transcribir
        with open(archivo_temporal, "rb") as archivo_audio:
            transcripcion = cliente_openai.audio.transcriptions.create(
                model="whisper-1",
                file=archivo_audio
            )

        # 4. Borrar el archivo temporal para mantener limpio el servidor
        if os.path.exists(archivo_temporal):
            os.remove(archivo_temporal)

        return transcripcion.text

    except Exception as e:
        print(f"[ERROR AUDIO] No se pudo transcribir: {e}")
        return "No pude entender el audio."