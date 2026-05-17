from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Cita, Paciente, Terapeuta
from schemas import CitaCreate, CitaOut

router = APIRouter(prefix="/api/citas", tags=["citas"])


@router.get("", response_model=list[CitaOut])
def list_citas(
    fecha: Optional[str] = None,
    estado: Optional[str] = None,
    terapeuta_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Cita)
    if fecha:
        q = q.filter(Cita.fecha == fecha)
    if estado:
        q = q.filter(Cita.estado == estado)
    if terapeuta_id:
        q = q.filter(Cita.terapeuta_id == terapeuta_id)
    return q.order_by(Cita.hora).all()


@router.get("/{cita_id}", response_model=CitaOut)
def get_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    return cita


@router.post("", response_model=CitaOut)
def create_cita(data: CitaCreate, db: Session = Depends(get_db)):
    cita = Cita(**data.model_dump())
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita


@router.put("/{cita_id}", response_model=CitaOut)
def update_cita(cita_id: int, data: CitaCreate, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    for k, v in data.model_dump().items():
        setattr(cita, k, v)
    db.commit()
    db.refresh(cita)
    return cita


@router.delete("/{cita_id}")
def delete_cita(cita_id: int, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    db.delete(cita)
    db.commit()
    return {"ok": True}
