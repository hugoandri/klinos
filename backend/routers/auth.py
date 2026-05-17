import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import LoginRequest, LoginResponse, RegisterRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "No autenticado")
    token = auth.replace("Bearer ", "")
    user = db.query(User).filter(User.auth_token == token).first()
    if not user:
        raise HTTPException(401, "Token inválido")
    return user


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password_hash != hash_password(data.password):
        raise HTTPException(401, "Credenciales inválidas")
    token = secrets.token_hex(32)
    user.auth_token = token
    db.commit()
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.post("/register", response_model=UserOut)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(400, "El username ya existe")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        nombre=data.nombre,
        email=data.email,
        rol=data.rol,
        permissions=data.permissions,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.auth_token = ""
    db.commit()
    return {"ok": True}


@router.get("/users", response_model=list[UserOut])
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.rol != "admin":
        raise HTTPException(403, "Se requiere rol admin")
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.rol != "admin":
        raise HTTPException(403, "Se requiere rol admin")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    return UserOut.model_validate(u)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.rol != "admin":
        raise HTTPException(403, "Se requiere rol admin")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    if "rol" in data:
        u.rol = data["rol"]
    if "permissions" in data:
        u.permissions = data["permissions"]
    db.commit()
    db.refresh(u)
    return UserOut.model_validate(u)
