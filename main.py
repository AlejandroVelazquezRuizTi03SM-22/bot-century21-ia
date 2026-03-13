import os
import json
import re
import io
import csv
from datetime import datetime
from fastapi import FastAPI, Form, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from twilio.rest import Client
import config
import database
import agent
import utils
import mailer
import whatsapp_notifier

app = FastAPI()

# ==============================================================================
# MODELOS DE DATOS (DASHBOARD)
# ==============================================================================
class ToggleRequest(BaseModel):
    estado: bool

class MensajeAsesorRequest(BaseModel):
    mensaje: str

class ToggleAsesorRequest(BaseModel):
    estado: bool

# ==============================================================================
# ENDPOINT PRINCIPAL: WHATSAPP BOT
# ==============================================================================
@app.post("/whatsapp")
async def whatsapp_reply(
    From: str = Form(...),
    Body: str = Form(default=""),               
    NumMedia: str = Form(default="0"),          
    MediaUrl0: str = Form(default=""),          
    MediaContentType0: str = Form(default="")   
):
    if NumMedia != "0" and "audio" in MediaContentType0:
        texto_transcrito = utils.descargar_y_transcribir_audio(MediaUrl0)
        Body = texto_transcrito

    print(f"\n[MENSAJE] {From} -> {Body}")

    # ==============================================================================
    # MODULO VIP (ASESORES)
    # ==============================================================================
    nombre_asesor_auth = database.obtener_asesor_por_telefono(From)
    if nombre_asesor_auth:
        body_lower = Body.lower()
        
        comandos_vip = ["/reporte", "/exclusivas", "/inventario", "#reporte", "#inventario"]
        if any(comando in body_lower for comando in comandos_vip):
            patron = r'(?:/reporte|/exclusivas|/inventario)\s+(?:de\s+|del\s+)?(?:la\s+|el\s+)?(?:asesora\s+|asesor\s+)?([a-zA-ZáéíóúÁÉÍÓÚñÑ]+)'
            match = re.search(patron, body_lower)
            
            if match:
                asesor_objetivo = match.group(1).capitalize() 
            else:
                asesor_objetivo = nombre_asesor_auth 
            
            base_url = "https://perceivable-mi-nonadjacently.ngrok-free.dev" 
            link_descarga = f"{base_url}/descargar/{asesor_objetivo.replace(' ', '%20')}"
            
            mensaje_vip = (
                f"Acceso Autorizado\n"
                f"Hola {nombre_asesor_auth}.\n\n"
                f"Aquí tienes el reporte de exclusivas de {asesor_objetivo}:\n"
                f"{link_descarga}\n\n"
                f"¡Éxito en tus cierres!"
            )
            
            print(f"\n[SEGURIDAD] Número autorizado perteneciente a: {nombre_asesor_auth}")
            print(f"[VIP MODO ACTIVADO] Generando reporte para: {asesor_objetivo}")
            
            xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{mensaje_vip}</Message></Response>"""
            return Response(content=xml.strip(), media_type="text/xml")

    # ==============================================================================
    # SILENCIADOR MANUAL DEL BOT (HUMAN IN THE LOOP) Y ACTUALIZACIÓN DE HORA
    # ==============================================================================
    cliente_db = database.obtener_cliente(From)
    bot_activo = cliente_db.get("bot_encendido", True) if cliente_db else True

    if not bot_activo:
        print(f"[BOT PAUSADO] Mensaje recibido de {From}. Esperando intervención humana.")
        
        ahora = datetime.now()
        hora_corta = ahora.strftime("%H:%M")
        historial_actual = cliente_db.get("observaciones_generales") or ""
        prefijo = "\n" if historial_actual else ""
        nuevo_historial = f"{historial_actual}{prefijo}[{hora_corta}] Cliente: {Body}"
        
        # Guardamos el mensaje, lo marcamos como NO LEÍDO y actualizamos la hora para que suba al tope
        try:
            database.supabase.table("clientes").update({
                "observaciones_generales": nuevo_historial,
                "leido": False,
                "fecha_contacto": ahora.strftime("%Y-%m-%d"),
                "hora_contacto": ahora.strftime("%H:%M:%S")
            }).eq("telefono", From).execute()
        except Exception as e:
            print(f"[ERROR ACTUALIZAR SILENCIO] {e}")
            
        return Response(content="<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>", media_type="text/xml")

    # ==============================================================================
    # MODULO CLIENTES (RAG Y CRM)
    # ==============================================================================
    historial = (cliente_db.get("observaciones_generales") or "")[-4000:] if cliente_db else ""

    datos_msg = {}
    try:
        resp = (agent.prompt_analista | agent.llm_analista).invoke({
            "mensaje": Body,
            "historial_chat": historial 
        })
        raw = resp.content.replace("```json", "").replace("```", "")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match: datos_msg = json.loads(match.group())
    except Exception as e:
        print(f"[ERROR ANALISTA] {e}")

    def fusionar(campo, es_numero=False):
        val_msg = utils.limpiar_numero(datos_msg.get(campo)) if es_numero else utils.limpiar_texto(datos_msg.get(campo))
        val_db = (utils.limpiar_numero(cliente_db.get(campo)) if es_numero else utils.limpiar_texto(cliente_db.get(campo))) if cliente_db else None
        return val_msg if val_msg else val_db

    datos_finales = {
        "nombre_cliente": fusionar("nombre_cliente"),
        "zona_municipio": fusionar("zona_municipio"),
        "tipo_inmueble": fusionar("tipo_inmueble"),
        "tipo_operacion": fusionar("tipo_operacion"),
        "presupuesto": fusionar("presupuesto", es_numero=True),
        "clave_propiedad": datos_msg.get("clave_propiedad"),
        "origen_campana": datos_msg.get("origen_campana")
    }

    if datos_finales["origen_campana"]: datos_msg["origen"] = datos_finales["origen_campana"]

    inventario = ""
    propiedades = []
    faltante = "Ninguno"
    quiere_ver = utils.detectar_intencion_ver_propiedades(Body)

    if datos_finales["clave_propiedad"]:
        propiedades = database.buscar_por_clave(datos_finales["clave_propiedad"])
    else:
        if not datos_finales["zona_municipio"]: 
            faltante = "ZONA"
        elif not datos_finales["presupuesto"]: 
            faltante = "PRESUPUESTO"
        elif not datos_finales["nombre_cliente"]: 
            faltante = "NOMBRE_SOLO_SI_HAY_CITA"

        if faltante in ["Ninguno", "NOMBRE_SOLO_SI_HAY_CITA"] or quiere_ver or datos_finales["zona_municipio"] or datos_finales["tipo_inmueble"]:
            propiedades = database.buscar_propiedades(
                datos_finales["tipo_inmueble"], 
                datos_finales["tipo_operacion"],
                datos_finales["zona_municipio"],
                datos_finales["presupuesto"], 
                mostrar_mix_general=(quiere_ver and not datos_finales["zona_municipio"])
            )

    if propiedades:
        for p in propiedades:
            id_prop = p.get('id') 
            clave = p.get('clave', 'S/N')
            tipo = p.get('subtipoPropiedad') or 'Propiedad'
            operacion = p.get('tipoOperacion') or 'Venta'
            mun = p.get('municipio', 'Zona C21')
            col = p.get('colonia', '')
            pre = p.get('precio', 0)
            desc = p.get('descripcion', 'Sin descripción detallada.')
            m2t = p.get('m2T') or 0      
            m2c = p.get('m2C') or 0      
            banos = p.get('banios') or 0 
            habs = p.get('recamaras') or p.get('ambientes') or 0 
            link_mapa = p.get('mapa_url')
            lat, lon = p.get('latitud'), p.get('longitud')
            if not link_mapa and lat and lon:
                link_mapa = f"https://maps.google.com/?q={lat},{lon}"
                if id_prop: database.guardar_mapa_generado(id_prop, link_mapa)
            if not link_mapa: link_mapa = "Solicita ubicación a tu asesor."
            link_ficha = p.get('url_ficha') or "Solicita el enlace con fotos a tu asesor"

            inventario += f"""
            ---
            Referencia: {clave}
            {tipo} en {operacion} - {mun} ({col})
            Precio: ${pre:,.0f}
            Terreno: {m2t}m2 | Constr: {m2c}m2
            Habitaciones: {habs} | Baños: {banos}
            Ubicación: {link_mapa}
            Fotos y Ficha Técnica: {link_ficha}
            Detalle: {desc}
            ---
            """
    elif quiere_ver and not datos_finales["clave_propiedad"]:
        inventario = "No encontré coincidencias exactas."

    if inventario and ("Referencia:" in inventario or "ID:" in inventario):
        faltante = "Ninguno"

    try:
        respuesta = (agent.prompt_vendedor | agent.llm_vendedor).invoke({
            "mensaje": Body, 
            "nombre_final": datos_finales["nombre_cliente"],
            "zona_final": datos_finales["zona_municipio"], 
            "presupuesto_final": datos_finales["presupuesto"],
            "operacion_final": datos_finales["tipo_operacion"],
            "dato_faltante_prioritario": faltante, 
            "inventario": inventario, 
            "historial_chat": historial
        }).content
    except Exception as e:
        print(f"[ERROR GENERACION] {e}")
        respuesta = "Dame un momento, estoy consultando el inventario."

    print(f"[BOT] {respuesta}")

    await database.guardar_cliente(Body, respuesta, From, datos_msg, cliente_existente=cliente_db)

    # ==============================================================================
    # MODULO NOTIFICACIONES
    # ==============================================================================
    valor_asesor = str(datos_msg.get("quiere_asesor", "")).lower()
    nombre_lead = datos_finales.get("nombre_cliente")
    correo_ya_enviado = cliente_db.get("correo_enviado", False) if cliente_db else False
    
    if valor_asesor == "true" and nombre_lead and not correo_ya_enviado:
        historial_actualizado = f"{(cliente_db.get('observaciones_generales') or '')}\nCliente: {Body}\nBot: {respuesta}"
        
        try:
            resumen_ejecutivo = (agent.prompt_resumen | agent.llm_analista).invoke({
                "historial": historial_actualizado,
                "nombre": datos_finales.get("nombre_cliente") or "Cliente sin nombre",
                "telefono": From
            }).content
        except Exception as e:
            resumen_ejecutivo = historial_actualizado 

        info_lead = {
            "nombre": datos_finales.get("nombre_cliente") or "Cliente",
            "telefono": From,
            "zona": datos_finales.get("zona_municipio") or "No especificada",
            "presupuesto": datos_finales.get("presupuesto") or "No especificado"
        }
        
        asesor_asignado = database.obtener_asesor_aleatorio()
        
        if asesor_asignado:
            telefono_asesor = asesor_asignado.get("telefono") or "whatsapp:+5214272786799"
            nombre_asesor = asesor_asignado.get("nombre") or "Administrador"
        else:
            telefono_asesor = "whatsapp:+5214272786799"
            nombre_asesor = "Administrador"
            
        correo_destino = "richardRI1690@gmail.com" 
            
        mailer.enviar_notificacion_asesor(info_lead, resumen_ejecutivo, correo_destino, nombre_asesor)
        whatsapp_notifier.enviar_alerta_asesor(telefono_asesor, info_lead, resumen_ejecutivo)
        
        try:
            database.supabase.table("clientes").update({"correo_enviado": True}).eq("telefono", From).execute()
        except Exception as e:
            pass

    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{respuesta.replace('&','y')}</Message></Response>"""
    return Response(content=xml.strip(), media_type="text/xml")


