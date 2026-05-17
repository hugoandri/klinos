from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TerapeutaBase(BaseModel):
    nombre: str
    email: str = ""
    telefono: str = ""
    especialidad: str = ""
    horario: str = ""
    activo: bool = True


class TerapeutaCreate(TerapeutaBase):
    pass


class TerapeutaOut(TerapeutaBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PacienteBase(BaseModel):
    nombre: str
    email: str = ""
    telefono: str = ""
    rut: str = ""
    edad: int = 0
    fecha_inicio: str = ""
    diagnostico: str = ""
    terapeuta_id: Optional[int] = None
    status: str = "Trabajo activo"
    sesiones_total: int = 0
    ultima_sesion: str = ""


class PacienteCreate(PacienteBase):
    pass


class PacienteOut(PacienteBase):
    id: int
    created_at: Optional[datetime] = None
    terapeuta: Optional[TerapeutaOut] = None

    class Config:
        from_attributes = True


class CitaBase(BaseModel):
    paciente_id: int
    terapeuta_id: int
    fecha: str
    hora: str
    duracion: int = 50
    tipo_sesion: str = ""
    sala: str = ""
    estado: str = "confirmada"
    notas: str = ""


class CitaCreate(CitaBase):
    pass


class CitaOut(CitaBase):
    id: int
    created_at: Optional[datetime] = None
    paciente: Optional[PacienteOut] = None
    terapeuta: Optional[TerapeutaOut] = None

    class Config:
        from_attributes = True


class FinanzaBase(BaseModel):
    paciente: str = ""
    terapeuta: str = ""
    tipo: str = ""
    fecha: str
    monto: int
    estado: str = "Pendiente"


class FinanzaCreate(FinanzaBase):
    pass


class FinanzaOut(FinanzaBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventoBase(BaseModel):
    nombre: str
    descripcion: str = ""
    fecha_inicio: str
    fecha_fin: str
    ubicacion: str = ""
    terapeutas_count: int = 0
    citas_count: int = 0


class EventoCreate(EventoBase):
    pass


class EventoOut(EventoBase):
    id: int

    class Config:
        from_attributes = True


class CursoBase(BaseModel):
    nombre: str
    tipo: str = ""
    profesor: str = ""
    horario: str = ""
    fecha_inicio: str = ""
    fecha_fin: str = ""
    hora: str = ""
    monto: str = ""
    tipo_pago: str = ""
    alumnos: int = 0
    tag: str = ""
    tag_color: str = ""


class CursoCreate(CursoBase):
    pass


class CursoOut(CursoBase):
    id: int

    class Config:
        from_attributes = True


class MiembroBase(BaseModel):
    nombre: str
    email: str
    rol: str = "Terapeuta"
    fecha_ingreso: str = ""
    avatar_color: str = ""


class MiembroCreate(MiembroBase):
    pass


class MiembroOut(MiembroBase):
    id: int

    class Config:
        from_attributes = True


class NotaClinicaBase(BaseModel):
    paciente_id: int
    contenido: str


class NotaClinicaCreate(NotaClinicaBase):
    pass


class NotaClinicaOut(NotaClinicaBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatronKlinosOut(BaseModel):
    id: int
    paciente_id: int
    patron: str
    frecuencia: int

    class Config:
        from_attributes = True


class PreparacionOut(BaseModel):
    id: int
    paciente_id: int
    item: str
    completado: bool

    class Config:
        from_attributes = True


class HistorialSesionOut(BaseModel):
    id: int
    paciente_id: int
    fecha: str
    contenido: str

    class Config:
        from_attributes = True


class CargaEmocionalOut(BaseModel):
    id: int
    estado: str
    nota: str
    sesiones_semana: int
    alta_intensidad: int
    fecha: str

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    citas_hoy: int
    pacientes_activos: int
    pagos_pendientes: int
    terapeutas_activos: int
    monto_pendiente: str


# ─── Auth ───
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    nombre: str
    email: str = ""
    rol: str = "terapeuta"
    permissions: str = "{}"


class UserOut(BaseModel):
    id: int
    username: str
    nombre: str
    email: str
    rol: str
    permissions: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserOut


# ─── Config ───
class ConfigUpdate(BaseModel):
    settings: dict[str, str]


# ─── Groq Chat ───
class ChatRequest(BaseModel):
    message: str
    paciente_id: int = 0


class ChatResponse(BaseModel):
    reply: str


# ─── Registro Sesion ───
class RegistroSesionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cita_id: int
    notas: str = ""
    analisis: str = ""
    recomendaciones: str = ""
    patologias: str = ""
    intensidad: str = ""
    estado: str = "pendiente"
    created_at: datetime | None = None
    cerrado_at: datetime | None = None


class NotasUpdate(BaseModel):
    notas: str


class TipoTerapiaCreate(BaseModel):
    nombre: str
    descripcion: str = ""
    duracion_default: int = 50
    color: str = "sage"
    activo: bool = True


class TipoTerapiaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    duracion_default: int | None = None
    color: str | None = None
    activo: bool | None = None


class TipoTerapiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    descripcion: str = ""
    duracion_default: int = 50
    color: str = "sage"
    activo: bool = True


class RegistroSesionCreate(BaseModel):
    cita_id: int


class NotasUpdate(BaseModel):
    notas: str
