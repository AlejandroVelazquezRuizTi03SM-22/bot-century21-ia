from twilio.rest import Client
import config

# ---------------------------------------------------------
# CONFIGURACIÓN DE TWILIO (Tus credenciales de la consola)
# ---------------------------------------------------------
# CORRECTO: Usamos el punto (.) para llamar a la variable que vive dentro de config.py
TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
TWILIO_NUMERO_BOT = "whatsapp:+14155238886" # El número de tu Sandbox o el Oficial

# Inicializamos el cliente de Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_alerta_asesor(numero_asesor, datos_cliente, resumen_ejecutivo):
    # Limpiamos el número para generar el enlace clicable de wa.me
    telefono_limpio = datos_cliente['telefono'].replace('whatsapp:+', '')
    
    mensaje_texto = f"""🚨 *¡NUEVO LEAD DE CENTURY 21 Diamante!* 🚨

👤 *Cliente:* {datos_cliente['nombre']}
📞 *Teléfono:* {datos_cliente['telefono']}

📋 *Resumen de la IA:*
{resumen_ejecutivo}

📲 *Contactar ahora:* Haz clic aquí para enviarle un mensaje rápido al cliente: https://wa.me/{telefono_limpio}

¡Éxito en tu cierre! 🤝"""

    try:
        # Ejecutamos el envío del mensaje
        message = twilio_client.messages.create(
            from_=TWILIO_NUMERO_BOT,
            body=mensaje_texto,
            to=numero_asesor
        )
        print(f"[WHATSAPP NOTIFIER] Alerta enviada correctamente al asesor. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[ERROR WHATSAPP NOTIFIER] No se pudo enviar la alerta: {e}")
        return False