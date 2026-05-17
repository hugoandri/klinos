from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import TipoTerapia
from schemas import TipoTerapiaCreate, TipoTerapiaUpdate, TipoTerapiaOut

router = APIRouter(prefix="/api/tipos-terapia", tags=["tipos-terapia"])


@router.get("", response_model=list[TipoTerapiaOut])
def listar_tipos(db: Session = Depends(get_db)):
    return db.query(TipoTerapia).order_by(TipoTerapia.nombre).all()


@router.get("/{tipo_id}", response_model=TipoTerapiaOut)
def obtener_tipo(tipo_id: int, db: Session = Depends(get_db)):
    t = db.query(TipoTerapia).filter(TipoTerapia.id == tipo_id).first()
    if not t:
        raise HTTPException(404, "Tipo de terapia no encontrado")
    return t


@router.post("", response_model=TipoTerapiaOut)
def crear_tipo(data: TipoTerapiaCreate, db: Session = Depends(get_db)):
    t = TipoTerapia(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/{tipo_id}", response_model=TipoTerapiaOut)
def actualizar_tipo(tipo_id: int, data: TipoTerapiaUpdate, db: Session = Depends(get_db)):
    t = db.query(TipoTerapia).filter(TipoTerapia.id == tipo_id).first()
    if not t:
        raise HTTPException(404, "Tipo de terapia no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{tipo_id}")
def eliminar_tipo(tipo_id: int, db: Session = Depends(get_db)):
    t = db.query(TipoTerapia).filter(TipoTerapia.id == tipo_id).first()
    if not t:
        raise HTTPException(404, "Tipo de terapia no encontrado")
    db.delete(t)
    db.commit()
    return {"ok": True}