@app.get("/descargar/{nombre_asesor}")
async def descargar_reporte_asesor(nombre_asesor: str):
    datos = database.obtener_propiedades_por_asesor(nombre_asesor)
    if not datos: return Response(content="No se encontraron propiedades.", media_type="text/plain")

    stream = io.StringIO()
    writer = csv.writer(stream, quoting=csv.QUOTE_ALL)
    writer.writerow(list(datos[0].keys()))
    for fila in datos:
        writer.writerow([str(valor) if valor is not None else "" for valor in fila.values()])

    stream.seek(0)
    return StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Inventario_{nombre_asesor}.csv"}
    )

# ================================================================
# ENDPOINTS DEL DASHBOARD (AHORA ORDENA POR HORA DE MENSAJE)
# ================================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    base_path = os.path.dirname(__file__)
    path = os.path.join(base_path, "dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/conversaciones")
def obtener_conversaciones():
    try:
        # Traemos todos los clientes (sin orden fijo de SQL)
        resp = database.supabase.table("clientes").select("telefono,nombre_cliente,bot_encendido,observaciones_generales,fecha_contacto,hora_contacto,leido").execute()
        clientes_db = resp.data
        
        # ORDENAMIENTO EN PYTHON: Combinamos fecha y hora para que el más reciente salte arriba
        def get_datetime(c):
            f = c.get('fecha_contacto') or '1970-01-01'
            h = c.get('hora_contacto') or '00:00:00'
            return f"{f} {h}"
            
        clientes_db.sort(key=get_datetime, reverse=True)
        
        clientes = []
        for c in clientes_db:
            try:
                tel_raw = c.get("telefono")
                tel = str(tel_raw) if tel_raw else "Sin Número"
                nombre_raw = c.get("nombre_cliente")
                display = str(nombre_raw) if nombre_raw else tel
                
                historial = str(c.get("observaciones_generales") or "")
                lineas = [l for l in historial.split('\n') if l.strip()]
                ultimo_msg = lineas[-1] if lineas else "Sin mensajes aún"
                
                ultimo_msg = re.sub(r"^\[\d{2}:\d{2}\]\s*", "", ultimo_msg)
                ultimo_msg = ultimo_msg.replace("Cliente:", "Cliente:").replace("Bot:", "IA:").replace("Asesor:", "Tú:")
                if len(ultimo_msg) > 35: ultimo_msg = ultimo_msg[:35] + "..."

                bot_estado = c.get("bot_encendido")
                if bot_estado is None: bot_estado = True
                
                leido_estado = c.get("leido")
                if leido_estado is None: leido_estado = True

                clientes.append({
                    "telefono": tel,
                    "display": display,
                    "bot_encendido": bool(bot_estado),
                    "ultimo_mensaje": ultimo_msg,
                    "leido": bool(leido_estado)
                })
            except Exception:
                continue 

        return clientes
    except Exception as e:
        print(f"[ALERTA DASHBOARD] Fallo crítico al cargar clientes: {e}")
        return []

