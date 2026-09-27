from datetime import datetime
from fastapi import APIRouter, Depends
from bson import ObjectId

from database import usuarios_collection, peso_historial_collection
from models import DatosFisicos, PerfilFisicoRespuesta, RegistroPeso
from security import requerir_rol

router = APIRouter(prefix="/perfil", tags=["Perfil físico"])


@router.get("/", response_model=PerfilFisicoRespuesta)
async def obtener_perfil(usuario_actual: dict = Depends(requerir_rol("alumno"))):
    usuario = await usuarios_collection.find_one({"_id": ObjectId(usuario_actual["id"])})

    return PerfilFisicoRespuesta(
        peso_kg=usuario.get("peso_kg"),
        altura_cm=usuario.get("altura_cm"),
        edad=usuario.get("edad"),
        sexo=usuario.get("sexo"),
        objetivo=usuario.get("objetivo"),
    )


@router.put("/", response_model=PerfilFisicoRespuesta)
async def actualizar_perfil(
    datos: DatosFisicos,
    usuario_actual: dict = Depends(requerir_rol("alumno")),
):
    await usuarios_collection.update_one(
        {"_id": ObjectId(usuario_actual["id"])},
        {"$set": datos.model_dump()},
    )

    # Cada actualización de peso queda registrada en el historial
    await peso_historial_collection.insert_one({
        "alumno_id": usuario_actual["id"],
        "peso_kg": datos.peso_kg,
        "fecha": datetime.utcnow(),
    })

    return PerfilFisicoRespuesta(**datos.model_dump())


@router.get("/historial-peso", response_model=list[RegistroPeso])
async def historial_peso(usuario_actual: dict = Depends(requerir_rol("alumno"))):
    cursor = peso_historial_collection.find(
        {"alumno_id": usuario_actual["id"]}
    ).sort("fecha", 1)  # orden cronológico ascendente, ideal para graficar

    resultado = []
    async for registro in cursor:
        resultado.append(RegistroPeso(
            id=str(registro["_id"]),
            peso_kg=registro["peso_kg"],
            fecha=registro["fecha"],
        ))
    return resultado


@router.get("/alumno/{alumno_id}", response_model=PerfilFisicoRespuesta)
async def perfil_de_alumno(
    alumno_id: str,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    alumno = await usuarios_collection.find_one({
        "_id": ObjectId(alumno_id),
        "rol": "alumno",
        "entrenador_id": usuario_actual["id"],
    })
    if not alumno:
        return PerfilFisicoRespuesta()

    return PerfilFisicoRespuesta(
        peso_kg=alumno.get("peso_kg"),
        altura_cm=alumno.get("altura_cm"),
        edad=alumno.get("edad"),
        sexo=alumno.get("sexo"),
        objetivo=alumno.get("objetivo"),
    )