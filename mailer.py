import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_notificacion_asesor(datos_cliente, historial_completo, correo_destino="alfredoferrusca885@gmail.com", nombre_asesor="Equipo Century 21"):
    # CONFIGURACIÓN
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_PASS = os.getenv("GMAIL_PASS")
    EMAIL_DESTINO = correo_destino

    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = EMAIL_DESTINO
        # 🚨 CAMBIO 1: Agregamos el nombre del asesor al ASUNTO del correo
        msg['Subject'] = f"🔴 NUEVO LEAD para {nombre_asesor}: {datos_cliente.get('nombre', 'Cliente')} 🏠"

        # Limpiamos el número para el link de WhatsApp (quitamos 'whatsapp:' y el '+')
        telefono_raw = datos_cliente.get('telefono', '')
        telefono_limpio = re.sub(r'\D', '', telefono_raw) # Deja solo los números

        # PLANTILLA HTML CON DISEÑO CENTURY 21
        cuerpo_html = f"""
        <html>
          <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f5f7; padding: 20px; margin: 0;">
            
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
              
              <div style="background-color: #212121; color: #BE9A5A; padding: 25px; text-align: center; border-bottom: 4px solid #BE9A5A;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px;">CENTURY 21 Diamante</h1>
                <p style="margin: 5px 0 0 0; color: #ffffff; font-size: 14px; font-weight: 300;">Notificación de Asistente IA</p>
              </div>

              <div style="padding: 30px;">
                <h2 style="color: #333333; margin-top: 0; border-bottom: 2px solid #eeeeee; padding-bottom: 10px; font-size: 18px;">
                  📋 Ficha del Prospecto
                </h2>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                  <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;"><strong>👔 Asesor Asignado:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #BE9A5A; font-weight: bold; text-align: right; font-size: 16px;">{nombre_asesor}</td>
                  </tr>
                  <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;"><strong>👤 Nombre del cliente:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #222; font-weight: bold; text-align: right;">{datos_cliente.get('nombre')}</td>
                  </tr>
                  <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;"><strong>📱 Teléfono:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #222; font-weight: bold; text-align: right;">{datos_cliente.get('telefono')}</td>
                  </tr>
                  <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;"><strong>📍 Zona de interés:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #222; font-weight: bold; text-align: right;">{datos_cliente.get('zona')}</td>
                  </tr>
                  <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;"><strong>💰 Presupuesto:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #222; font-weight: bold; text-align: right;">${datos_cliente.get('presupuesto')}</td>
                  </tr>
                </table>

                <h2 style="color: #333333; margin-top: 0; border-bottom: 2px solid #eeeeee; padding-bottom: 10px; font-size: 18px;">
                  💬 Historial de Conversación
                </h2>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #BE9A5A; font-size: 14px; color: #444444; line-height: 1.6; white-space: pre-wrap; border-radius: 0 4px 4px 0;">
{historial_completo}
                </div>

                <div style="text-align: center; margin-top: 35px; margin-bottom: 10px;">
                  <a href="https://wa.me/{telefono_limpio}" style="background-color: #25D366; color: white; padding: 14px 28px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 2px 5px rgba(37, 211, 102, 0.4);">
                    Abrir chat en WhatsApp
                  </a>
                </div>
                
              </div>
              
              <div style="background-color: #f4f5f7; color: #888888; text-align: center; padding: 15px; font-size: 12px; border-top: 1px solid #eeeeee;">
                Este mensaje fue generado automáticamente por la arquitectura RAG del chatbot.
              </div>

            </div>
          </body>
        </html>
        """
      
        msg.attach(MIMEText(cuerpo_html, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("[MAILER] Correo HTML enviado exitosamente.")
    except Exception as e:
        print(f"[MAILER ERROR] {e}")