@app.get("/chat/{telefono}")
def obtener_chat(telefono: str):
    try:
        resp = database.supabase.table("clientes").select("telefono,nombre_cliente,observaciones_generales,bot_encendido").eq("telefono", telefono).execute()
        return resp.data
    except Exception as e:
        return []

# ENDPOINT NUEVO: Quita el punto verde cuando abres el chat
@app.post("/api/marcar_leido/{telefono}")
def marcar_leido(telefono: str):
    try:
        database.supabase.table("clientes").update({"leido": True}).eq("telefono", telefono).execute()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@app.post("/toggle_bot/{telefono}")
def toggle_bot(telefono: str, req: ToggleRequest):
    try:
        database.supabase.table("clientes").update({"bot_encendido": req.estado}).eq("telefono", telefono).execute()
        return {"status": "ok", "bot_encendido": req.estado}
    except Exception:
        return {"status": "error"}

@app.post("/api/enviar_mensaje/{telefono}")
def enviar_mensaje_asesor(telefono: str, req: MensajeAsesorRequest):
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=whatsapp_notifier.TWILIO_NUMERO_BOT,
            body=req.mensaje,
            to=telefono
        )
    except Exception as e:
        print(f"[ERROR TWILIO] No se pudo enviar el mensaje: {e}")
        return {"status": "error", "detalle": str(e)}

    try:
        cliente_db = database.obtener_cliente(telefono)
        if cliente_db:
            ahora = datetime.now()
            hora_corta = ahora.strftime("%H:%M")
            historial_actual = cliente_db.get("observaciones_generales") or ""
            prefijo = "\n" if historial_actual else ""
            nuevo_historial = f"{historial_actual}{prefijo}[{hora_corta}] Asesor: {req.mensaje}"
            
            # Al contestar el asesor: Apagamos el bot, marcamos como leído, y actualizamos la hora para mantenerlo arriba
            database.supabase.table("clientes").update({
                "observaciones_generales": nuevo_historial,
                "bot_encendido": False,
                "leido": True,
                "fecha_contacto": ahora.strftime("%Y-%m-%d"),
                "hora_contacto": ahora.strftime("%H:%M:%S")
            }).eq("telefono", telefono).execute()
    except Exception:
        pass

    return {"status": "ok", "bot_encendido": False}

