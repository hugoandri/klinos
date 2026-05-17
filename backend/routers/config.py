from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Configuracion
from schemas import ConfigUpdate

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
def get_config(db: Session = Depends(get_db)):
    configs = db.query(Configuracion).all()
    return {c.key: c.value for c in configs}


@router.put("")
def update_config(data: ConfigUpdate, db: Session = Depends(get_db)):
    for key, value in data.settings.items():
        existing = db.query(Configuracion).filter(Configuracion.key == key).first()
        if existing:
            existing.value = value
        else:
            db.add(Configuracion(key=key, value=value))
    db.commit()
    configs = db.query(Configuracion).all()
    return {c.key: c.value for c in configs}
