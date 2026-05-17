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
    Miembro,
    NotaClinica,
    Paciente,
    PatronKlinos,
    PreparacionSesion,
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

        # ── Tipos de Terapia ──
        db.add_all([
            TipoTerapia(nombre="Psicoterapia Individual", descripcion="Sesión individual de psicoterapia", duracion_default=50, color="#3E8E6B"),
            TipoTerapia(nombre="Kinesiología", descripcion="Terapia física y rehabilitación", duracion_default=45, color="#D4893B"),
            TipoTerapia(nombre="Fonoaudiología", descripcion="Terapia del lenguaje y comunicación", duracion_default=30, color="#C25A6E"),
            TipoTerapia(nombre="Terapia Ocupacional", descripcion="Rehabilitación de actividades diarias", duracion_default=60, color="#6C5CE7"),
            TipoTerapia(nombre="Evaluación Psicológica", descripcion="Evaluación diagnóstica inicial", duracion_default=50, color="#3B7DBF"),
        ])
        db.commit()

        # ── Pacientes ──
        p1 = Paciente(nombre="Juan Pérez", email="juan@email.com", telefono="+56 9 1234 5678", rut="12.345.678-9", edad=35, fecha_inicio="02 oct 2025", diagnostico="Ansiedad generalizada", terapeuta_id=t1.id, status="Trabajo activo", sesiones_total=12, ultima_sesion="14 abr")
        p2 = Paciente(nombre="María Soto", email="maria@email.com", telefono="+56 9 2345 6789", rut="15.678.901-2", edad=28, fecha_inicio="15 oct 2025", diagnostico="Rehabilitación", terapeuta_id=t2.id, status="Trabajo activo", sesiones_total=8, ultima_sesion="13 abr")
        p3 = Paciente(nombre="Carlos Muñoz", email="carlos@email.com", telefono="+56 9 3456 7890", rut="18.901.234-5", edad=42, fecha_inicio="20 sep 2025", diagnostico="Lenguaje", terapeuta_id=t3.id, status="En cierre", sesiones_total=20, ultima_sesion="12 abr")
        p4 = Paciente(nombre="Ana Fernández", email="ana@email.com", telefono="+56 9 4567 8901", rut="14.567.890-1", edad=31, fecha_inicio="01 nov 2025", diagnostico="Exploración inicial", terapeuta_id=t2.id, status="Exploración", sesiones_total=5, ultima_sesion="10 abr")
        p5 = Paciente(nombre="Roberto Díaz", email="roberto@email.com", telefono="+56 9 5678 9012", rut="16.789.012-3", edad=45, fecha_inicio="10 oct 2025", diagnostico="TCC", terapeuta_id=t1.id, status="Trabajo activo", sesiones_total=15, ultima_sesion="11 abr")
        p6 = Paciente(nombre="Valentina Rojas", email="valentina@email.com", telefono="+56 9 6789 0123", rut="20.123.456-7", edad=26, fecha_inicio="01 abr 2026", diagnostico="Exploración inicial", terapeuta_id=t1.id, status="Exploración", sesiones_total=3, ultima_sesion="09 abr")
        db.add_all([p1, p2, p3, p4, p5, p6])
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

        # Citas pasadas
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

        # ── Miembros ──
        db.add_all([
            Miembro(nombre="Dra. María González", email="maria.gonzalez@centro.cl", rol="Admin", fecha_ingreso="01 oct 2025", avatar_color="blue"),
            Miembro(nombre="Dr. Pedro Silva", email="pedro.silva@centro.cl", rol="Terapeuta", fecha_ingreso="05 oct 2025", avatar_color="sage"),
            Miembro(nombre="Dra. Ana López", email="ana.lopez@centro.cl", rol="Terapeuta", fecha_ingreso="10 oct 2025", avatar_color="rose"),
            Miembro(nombre="Dr. Carlos Ruiz", email="carlos.ruiz@centro.cl", rol="Terapeuta", fecha_ingreso="12 oct 2025", avatar_color="amber"),
        ])
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
            PatronKlinos(paciente_id=p1.id, patron="Autocrítica", frecuencia=4),
            PatronKlinos(paciente_id=p1.id, patron="Vínculos", frecuencia=3),
            PatronKlinos(paciente_id=p1.id, patron="Trabajo", frecuencia=2),
            PatronKlinos(paciente_id=p5.id, patron="Resistencia", frecuencia=4),
        ])
        db.commit()

        db.add_all([
            PreparacionSesion(paciente_id=p1.id, item="Retomar autorregistros de la semana", completado=True),
            PreparacionSesion(paciente_id=p1.id, item="Revisar patrón de exposición gradual", completado=True),
            PreparacionSesion(paciente_id=p1.id, item="Explorar situación laboral pendiente", completado=False),
            PreparacionSesion(paciente_id=p1.id, item="Evaluar calidad de sueño esta semana", completado=False),
        ])
        db.commit()

        db.add_all([
            HistorialSesion(paciente_id=p1.id, fecha="14 abr", contenido="Exposición gradual. Buena apertura. Reporta ansiedad baja esta semana. Tarea: continuar autorregistros."),
            HistorialSesion(paciente_id=p1.id, fecha="07 abr", contenido="Trabajó autocrítica en vínculo laboral. Técnica de distanciamiento cognitivo aplicada."),
            HistorialSesion(paciente_id=p1.id, fecha="31 mar", contenido="Sesión más difícil. Resistencia alta. Evitación social más marcada esta semana."),
            HistorialSesion(paciente_id=p1.id, fecha="24 mar", contenido="Avance en identificación de disparadores internos. Primera vez que nombra el patrón por sí mismo."),
        ])
        db.commit()

        db.add(NotaClinica(paciente_id=p1.id, contenido="Paciente con ansiedad generalizada. Progreso positivo en las últimas semanas. Tendencia a la evitación en contextos sociales y laborales. La autocrítica sigue siendo un eje central del trabajo terapéutico. Buen nivel de insight."))
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
            "cursos": "view_edit", "miembros": "view_edit", "klinos": "view_edit",
            "config": "view_edit", "historial": "view_edit", "carga": "view_edit"
        })
        terapeuta_perms = json.dumps({
            "dashboard": "view", "agenda": "view_edit", "reservar": "view_edit",
            "pacientes": "view_edit", "terapeutas": "view",
            "citas": "view_edit", "finanzas": "view", "eventos": "view",
            "cursos": "view", "miembros": "view", "klinos": "view_edit",
            "config": "hide", "historial": "view_edit", "carga": "view_edit"
        })
        recepcion_perms = json.dumps({
            "dashboard": "view", "agenda": "view_edit", "reservar": "view_edit",
            "pacientes": "view_edit", "terapeutas": "view",
            "citas": "view_edit", "finanzas": "view_edit", "eventos": "view",
            "cursos": "view", "miembros": "view", "klinos": "hide",
            "config": "hide", "historial": "hide", "carga": "hide"
        })

        db.add_all([
            User(username="hugo", password_hash=hp("admin123"), nombre="Hugo Admin", email="hugo@klinos.cl", rol="admin", permissions=admin_perms),
            User(username="maria", password_hash=hp("klinos2025"), nombre="Dra. María González", email="maria.gonzalez@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="pedro", password_hash=hp("klinos2025"), nombre="Dr. Pedro Silva", email="pedro.silva@centro.cl", rol="terapeuta", permissions=terapeuta_perms),
            User(username="recepcion", password_hash=hp("klinos2025"), nombre="Recepcionista", email="recepcion@klinos.cl", rol="recepcion", permissions=recepcion_perms),
        ])
        db.commit()

    finally:
        db.close()
