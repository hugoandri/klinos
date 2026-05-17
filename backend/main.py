from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import (
    auth,
    citas,
    config,
    cursos,
    dashboard,
    eventos,
    finanzas,
    klinos,
    miembros,
    pacientes,
    terapeutas,
    terapias,
)
from seed import seed_data

app = FastAPI(title="Klinós API", version="1.0.0")

Base.metadata.create_all(bind=engine)

seed_data()

app.include_router(auth.router)
app.include_router(config.router)
app.include_router(dashboard.router)
app.include_router(pacientes.router)
app.include_router(terapeutas.router)
app.include_router(citas.router)
app.include_router(finanzas.router)
app.include_router(eventos.router)
app.include_router(cursos.router)
app.include_router(miembros.router)
app.include_router(klinos.router)
app.include_router(terapias.router)

static_dir = Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
