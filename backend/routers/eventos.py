from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Evento
from schemas import EventoCreate, EventoOut

router = APIRouter(prefix="/api/eventos", tags=["eventos"])


@router.get("", response_model=list[EventoOut])
def list_eventos(db: Session = Depends(get_db)):
    return db.query(Evento).order_by(Evento.fecha_inicio).all()


@router.post("", response_model=EventoOut)
def create_evento(data: EventoCreate, db: Session = Depends(get_db)):
    e = Evento(**data.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
