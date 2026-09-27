from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from database import usuarios_collection
from models import VincularAlumno
from security import requerir_rol

router = APIRouter(prefix="/entrenador", tags=["Entrenador"])


@router.get("/mis-alumnos")
async def mis_alumnos(usuario_actual: dict = Depends(requerir_rol("entrenador"))):
    cursor = usuarios_collection.find({
        "rol": "alumno",
        "entrenador_id": usuario_actual["id"],
    })
    alumnos = []
    async for alumno in cursor:
        alumnos.append({
            "id": str(alumno["_id"]),
            "nombre": alumno["nombre"],
            "email": alumno["email"],
            "activo": alumno.get("activo", True),
        })
    return {"alumnos": alumnos}


@router.post("/vincular-alumno", status_code=status.HTTP_200_OK)
async def vincular_alumno(
    datos: VincularAlumno,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    alumno = await usuarios_collection.find_one({
        "email": datos.email,
        "rol": "alumno",
    })

    if not alumno:
        raise HTTPException(
            status_code=404,
            detail="No existe un alumno registrado con ese email",
        )

    if alumno.get("entrenador_id") == usuario_actual["id"]:
        raise HTTPException(
            status_code=400,
            detail="Ese alumno ya está vinculado contigo",
        )

    await usuarios_collection.update_one(
        {"_id": alumno["_id"]},
        {"$set": {"entrenador_id": usuario_actual["id"], "activo": True}},
    )

    return {
        "mensaje": "Alumno vinculado correctamente",
        "alumno": {
            "id": str(alumno["_id"]),
            "nombre": alumno["nombre"],
            "email": alumno["email"],
        },
    }


@router.patch("/alumnos/{alumno_id}/estado")
async def cambiar_estado_alumno(
    alumno_id: str,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    alumno = await usuarios_collection.find_one({
        "_id": ObjectId(alumno_id),
        "rol": "alumno",
        "entrenador_id": usuario_actual["id"],
    })
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado o no está vinculado contigo")

    nuevo_estado = not alumno.get("activo", True)

    await usuarios_collection.update_one(
        {"_id": alumno["_id"]},
        {"$set": {"activo": nuevo_estado}},
    )

    return {
        "id": str(alumno["_id"]),
        "nombre": alumno["nombre"],
        "activo": nuevo_estado,
    }