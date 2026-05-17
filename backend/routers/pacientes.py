from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Paciente
from schemas import PacienteCreate, PacienteOut

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


@router.get("", response_model=list[PacienteOut])
def list_pacientes(db: Session = Depends(get_db)):
    return db.query(Paciente).order_by(Paciente.nombre).all()


@router.get("/{paciente_id}", response_model=PacienteOut)
def get_paciente(paciente_id: int, db: Session = Depends(get_db)):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(404, "Paciente no encontrado")
    return p


@router.post("", response_model=PacienteOut)
def create_paciente(data: PacienteCreate, db: Session = Depends(get_db)):
    p = Paciente(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{paciente_id}", response_model=PacienteOut)
def update_paciente(paciente_id: int, data: PacienteCreate, db: Session = Depends(get_db)):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(404, "Paciente no encontrado")
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{paciente_id}")
def delete_paciente(paciente_id: int, db: Session = Depends(get_db)):
    p = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not p:
        raise HTTPException(404, "Paciente no encontrado")
    db.delete(p)
    db.commit()
    return {"ok": True}
