from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Curso
from schemas import CursoCreate, CursoOut

router = APIRouter(prefix="/api/cursos", tags=["cursos"])


@router.get("", response_model=list[CursoOut])
def list_cursos(db: Session = Depends(get_db)):
    return db.query(Curso).order_by(Curso.nombre).all()


@router.post("", response_model=CursoOut)
def create_curso(data: CursoCreate, db: Session = Depends(get_db)):
    c = Curso(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c
