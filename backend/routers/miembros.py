from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Miembro
from schemas import MiembroCreate, MiembroOut

router = APIRouter(prefix="/api/miembros", tags=["miembros"])


@router.get("", response_model=list[MiembroOut])
def list_miembros(db: Session = Depends(get_db)):
    return db.query(Miembro).order_by(Miembro.nombre).all()


@router.post("", response_model=MiembroOut)
def create_miembro(data: MiembroCreate, db: Session = Depends(get_db)):
    m = Miembro(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{miembro_id}")
def delete_miembro(miembro_id: int, db: Session = Depends(get_db)):
    m = db.query(Miembro).filter(Miembro.id == miembro_id).first()
    if not m:
        return {"ok": False}
    db.delete(m)
    db.commit()
    return {"ok": True}
