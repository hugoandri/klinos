from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Terapeuta(Base):
    __tablename__ = "terapeutas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200))
    telefono: Mapped[str] = mapped_column(String(50), default="")
    especialidad: Mapped[str] = mapped_column(String(200), default="")
    horario: Mapped[str] = mapped_column(String(100), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    pacientes: Mapped[list["Paciente"]] = relationship("Paciente", back_populates="terapeuta")
    citas: Mapped[list["Cita"]] = relationship("Cita", back_populates="terapeuta")


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    rut: Mapped[str] = mapped_column(String(20), default="")
    edad: Mapped[int] = mapped_column(Integer, default=0)
    fecha_inicio: Mapped[str] = mapped_column(String(20), default="")
    diagnostico: Mapped[str] = mapped_column(String(300), default="")
    terapeuta_id: Mapped[int] = mapped_column(Integer, ForeignKey("terapeutas.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Trabajo activo")
    sesiones_total: Mapped[int] = mapped_column(Integer, default=0)
    ultima_sesion: Mapped[str] = mapped_column(String(20), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    terapeuta: Mapped["Terapeuta"] = relationship("Terapeuta", back_populates="pacientes")
    citas: Mapped[list["Cita"]] = relationship("Cita", back_populates="paciente")
    notas_clinicas: Mapped[list["NotaClinica"]] = relationship("NotaClinica", back_populates="paciente")
    patrones: Mapped[list["PatronKlinos"]] = relationship("PatronKlinos", back_populates="paciente")
    preparaciones: Mapped[list["PreparacionSesion"]] = relationship("PreparacionSesion", back_populates="paciente")
    historial_sesiones: Mapped[list["HistorialSesion"]] = relationship("HistorialSesion", back_populates="paciente")


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"))
    terapeuta_id: Mapped[int] = mapped_column(Integer, ForeignKey("terapeutas.id"))
    fecha: Mapped[str] = mapped_column(String(20))
    hora: Mapped[str] = mapped_column(String(10))
    duracion: Mapped[int] = mapped_column(Integer, default=50)
    tipo_sesion: Mapped[str] = mapped_column(String(100), default="")
    sala: Mapped[str] = mapped_column(String(20), default="")
    estado: Mapped[str] = mapped_column(String(30), default="confirmada")
    notas: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="citas")
    terapeuta: Mapped["Terapeuta"] = relationship("Terapeuta", back_populates="citas")


class Finanza(Base):
    __tablename__ = "finanzas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente: Mapped[str] = mapped_column(String(200), default="")
    terapeuta: Mapped[str] = mapped_column(String(200), default="")
    tipo: Mapped[str] = mapped_column(String(100), default="")
    fecha: Mapped[str] = mapped_column(String(20))
    monto: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20), default="Pendiente")


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    fecha_inicio: Mapped[str] = mapped_column(String(20))
    fecha_fin: Mapped[str] = mapped_column(String(20))
    ubicacion: Mapped[str] = mapped_column(String(300), default="")
    terapeutas_count: Mapped[int] = mapped_column(Integer, default=0)
    citas_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[str] = mapped_column(String(100), default="")
    profesor: Mapped[str] = mapped_column(String(200), default="")
    horario: Mapped[str] = mapped_column(String(200), default="")
    fecha_inicio: Mapped[str] = mapped_column(String(20))
    fecha_fin: Mapped[str] = mapped_column(String(20))
    hora: Mapped[str] = mapped_column(String(50), default="")
    monto: Mapped[str] = mapped_column(String(50), default="")
    tipo_pago: Mapped[str] = mapped_column(String(50), default="")
    alumnos: Mapped[int] = mapped_column(Integer, default=0)
    tag: Mapped[str] = mapped_column(String(50), default="")
    tag_color: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Miembro(Base):
    __tablename__ = "miembros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200))
    rol: Mapped[str] = mapped_column(String(50), default="Terapeuta")
    fecha_ingreso: Mapped[str] = mapped_column(String(20))
    avatar_color: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class NotaClinica(Base):
    __tablename__ = "notas_clinicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"))
    contenido: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="notas_clinicas")


class PatronKlinos(Base):
    __tablename__ = "patrones_klinos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"))
    patron: Mapped[str] = mapped_column(String(200))
    frecuencia: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="patrones")


class PreparacionSesion(Base):
    __tablename__ = "preparaciones_sesion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"))
    item: Mapped[str] = mapped_column(String(300))
    completado: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="preparaciones")


class HistorialSesion(Base):
    __tablename__ = "historial_sesiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"))
    fecha: Mapped[str] = mapped_column(String(20))
    contenido: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="historial_sesiones")


class CargaEmocional(Base):
    __tablename__ = "carga_emocional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estado: Mapped[str] = mapped_column(String(20), default="Bien")
    nota: Mapped[str] = mapped_column(Text, default="")
    sesiones_semana: Mapped[int] = mapped_column(Integer, default=0)
    alta_intensidad: Mapped[int] = mapped_column(Integer, default=0)
    fecha: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


# ─── Users / Auth ───
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    nombre: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), default="")
    rol: Mapped[str] = mapped_column(String(50), default="terapeuta")
    auth_token: Mapped[str] = mapped_column(String(200), default="")
    permissions: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


# ─── Configuracion ───
class Configuracion(Base):
    __tablename__ = "configuracion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, default="")


# ─── Registro de Sesiones ───
class RegistroSesion(Base):
    __tablename__ = "registro_sesion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cita_id: Mapped[int] = mapped_column(Integer, index=True)
    notas: Mapped[str] = mapped_column(Text, default="")
    analisis: Mapped[str] = mapped_column(Text, default="")
    intensidad: Mapped[str] = mapped_column(String(50), default="")
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    cerrado_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ─── Tipo de Terapia ───
class TipoTerapia(Base):
    __tablename__ = "tipos_terapia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    duracion_default: Mapped[int] = mapped_column(Integer, default=50)
    color: Mapped[str] = mapped_column(String(20), default="sage")
    activo: Mapped[bool] = mapped_column(Integer, default=True)
