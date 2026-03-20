import os
import json
import re
from datetime import datetime
from fastapi import FastAPI, Form, Response
from twilio.rest import Client
import config
import database
import agent
import utils
import whatsapp_notifier

# 1. IMPORTAMOS EL MÓDULO DEL DASHBOARD (Tu código)
from dashboard.routes import router as dashboard_router

app = FastAPI()

# 2. CONECTAMOS EL DASHBOARD A LA APP PRINCIPAL
app.include_router(dashboard_router)

# ==============================================================================
# ENDPOINT PRINCIPAL: WHATSAPP BOT (Lógica intacta de tu compañero)
# ==============================================================================
@app.post("/whatsapp")
async def whatsapp_reply(
    From: str = Form(...),
    Body: str = Form(default=""),               
    NumMedia: str = Form(default="0"),          
    MediaUrl0: str = Form(default=""),          
    MediaContentType0: str = Form(default="")   
):
    # 1. Procesamiento de Audio
    if NumMedia != "0" and "audio" in MediaContentType0:
        texto_transcrito = utils.descargar_y_transcribir_audio(MediaUrl0)
        Body = texto_transcrito

    print(f"\n[MENSAJE] {From} -> {Body}")
    body_lower = Body.lower()

    # ==============================================================================
    # SILENCIADOR MANUAL DEL BOT (HUMAN IN THE LOOP)
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
        resp = await (agent.prompt_analista | agent.llm_analista).ainvoke({
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
        if campo == "presupuesto" and datos_msg.get("zona_municipio") and not datos_msg.get("presupuesto"):
            return None
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

    # 🔍 DETECCIÓN DE INTENCIÓN DE CRÉDITO
    tipo_credito_detectado = None
    if "infonavit" in body_lower: tipo_credito_detectado = "infonavit"
    elif "fovissste" in body_lower: tipo_credito_detectado = "fovissste"
    elif "bancario" in body_lower: tipo_credito_detectado = "bancario"
    elif "credito" in body_lower or "crédito" in body_lower: tipo_credito_detectado = "general"

    if datos_finales["clave_propiedad"]:
        propiedades = database.buscar_por_clave(datos_finales["clave_propiedad"])
    else:
        if not datos_finales["zona_municipio"]: faltante = "ZONA"
        elif not datos_finales["presupuesto"]: faltante = "PRESUPUESTO"
        
        if faltante in ["Ninguno", "NOMBRE_SOLO_SI_HAY_CITA"] or quiere_ver or datos_finales["zona_municipio"] or datos_finales["tipo_inmueble"]:
            propiedades = database.buscar_propiedades(
                datos_finales["tipo_inmueble"], 
                datos_finales["tipo_operacion"],
                datos_finales["zona_municipio"],
                datos_finales["presupuesto"], 
                mostrar_mix_general=(quiere_ver and not datos_finales["zona_municipio"]),
                tipo_credito=tipo_credito_detectado
            )

    if propiedades:
        for p in propiedades:
            pre = p.get('precio', 0)
            desc = p.get('descripcion', '').lower()
            
        
            acepta = {
                "Infonavit": "infonavit" in desc,
                "Fovissste": "fovissste" in desc,
                "Bancario": "bancario" in desc or "crédito" in desc or "credito" in desc
            }
            creditos_aceptados = [nombre for nombre, lo_acepta in acepta.items() if lo_acepta]
            status_credito = f"✅ Acepta: {', '.join(creditos_aceptados)}" if creditos_aceptados else "❌ NO acepta créditos, solo pago con recursos propios"

            inventario += f"""
                ---
                🆔 Referencia: {p.get('clave', 'S/N')}
                🏠 {p.get('subtipoPropiedad', 'Propiedad')} en {p.get('tipoOperacion', 'Venta')} - {p.get('municipio', 'Zona C21')}
                💰 Precio: ${pre:,.0f}
                💳 Créditos: {status_credito}
                📝 Detalles: {p.get('descripcion', 'Sin descripción detallada.')}
                📸 Ficha: {p.get('url_ficha') or 'Consultar asesor'}
                ---
                """
    elif quiere_ver and not datos_finales["clave_propiedad"]:
        inventario = "No encontré coincidencias exactas."

    try:
        respuesta_ia = await (agent.prompt_vendedor | agent.llm_vendedor).ainvoke({
            "mensaje": Body, 
            "nombre_final": datos_finales["nombre_cliente"],
            "zona_final": datos_finales["zona_municipio"], 
            "presupuesto_final": datos_finales["presupuesto"],
            "operacion_final": datos_finales["tipo_operacion"],
            "dato_faltante_prioritario": faltante, 
            "inventario": inventario, 
            "historial_chat": historial
        })
        respuesta = respuesta_ia.content # <--- Aquí sacamos el texto ya que terminó de pensar
    except Exception as e:
        print(f"[ERROR GENERACION] {e}")
        respuesta = "Dame un momento, estoy consultando el inventario."

    print(f"[BOT] {respuesta}")

    # Guardar primera interacción en DB
    await database.guardar_cliente(Body, respuesta, From, datos_msg, cliente_existente=cliente_db)

    # ==============================================================================
    # MODULO NOTIFICACIONES Y ASIGNACIÓN (REESCRITO)
    # ==============================================================================
    valor_asesor = str(datos_msg.get("quiere_asesor", "")).lower()
    nombre_lead = datos_finales.get("nombre_cliente")
    
    alerta_ya_enviada = cliente_db.get("correo_enviado", False) if cliente_db else False
    
    if valor_asesor == "true" and nombre_lead and not alerta_ya_enviada:
        historial_actualizado = f"{(cliente_db.get('observaciones_generales') or '')}\nCliente: {Body}\nBot: {respuesta}"
        nombre_seguro = nombre_lead if nombre_lead else "Cliente (Sin nombre)"
        
        try:
            resumen_ia = await (agent.prompt_resumen | agent.llm_analista).ainvoke({
                "historial": historial_actualizado,
                "nombre": nombre_seguro,
                "telefono": From
            })
            resumen_ejecutivo = resumen_ia.content 
            
            info_lead = {
                "nombre": nombre_seguro,
                "telefono": From,
                "zona": datos_finales.get("zona_municipio") or "No especificada",
                "presupuesto": datos_finales.get("presupuesto") or "No especificado"
            }
            
            #LÓGICA DE ASIGNACIÓN 
            asesor_asignado = None
            nombre_solicitado = datos_msg.get("asesor_solicitado")
            # Valores por defecto (se va a la oficina si algo falla)
            nombre_final_asesor = "Oficina"
            telefono_final_asesor = whatsapp_notifier.NUMERO_OFICINA
            
            if nombre_solicitado:
                asesor_asignado = database.obtener_asesor_por_nombre(nombre_solicitado)
                if asesor_asignado:
                    print(f"[ASIGNACIÓN] El cliente pidió a {asesor_asignado['nombre']} y está ACTIVO.")
                    nombre_final_asesor = asesor_asignado['nombre']
                    telefono_final_asesor = asesor_asignado['telefono']
                else:
                    print(f"[ASIGNACIÓN] Pidió a '{nombre_solicitado}' pero está inactivo/no existe. Va a Oficina.")
                    nombre_final_asesor = f"Oficina (Pidió a {nombre_solicitado})"
            else:
                asesor_asignado = database.obtener_asesor_aleatorio()
                if asesor_asignado:
                    print(f"[ASIGNACIÓN] La ruleta eligió a: {asesor_asignado['nombre']}")
                    nombre_final_asesor = asesor_asignado['nombre']
                    telefono_final_asesor = asesor_asignado['telefono']

            # ENVIAR ALERTA DOBLE (Asesor + Oficina)
            whatsapp_notifier.enviar_alerta_asesor(
                numero_asesor=telefono_final_asesor,
                datos_cliente=info_lead,
                resumen_ai=resumen_ejecutivo,
                nombre_asesor=nombre_final_asesor
            )
            # ACTUALIZAR BASE DE DATOS (Columna seguimiento)
            database.supabase.table("clientes").update({
                "correo_enviado": True, #
                "seguimiento": nombre_final_asesor 
            }).eq("telefono", From).execute()
            
        except Exception as e:
            print(f"[ERROR EN NOTIFICACIONES] {e}")

    # Respuesta XML Segura
    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{respuesta.replace('&','y')}</Message></Response>"""
    return Response(content=xml.strip(), media_type="text/xml")