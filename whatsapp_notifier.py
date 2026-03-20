import config
from twilio.rest import Client

# =========================================================
# CONFIGURACIÓN DE TWILIO
# =========================================================
# Inicializamos el cliente de Twilio una sola vez
client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

# Tus números oficiales
NUMERO_TWILIO = "whatsapp:+5214271097523" 
NUMERO_OFICINA = "whatsapp:+5214276880588" 

def enviar_alerta_asesor(numero_asesor, datos_cliente, resumen_ai, nombre_asesor):
    # 1. Extraemos los datos del cliente
    cliente_nombre = datos_cliente.get('nombre', 'Cliente sin nombre')
    cliente_telefono = datos_cliente.get('telefono', 'Sin teléfono')
    zona = datos_cliente.get('zona', 'No especificada')
    presupuesto = datos_cliente.get('presupuesto', 'No especificado')
    zona_presupuesto = f"{zona} / {presupuesto}"

    # 2. CONSTRUIMOS LA PLANTILLA EXACTA (Aprobada por Meta)
    mensaje_plantilla = f"""🚨 *NUEVO LEAD CENTURY 21 DIAMANTE* 🚨

Hola {nombre_asesor}, el asistente virtual te ha asignado un nuevo prospecto.

👤 *Cliente:* {cliente_nombre}
📱 *Teléfono:* {cliente_telefono}
📍 *Zona/Presupuesto:* {zona_presupuesto}

📝 *Resumen de la solicitud:*
{resumen_ai}

Por favor, contacta a este prospecto lo antes posible. ¡Mucho éxito! 💎"""

    try:
        # 3. Enviar mensaje al Asesor
        if numero_asesor:
            # 🛡️ BLINDAJE: Limpiamos el número para evitar errores de mayúsculas ("WhatsApp:") o espacios
            numero_limpio = numero_asesor.lower().replace("whatsapp:", "").strip()
            numero_formateado = f"whatsapp:{numero_limpio}"
            
            client.messages.create(
                from_=NUMERO_TWILIO,
                body=mensaje_plantilla,
                to=numero_formateado
            )
            print(f"[ALERTA ENVIADA] Lead enviado a {nombre_asesor} con plantilla oficial.")
        
        # 4. Enviar copia a la Oficina
        client.messages.create(
            from_=NUMERO_TWILIO,
            body=mensaje_plantilla,
            to=NUMERO_OFICINA
        )
        
    except Exception as e:
        print(f"[ERROR TWILIO PLANTILLA] {e}")