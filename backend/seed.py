import hashlib
import json

from database import SessionLocal
from models import (
    CargaEmocional,
    Cita,
    Configuracion,
    Curso,
    Evento,
    Finanza,
    HistorialSesion,
    NotaClinica,
    Paciente,
    PatronKlinos,
    PreparacionSesion,
    RegistroSesion,
    Terapeuta,
    TipoTerapia,
    User,
)


def seed_data():
    db = SessionLocal()
    try:
        if db.query(Terapeuta).count() > 0:
            return

        # ── Terapeutas ──
        t1 = Terapeuta(nombre="Dra. María González", email="maria.gonzalez@centro.cl", telefono="+56 9 1111 2222", especialidad="Psicología Clínica", horario="Lun–Vie · 09:00–18:00")
        t2 = Terapeuta(nombre="Dr. Pedro Silva", email="pedro.silva@centro.cl", telefono="+56 9 7777 8888", especialidad="Kinesiología", horario="Lun–Sáb · 08:00–17:00")
        t3 = Terapeuta(nombre="Dra. Ana López", email="ana.lopez@centro.cl", telefono="+56 9 5555 6666", especialidad="Fonoaudiología", horario="Lun, Mié, Vie · 09:00–14:00")
        t4 = Terapeuta(nombre="Dr. Carlos Ruiz", email="carlos.ruiz@centro.cl", telefono="+56 9 3333 4444", especialidad="Terapia Ocupacional", horario="Mar, Jue, Sáb · 10:00–16:00")
        db.add_all([t1, t2, t3, t4])
        db.commit()

        # ── Pacientes ──
        p1 = Paciente(nombre="Juan Pérez", email="juan@ejemplo.com", telefono="+56 9 1234 5678", rut="12.345.678-9", edad=32, fecha_inicio="01 mar 2026", diagnostico="Trastorno de ansiedad generalizada", terapeuta_id=t1.id, status="Trabajo activo", sesiones_total=8, ultima_sesion="14 abr 2026")
        p2 = Paciente(nombre="María Soto", email="maria@ejemplo.com", telefono="", rut="23.456.789-0", edad=28, fecha_inicio="05 feb 2026", diagnostico="Lumbalgia crónica", terapeuta_id=t2.id, status="Trabajo activo", sesiones_total=12, ultima_sesion="15 abr 2026")
        p3 = Paciente(nombre="Carlos Muñoz", email="carlos@ejemplo.com", telefono="+56 9 9876 5432", rut="34.567.890-1", edad=45, fecha_inicio="10 ene 2026", diagnostico="Retraso fonológico", terapeuta_id=t3.id, status="Trabajo activo", sesiones_total=6, ultima_sesion="10 abr 2026")
        p4 = Paciente(nombre="Roberto Díaz", email="roberto@ejemplo.com", telefono="+56 9 5555 1234", rut="45.678.901-2", edad=55, fecha_inicio="20 dic 2025", diagnostico="ACV isquémico - rehabilitación", terapeuta_id=t2.id, status="Alta", sesiones_total=24, ultima_sesion="01 abr 2026")
        p5 = Paciente(nombre="Ana Fernández", email="ana.f@ejemplo.com", telefono="", rut="56.789.012-3", edad=38, fecha_inicio="15 mar 2026", diagnostico="Depresión mayor", terapeuta_id=t1.id, status="Trabajo activo", sesiones_total=4, ultima_sesion="14 abr 2026")
        p6 = Paciente(nombre="Valentina Rojas", email="valentina@ejemplo.com", telefono="+56 9 7777 8888", rut="67.890.123-4", edad=22, fecha_inicio="01 abr 2026", diagnostico="Evaluación inicial", terapeuta_id=t1.id, status="Pendiente", sesiones_total=1, ultima_sesion="")
        db.add_all([p1, p2, p3, p4, p5, p6])
        db.commit()

        # ── Tipos de Terapia ──
        db.add_all([
            TipoTerapia(nombre="Psicoterapia Individual", descripcion="Sesión individual de psicoterapia", duracion_default=50, color="#3E8E6B"),
            TipoTerapia(nombre="Kinesiología", descripcion="Terapia física y rehabilitación", duracion_default=45, color="#D4893B"),
            TipoTerapia(nombre="Fonoaudiología", descripcion="Terapia del lenguaje y comunicación", duracion_default=30, color="#C25A6E"),
            TipoTerapia(nombre="Terapia Ocupacional", descripcion="Rehabilitación de actividades diarias", duracion_default=60, color="#6C5CE7"),
            TipoTerapia(nombre="Evaluación Psicológica", descripcion="Evaluación diagnóstica inicial", duracion_default=50, color="#3B7DBF"),
        ])
        db.commit()

        # ── Citas ──
        citas_data = [
            (p1, t1, "09:00", "Psicoterapia Individual", "Sala 1", 50),
            (p2, t2, "09:30", "Kinesiología", "Sala 3", 45),
            (p3, t3, "10:00", "Fonoaudiología", "Sala 2", 30),
            (p5, t1, "11:00", "Psicoterapia Individual", "Sala 1", 50),
            (p4, t2, "11:30", "Kinesiología", "Sala 3", 45),
            (p6, t1, "14:00", "Evaluación Psicológica", "Sala 1", 50),
        ]
        estados = ["confirmada", "confirmada", "pendiente_pago", "confirmada", "pendiente_pago", "confirmada"]
        for i, (p, t, hora, tipo, sala, dur) in enumerate(citas_data):
            db.add(Cita(paciente_id=p.id, terapeuta_id=t.id, fecha="15 abr", hora=hora, duracion=dur, tipo_sesion=tipo, sala=sala, estado=estados[i]))

        db.add(Cita(paciente_id=p5.id, terapeuta_id=t1.id, fecha="14 abr", hora="09:00", duracion=50, tipo_sesion="Psicoterapia Individual", sala="Sala 1", estado="completada"))
        db.add(Cita(paciente_id=p4.id, terapeuta_id=t2.id, fecha="14 abr", hora="10:00", duracion=45, tipo_sesion="Kinesiología", sala="Sala 3", estado="completada"))
        db.add(Cita(paciente_id=p2.id, terapeuta_id=t4.id, fecha="13 abr", hora="15:00", duracion=60, tipo_sesion="Terapia Ocupacional", sala="Sala 2", estado="confirmada"))
        db.commit()

        # ── Finanzas ──
        finanzas = [
            ("Juan Pérez", "Dra. González", "Psicoterapia", "15 abr", 30000, "Pagado"),
            ("María Soto", "Dr. Silva", "Kinesiología", "15 abr", 25000, "Pendiente"),
            ("Carlos Muñoz", "Dra. López", "Fonoaudiología", "15 abr", 20000, "Pendiente"),
            ("Roberto Díaz", "Dra. González", "Psicoterapia", "14 abr", 30000, "Pagado"),
            ("Ana Fernández", "Dr. Silva", "Kinesiología", "14 abr", 25000, "Pagado"),
            ("María Soto", "Dr. Ruiz", "T. Ocupacional", "13 abr", 35000, "Pagado"),
            ("Valentina Rojas", "Dra. González", "Evaluación", "13 abr", 40000, "Pendiente"),
            ("Juan Pérez", "Dra. González", "Psicoterapia", "07 abr", 30000, "Pagado"),
        ]
        for pac_nombre, ter_nombre, tipo, fecha, monto, estado in finanzas:
            db.add(Finanza(paciente=pac_nombre, terapeuta=ter_nombre, tipo=tipo, fecha=fecha, monto=monto, estado=estado))
        db.commit()

        # ── Eventos ──
        db.add_all([
            Evento(nombre="Feria de Bienestar 2026", descripcion="Evento presencial con múltiples terapeutas y agenda independiente.", fecha_inicio="10 mayo 2026", fecha_fin="12 mayo 2026", ubicacion="Centro de Convenciones, Santiago", terapeutas_count=4, citas_count=0),
            Evento(nombre="Congreso de Salud Mental", descripcion="Participación institucional en congreso nacional.", fecha_inicio="20 junio 2026", fecha_fin="22 junio 2026", ubicacion="Hotel Marriott, Santiago", terapeutas_count=2, citas_count=0),
        ])
        db.commit()

        # ── Cursos ──
        db.add_all([
            Curso(nombre="Mindfulness para Terapeutas", tipo="Bienestar profesional", profesor="Dr. Andrea Soto", horario="L·X · 01 mar – 30 jun 2026 · 19:00 (60 min)", fecha_inicio="01 mar 2026", fecha_fin="30 jun 2026", hora="19:00", monto="$45.000 / mes", tipo_pago="Mensual", alumnos=8, tag="Mensual", tag_color="sage"),
            Curso(nombre="TCC Avanzada", tipo="Formación clínica", profesor="Dra. Carmen Vidal", horario="V · 12 abr – 14 jun 2026 · 09:00 (90 min)", fecha_inicio="12 abr 2026", fecha_fin="14 jun 2026", hora="09:00", monto="$180.000", tipo_pago="Pago único", alumnos=12, tag="Pago único", tag_color="blue"),
        ])
        db.commit()

        # ── Klinós: Patrones, preparaciones, historial, notas ──
        db.add_all([
            PatronKlinos(paciente_id=p1.id, patron="Evitación social", frecuencia=5),
            PatronKlinos(paciente_id=p1.id, patron="Autoexigencia", frecuencia=4),
            PatronKlinos(paciente_id=p2.id, patron="Sedentarismo", frecuencia=7),
            PatronKlinos(paciente_id=p5.id, patron="Aislamiento", frecuencia=6),
        ])
        db.commit()

        db.add_all([
            PreparacionSesion(paciente_id=p1.id, item="Revisar tarea de exposición gradual"),
            PreparacionSesion(paciente_id=p1.id, item="Evaluar escala de ansiedad"),
            PreparacionSesion(paciente_id=p2.id, item="Ejercicios de fortalecimiento lumbar"),
            PreparacionSesion(paciente_id=p5.id, item="Escala de depresión de Beck"),
        ])
        db.commit()

        now = "14 abr"
        db.add_all([
            HistorialSesion(paciente_id=p1.id, fecha="07 abr", contenido="El paciente reporta disminución de ansiedad..."),
            HistorialSesion(paciente_id=p1.id, fecha="31 mar", contenido="Se trabajó en identificación de pensamientos automáticos..."),
            HistorialSesion(paciente_id=p5.id, fecha="07 abr", contenido="Primera sesión de evaluación..."),
        ])
        db.commit()

        db.add_all([
            NotaClinica(paciente_id=p1.id, contenido="Evaluación inicial: Paciente presenta síntomas de ansiedad generalizada con evitación social significativa. Se recomienda terapia cognitivo-conductual con exposición gradual."),
            NotaClinica(paciente_id=p5.id, contenido="Paciente refiere estado de ánimo deprimido desde hace 3 meses. Se aplica escala PHQ-9 con puntuación de 18 (depresión moderada-grave)."),
        ])
        db.commit()

        # ── Sesiones cerradas (para intensidad / carga) ──
        db.add_all([
            RegistroSesion(cita_id=1, notas="Sesión de psicoterapia", analisis="Paciente con ansiedad moderada", intensidad="media", estado="cerrado", cerrado_at=None),
            RegistroSesion(cita_id=2, notas="Sesión de kinesiología", analisis="Progreso en movilidad", intensidad="baja", estado="cerrado", cerrado_at=None),
            RegistroSesion(cita_id=3, notas="Ejercicios fonológicos", analisis="Mejoría en pronunciación", intensidad="media", estado="cerrado", cerrado_at=None),
            RegistroSesion(cita_id=4, notas="Sesión profunda", analisis="Alta carga emocional", intensidad="alta", estado="cerrado", cerrado_at=None),
        ])
        db.commit()

        # ── Carga emocional ──
        db.add(CargaEmocional(estado="Bien", nota="", sesiones_semana=8, alta_intensidad=4, fecha="15 abr 2026"))
        db.commit()

        # ── Usuarios ──
        def hp(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        admin_perms = json.dumps({
            "dashboard": "view_edit", "agenda": "view_edit", "reservar": "view_edit",
            "pacientes": "view_edit", "terapeutas": "view_edit",
            "citas": "view_edit", "finanzas": "view_edit", "eventos": "view_edit",
            "cursos": "view_edit", "klinos": "view_edit",
            "config": "view_edit", "historial": "view_edit", "carga": "view_edit"
        })
        terapeuta_perms = json.dumps({
            "dashboard": "view", "agenda": "view_edit", "reservar": "view_edit",
            "pacientes": "view_edit", "terapeutas": "view",
            "citas": "view_edit", "finanzas": "view", "eventos": "view",
            "cursos": "view", "klinos": "view_edit",
            "config": "hide", "historial": "view_edit", "carga": "view_edit"
        })
        recepcion_perms = json.dumps({
            "dashboard": "view", "agenda": "view_edit", "reservar": "view_edit",
            "pacientes": "view_edit", "terapeutas": "view",
            "citas": "view_edit", "finanzas": "view_edit", "eventos": "view",
            "cursos": "view", "klinos": "hide",
            "config": "hide", "historial": "hide", "carga": "hide"
        })

        db.add_all([
            User(username="hugo", password_hash=hp("admin123"), nombre="Hugo Admin", email="hugo@klinos.cl", rol="admin", permissions=admin_perms),
            User(username="maria", password_hash=hp("klinos2025"), nombre="Dra. María González", email="maria.gonzalez@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="pedro", password_hash=hp("klinos2025"), nombre="Dr. Pedro Silva", email="pedro.silva@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="ana", password_hash=hp("klinos2025"), nombre="Dra. Ana López", email="ana.lopez@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="carlos", password_hash=hp("klinos2025"), nombre="Dr. Carlos Ruiz", email="carlos.ruiz@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="recepcion", password_hash=hp("klinos2025"), nombre="Recepcionista", email="recepcion@klinos.cl", rol="recepcion", permissions=recepcion_perms),
        ])
        db.commit()

        # ── Link users to terapeutas ──
        for t in db.query(Terapeuta).all():
            user = db.query(User).filter(User.email == t.email).first()
            if user and not t.user_id:
                t.user_id = user.id
        db.commit()

    finally:
        db.close()
