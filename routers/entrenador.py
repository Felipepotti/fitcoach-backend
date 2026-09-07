from fastapi import APIRouter, Depends
from bson import ObjectId

from database import usuarios_collection
from security import requerir_rol

router = APIRouter(prefix="/entrenador", tags=["Entrenador"])

@router.get("/mis-alumnos")
async def mis_alumnos(usuario_actual: dict = Depends(requerir_rol("entrenador"))):
    cursor = usuarios_collection.find({"rol": "alumno"})
    alumnos = []
    async for alumno in cursor:
        alumnos.append({
            "id": str(alumno["_id"]),
            "nombre": alumno["nombre"],
            "email": alumno["email"],
        })
    return {"alumnos": alumnos}