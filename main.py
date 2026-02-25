import json
import re
import io
import csv
from fastapi import FastAPI, Form, Response
from fastapi.responses import StreamingResponse
import database
import agent
import utils

app = FastAPI()

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

    print(f"\n[MENSAJE] {From} → {Body}")

    nombre_asesor = database.obtener_asesor_por_telefono(From)
    if nombre_asesor and ("reporte" in Body.lower() or "inventario" in Body.lower()):
        base_url = "https://TU-URL-DE-RENDER.onrender.com" 
        link_descarga = f"{base_url}/descargar/{nombre_asesor.replace(' ', '%20')}"
        mensaje_vip = f"👋 Hola colega *{nombre_asesor}*.\n\nAquí tienes tu reporte de inventario:\n📄 {link_descarga}\n\n¡Éxito en tus ventas! 🏠"
        xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{mensaje_vip}</Message></Response>"""
        return Response(content=xml.strip(), media_type="text/xml")

    cliente_db = database.obtener_cliente(From)
    historial = (cliente_db.get("observaciones_generales") or "")[-600:] if cliente_db else ""

    datos_msg = {}
    try:
        resp = (agent.prompt_analista | agent.llm_analista).invoke({"mensaje": Body})
        raw = resp.content.replace("```json", "").replace("```", "")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match: datos_msg = json.loads(match.group())
    except: pass

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

    if datos_finales["clave_propiedad"]:
        propiedades = database.buscar_por_clave(datos_finales["clave_propiedad"])
    else:
        quiere_ver = utils.detectar_intencion_ver_propiedades(Body)
        if not datos_finales["nombre_cliente"]: faltante = "NOMBRE"
        elif not datos_finales["zona_municipio"]: faltante = "ZONA"
        elif not datos_finales["presupuesto"]: faltante = "PRESUPUESTO"

        if faltante == "Ninguno" or quiere_ver:
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

            inventario += f"""
            ---
            🆔 Referencia: {clave}
            🏠 {tipo} en {operacion} - {mun} ({col})
            💰 Precio: ${pre:,.0f}
            📏 Terreno: {m2t}m² | Constr: {m2c}m²
            🛏️ Habitaciones: {habs} | 🛁 Baños: {banos}
            📍 Ubicación: {link_mapa}
            📝 Detalle: {desc}
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