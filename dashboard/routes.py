import os
import re
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from twilio.rest import Client
import config
import database
import whatsapp_notifier

router = APIRouter()

# ==============================================================================
# MODELOS DE DATOS
# ==============================================================================
class ToggleRequest(BaseModel):
    estado: bool

class MensajeAsesorRequest(BaseModel):
    mensaje: str

class ToggleAsesorRequest(BaseModel):
    estado: bool

class NuevoAsesorRequest(BaseModel):
    nombre: str
    telefono: str

# ==============================================================================
# RUTAS DEL DASHBOARD (FRONTEND Y BACKEND)
# ==============================================================================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    base_path = os.path.dirname(__file__)
    path = os.path.join(base_path, "dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@router.get("/conversaciones")
def obtener_conversaciones():
    try:
        resp = database.supabase.table("clientes").select("telefono,nombre_cliente,bot_encendido,observaciones_generales,fecha_contacto,hora_contacto,leido").execute()
        clientes_db = resp.data
        
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

@router.get("/chat/{telefono}")
def obtener_chat(telefono: str):
    try:
        resp = database.supabase.table("clientes").select("telefono,nombre_cliente,observaciones_generales,bot_encendido").eq("telefono", telefono).execute()
        return resp.data
    except Exception:
        return []

@router.post("/api/marcar_leido/{telefono}")
def marcar_leido(telefono: str):
    try:
        database.supabase.table("clientes").update({"leido": True}).eq("telefono", telefono).execute()
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@router.post("/toggle_bot/{telefono}")
def toggle_bot(telefono: str, req: ToggleRequest):
    try:
        database.supabase.table("clientes").update({"bot_encendido": req.estado}).eq("telefono", telefono).execute()
        return {"status": "ok", "bot_encendido": req.estado}
    except Exception:
        return {"status": "error"}

@router.post("/api/enviar_mensaje/{telefono}")
def enviar_mensaje_asesor(telefono: str, req: MensajeAsesorRequest):
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        client.messages.create(
            # 🚨 CORRECCIÓN: Aquí estaba el error. Ahora usamos el nombre correcto de la variable.
            from_=whatsapp_notifier.NUMERO_TWILIO,
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

# ==============================================================================
# GESTIÓN DE ASESORES (CRUD COMPLETO)
# ==============================================================================
@router.get("/api/asesores")
def obtener_asesores():
    try:
        resp = database.supabase.table("asesores").select("id, nombre, telefono, activo").order("id").execute()
        return resp.data
    except Exception:
        return []

@router.post("/api/asesores/{id_asesor}/toggle")
def toggle_asesor(id_asesor: int, req: ToggleAsesorRequest):
    try:
        database.supabase.table("asesores").update({"activo": req.estado}).eq("id", id_asesor).execute()
        return {"status": "ok", "activo": req.estado}
    except Exception:
        return {"status": "error"}

@router.post("/api/asesores")
def agregar_asesor(req: NuevoAsesorRequest):
    try:
        tel_limpio = req.telefono.strip()
        if not tel_limpio.startswith("whatsapp:"):
            tel_limpio = f"whatsapp:{tel_limpio}"

        nuevo = {
            "nombre": req.nombre.strip(),
            "telefono": tel_limpio,
            "activo": True 
        }
        res = database.supabase.table("asesores").insert(nuevo).execute()
        return {"status": "ok", "data": res.data}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

@router.delete("/api/asesores/{id_asesor}")
def eliminar_asesor(id_asesor: int):
    try:
        database.supabase.table("asesores").delete().eq("id", id_asesor).execute()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

# ==============================================================================
# REPORTES Y ANALÍTICA
# ==============================================================================
@router.get("/api/reportes/resumen")
def obtener_resumen_reportes():
    try:
        res = database.supabase.table("clientes").select("id_propiedad_opcional").neq("id_propiedad_opcional", "").execute()
        conteo = {}
        for row in res.data:
            prop_id = row.get("id_propiedad_opcional")
            if prop_id and prop_id.strip() and str(prop_id).lower() != "none":
                conteo[prop_id] = conteo.get(prop_id, 0) + 1
        lista_resumen = [{"clave": k, "interesados": v} for k, v in conteo.items()]
        lista_resumen.sort(key=lambda x: x["interesados"], reverse=True)
        return {"status": "ok", "resultados": lista_resumen}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

@router.get("/api/reportes/propiedad/{clave}")
def reporte_propiedad(clave: str):
    try:
        columnas = "id,nombre_cliente,telefono,fecha_contacto,hora_contacto,presupuesto,observaciones_generales"
        res = database.supabase.table("clientes").select(columnas).eq("id_propiedad_opcional", clave).execute()
        return {"status": "ok", "resultados": res.data}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}