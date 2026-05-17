from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Finanza
from schemas import FinanzaCreate, FinanzaOut

router = APIRouter(prefix="/api/finanzas", tags=["finanzas"])


@router.get("", response_model=list[FinanzaOut])
def list_finanzas(estado: str = None, db: Session = Depends(get_db)):
    q = db.query(Finanza)
    if estado:
        q = q.filter(Finanza.estado == estado)
    return q.order_by(Finanza.fecha.desc()).all()


@router.post("", response_model=FinanzaOut)
def create_finanza(data: FinanzaCreate, db: Session = Depends(get_db)):
    f = Finanza(**data.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f
