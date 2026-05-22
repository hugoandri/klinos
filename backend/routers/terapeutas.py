from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from database import get_db
from models import Terapeuta, User
from schemas import TerapeutaCreate, TerapeutaOut, TerapeutaPerfilOut

router = APIRouter(prefix="/api/terapeutas", tags=["terapeutas"])


class CreateUserForTerapeuta(BaseModel):
    username: str
    password: str
    user_rol: str = "terapeuta"


@router.get("", response_model=list[TerapeutaOut])
def list_terapeutas(db: Session = Depends(get_db)):
    return db.query(Terapeuta).order_by(Terapeuta.nombre).all()


@router.get("/perfiles", response_model=list[TerapeutaPerfilOut])
def list_perfiles(db: Session = Depends(get_db)):
    terapeutas = db.query(Terapeuta).order_by(Terapeuta.nombre).all()
    result = []
    for t in terapeutas:
        user = db.query(User).filter(User.id == t.user_id).first() if t.user_id else None
        result.append(TerapeutaPerfilOut(
            id=t.id,
            nombre=t.nombre,
            email=t.email,
            telefono=t.telefono,
            especialidad=t.especialidad,
            horario=t.horario,
            activo=t.activo,
            user_id=t.user_id,
            username=user.username if user else None,
            user_rol=user.rol if user else None,
            created_at=t.created_at,
        ))
    return result


@router.get("/{terapeuta_id}", response_model=TerapeutaOut)
def get_terapeuta(terapeuta_id: int, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    return t


@router.post("", response_model=TerapeutaOut)
def create_terapeuta(data: TerapeutaCreate, db: Session = Depends(get_db)):
    user_id = None
    if data.user_id:
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(400, "Usuario no encontrado")
        if data.password:
            user.password_hash = bcrypt.hash(data.password)
            db.commit()
        user_id = user.id
    elif data.username and data.password:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(400, "El nombre de usuario ya existe")
        user = User(
            username=data.username,
            password_hash=bcrypt.hash(data.password),
            nombre=data.nombre,
            email=data.email,
            rol=data.user_rol,
            permissions=_default_perms(data.user_rol),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    t = Terapeuta(
        nombre=data.nombre,
        email=data.email,
        telefono=data.telefono,
        especialidad=data.especialidad,
        horario=data.horario,
        activo=data.activo,
        user_id=user_id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{terapeuta_id}/create-user")
def create_user_for_terapeuta(terapeuta_id: int, data: CreateUserForTerapeuta, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    if t.user_id:
        raise HTTPException(400, "El terapeuta ya tiene un usuario asociado")
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(400, "El nombre de usuario ya existe")
    user = User(
        username=data.username,
        password_hash=bcrypt.hash(data.password),
        nombre=t.nombre,
        email=t.email,
        rol=data.user_rol,
        permissions=_default_perms(data.user_rol),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    t.user_id = user.id
    db.commit()
    return {"ok": True, "user_id": user.id, "username": user.username}


@router.put("/{terapeuta_id}", response_model=TerapeutaOut)
def update_terapeuta(terapeuta_id: int, data: TerapeutaCreate, db: Session = Depends(get_db)):
    t = db.query(Terapeuta).filter(Terapeuta.id == terapeuta_id).first()
    if not t:
        raise HTTPException(404, "Terapeuta no encontrado")
    for k, v in data.model_dump(exclude={"username", "password", "user_rol"}).items():
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