# ================================================================
# ENDPOINTS DE ASESORES (ACTIVOS/INACTIVOS)
# ================================================================
@app.get("/api/asesores")
def obtener_asesores():
    try:
        resp = database.supabase.table("asesores").select("id, nombre, activo").order("id").execute()
        return resp.data
    except Exception as e:
        return []

@app.post("/api/asesores/{id_asesor}/toggle")
def toggle_asesor(id_asesor: int, req: ToggleAsesorRequest):
    try:
        database.supabase.table("asesores").update({"activo": req.estado}).eq("id", id_asesor).execute()
        return {"status": "ok", "activo": req.estado}
    except Exception as e:
        return {"status": "error"}

# ================================================================
# NUEVO: ENDPOINT DE REPORTES POR PROPIEDAD
# ================================================================
@app.get("/api/reportes/propiedad/{clave}")
def reporte_propiedad(clave: str):
    try:
        # Buscamos clientes que tengan esta clave en su registro usando la columna correcta
        res = database.supabase.table("clientes").select("fecha_contacto,nombre_cliente,telefono,presupuesto,zona_municipio").eq("id_propiedad_opcional", clave).execute()
        datos = res.data
                
        return {"status": "ok", "resultados": datos}
    except Exception as e:
        print(f"[ERROR REPORTES] Fallo al generar reporte: {e}")
        return {"status": "error", "detalle": str(e)}