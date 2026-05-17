import os

from fastapi import APIRouter, Depends, HTTPException
from groq import Groq
from sqlalchemy.orm import Session

from database import get_db
from models import (
    CargaEmocional,
    Configuracion,
    HistorialSesion,
    NotaClinica,
    Paciente,
    PatronKlinos,
    PreparacionSesion,
    RegistroSesion,
)
from schemas import (
    CargaEmocionalOut,
    ChatRequest,
    ChatResponse,
    HistorialSesionOut,
    NotasUpdate,
    NotaClinicaCreate,
    NotaClinicaOut,
    PatronKlinosOut,
    PreparacionOut,
    RegistroSesionCreate,
    RegistroSesionOut,
)

router = APIRouter(prefix="/api/klinos", tags=["klinos"])


@router.get("/notas/{paciente_id}", response_model=list[NotaClinicaOut])
def list_notas(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(NotaClinica).filter(NotaClinica.paciente_id == paciente_id).order_by(NotaClinica.created_at.desc()).all()


@router.post("/notas", response_model=NotaClinicaOut)
def save_nota(data: NotaClinicaCreate, db: Session = Depends(get_db)):
    n = NotaClinica(**data.model_dump())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


@router.get("/patrones/{paciente_id}", response_model=list[PatronKlinosOut])
def list_patrones(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(PatronKlinos).filter(PatronKlinos.paciente_id == paciente_id).all()


@router.get("/preparaciones/{paciente_id}", response_model=list[PreparacionOut])
def list_preparaciones(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(PreparacionSesion).filter(PreparacionSesion.paciente_id == paciente_id).all()


@router.get("/historial/{paciente_id}", response_model=list[HistorialSesionOut])
def list_historial(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(HistorialSesion).filter(HistorialSesion.paciente_id == paciente_id).order_by(HistorialSesion.fecha.desc()).all()


@router.put("/preparaciones/{prep_id}", response_model=PreparacionOut)
def toggle_preparacion(prep_id: int, db: Session = Depends(get_db)):
    p = db.query(PreparacionSesion).filter(PreparacionSesion.id == prep_id).first()
    if not p:
        raise HTTPException(404, "Preparación no encontrada")
    p.completado = not p.completado
    db.commit()
    db.refresh(p)
    return p


@router.get("/carga", response_model=CargaEmocionalOut | None)
def get_carga(db: Session = Depends(get_db)):
    return db.query(CargaEmocional).order_by(CargaEmocional.id.desc()).first()


@router.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest, db: Session = Depends(get_db)):
    cfg = {c.key: c.value for c in db.query(Configuracion).all()}
    api_key = cfg.get("groq_api_key") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return ChatResponse(reply="Configura tu API key de Groq en Configuración → Integraciones.")
    try:
        context = ""
        if data.paciente_id:
            p = db.query(Paciente).filter(Paciente.id == data.paciente_id).first()
            if p:
                notas = db.query(NotaClinica).filter(NotaClinica.paciente_id == data.paciente_id).order_by(NotaClinica.created_at.desc()).limit(3).all()
                notas_text = "\n".join(f"- {n.contenido}" for n in notas)
                context = f"Contexto del paciente {p.nombre} (diagnóstico: {p.diagnostico or 'N/A'}, sesiones: {p.sesiones_total}):\n{notas_text}"

        client = Groq(api_key=api_key)
        messages = [
            {"role": "system", "content": "Eres Klinós IA, un asistente clínico experto en psicología y salud mental. Respondes en español, con lenguaje profesional pero accesible. Ayudas a terapeutas a reflexionar sobre sus casos."},
        ]
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": data.message})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or ""
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Error al conectar con Groq: {str(e)}")


# ─── Sesiones ───
@router.get("/sesiones/terapeuta/{terapeuta_id}")
def sesiones_por_terapeuta(terapeuta_id: int, db: Session = Depends(get_db)):
    from models import Cita, Terapeuta
    citas = db.query(Cita).filter(Cita.terapeuta_id == terapeuta_id).order_by(Cita.fecha, Cita.hora).all()
    result = []
    for c in citas:
        reg = db.query(RegistroSesion).filter(RegistroSesion.cita_id == c.id).first()
        paciente = db.query(Paciente).filter(Paciente.id == c.paciente_id).first()
        result.append({
            "id": c.id,
            "paciente": paciente.nombre if paciente else "N/A",
            "paciente_id": c.paciente_id,
            "fecha": c.fecha,
            "hora": c.hora,
            "tipo_sesion": c.tipo_sesion,
            "sala": c.sala,
            "duracion": c.duracion,
            "estado": c.estado,
            "sesion_estado": reg.estado if reg else "pendiente",
            "registro_id": reg.id if reg else None,
        })
    return result


@router.get("/sesiones/terapeuta/by-name/{nombre}")
def sesiones_por_nombre(nombre: str, db: Session = Depends(get_db)):
    from models import Cita, Terapeuta
    terapeuta = db.query(Terapeuta).filter(Terapeuta.nombre.ilike(f"%{nombre}%")).first()
    if not terapeuta:
        return []
    return sesiones_por_terapeuta(terapeuta.id, db)


@router.post("/sesiones/iniciar", response_model=RegistroSesionOut)
def iniciar_sesion(data: RegistroSesionCreate, db: Session = Depends(get_db)):
    existing = db.query(RegistroSesion).filter(RegistroSesion.cita_id == data.cita_id).first()
    if existing:
        existing.estado = "activa"
        db.commit()
        db.refresh(existing)
        return existing
    reg = RegistroSesion(cita_id=data.cita_id, estado="activa")
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.put("/sesiones/{registro_id}/notas")
def guardar_notas(registro_id: int, data: NotasUpdate, db: Session = Depends(get_db)):
    reg = db.query(RegistroSesion).filter(RegistroSesion.id == registro_id).first()
    if not reg:
        raise HTTPException(404, "Registro no encontrado")
    reg.notas = data.notas
    db.commit()
    return {"ok": True}


@router.get("/sesiones/{registro_id}")
def get_registro(registro_id: int, db: Session = Depends(get_db)):
    reg = db.query(RegistroSesion).filter(RegistroSesion.id == registro_id).first()
    if not reg:
        raise HTTPException(404, "Registro no encontrado")
    return RegistroSesionOut.model_validate(reg)


@router.post("/sesiones/{registro_id}/cerrar")
def cerrar_sesion(registro_id: int, db: Session = Depends(get_db)):
    from datetime import datetime
    reg = db.query(RegistroSesion).filter(RegistroSesion.id == registro_id).first()
    if not reg:
        raise HTTPException(404, "Registro no encontrado")
    reg.estado = "cerrada"
    reg.cerrado_at = datetime.now()

    # Analizar con Groq si hay notas
    if reg.notas.strip():
        cfg = {c.key: c.value for c in db.query(Configuracion).all()}
        api_key = cfg.get("groq_api_key") or os.environ.get("GROQ_API_KEY", "")
        if api_key:
            try:
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {"role": "system", "content": "Eres un analista clínico. Analiza las notas de sesión de un terapeuta y proporciona: 1) Un breve resumen/conclusión de la sesión (2-3 líneas). 2) Una calificación de intensidad para el TERAPEUTA (baja, media, alta) basada en el contenido emocional y la complejidad del caso. Responde solo con el análisis en formato: CONCLUSIÓN: ... | INTENSIDAD: baja|media|alta"},
                        {"role": "user", "content": f"Notas de la sesión:\n{reg.notas}"},
                    ],
                    max_tokens=512,
                    temperature=0.5,
                )
                respuesta = completion.choices[0].message.content or ""
                if "|" in respuesta:
                    partes = respuesta.split("|")
                    reg.analisis = partes[0].replace("CONCLUSIÓN:", "").strip()
                    intensidad_raw = partes[1].replace("INTENSIDAD:", "").strip().lower()
                    reg.intensidad = intensidad_raw if intensidad_raw in ("baja", "media", "alta") else "media"
                else:
                    reg.analisis = respuesta
                    reg.intensidad = "media"
            except Exception:
                reg.analisis = "No se pudo analizar la sesión."
                reg.intensidad = "media"

    db.commit()
    db.refresh(reg)
    return RegistroSesionOut.model_validate(reg)
