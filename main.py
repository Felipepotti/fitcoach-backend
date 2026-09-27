from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routers import auth, entrenador, rutinas, progreso
from routers import auth, entrenador, rutinas, progreso, perfil

app = FastAPI(title="FitCoach API")

origenes_permitidos = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entrenador.router)
app.include_router(rutinas.router)
app.include_router(progreso.router)
app.include_router(perfil.router)


@app.get("/")
def read_root():
    return {"mensaje": "FitCoach API funcionando correctamente"}


@app.get("/test-db")
async def test_db():
    colecciones = await database.list_collection_names()
    return {"conexion": "exitosa", "colecciones": colecciones}