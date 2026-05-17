from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Cita, CargaEmocional, Finanza, Paciente, Terapeuta
from schemas import DashboardStats

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    hoy = "15 abr"
    citas_hoy = db.query(Cita).filter(Cita.fecha == hoy).count()
    pacientes_activos = db.query(Paciente).filter(Paciente.status.in_(["Trabajo activo", "Exploración", "En cierre"])).count()
    terapeutas_activos = db.query(Terapeuta).filter(Terapeuta.activo == True).count()

    pagos = db.query(Finanza).filter(Finanza.estado == "Pendiente").all()
    monto_pendiente = sum(p.monto for p in pagos)
    monto_str = f"${monto_pendiente:,}".replace(",", ".")

    return DashboardStats(
        citas_hoy=citas_hoy,
        pacientes_activos=pacientes_activos,
        pagos_pendientes=len(pagos),
        terapeutas_activos=terapeutas_activos,
        monto_pendiente=monto_str,
    )
