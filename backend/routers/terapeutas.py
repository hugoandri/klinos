from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Terapeuta
from schemas import TerapeutaCreate, TerapeutaOut

router = APIRouter(prefix="/api/terapeutas", tags=["terapeutas"])


@router.get("", response_model=list[TerapeutaOut])
def list_terapeutas(db: Session = Depends(get_db)):
    return db.query(Terapeuta).order_by(Terapeuta.nombre).all()


@router.get("/{terapeuta_id}", response_model=TerapeutaOut)
def get_terapeuta(terapeuta_id: int, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    return t


@router.post("", response_model=TerapeutaOut)
def create_terapeuta(data: TerapeutaCreate, db: Session = Depends(get_db)):
    t = Terapeuta(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/{terapeuta_id}", response_model=TerapeutaOut)
def update_terapeuta(terapeuta_id: int, data: TerapeutaCreate, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{terapeuta_id}")
def delete_terapeuta(terapeuta_id: int, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    db.delete(t)
    db.commit()
    return {"ok": True}
