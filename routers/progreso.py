from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from database import progreso_collection, rutinas_collection
from models import ProgresoRegistrar, ProgresoRespuesta
from security import requerir_rol

router = APIRouter(prefix="/progreso", tags=["Progreso"])


@router.post("/", response_model=ProgresoRespuesta, status_code=status.HTTP_201_CREATED)
async def registrar_progreso(
    progreso: ProgresoRegistrar,
    usuario_actual: dict = Depends(requerir_rol("alumno")),
):
    rutina = await rutinas_collection.find_one({"_id": ObjectId(progreso.rutina_id)})
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Verifica que la rutina realmente pertenezca a este alumno
    if rutina["alumno_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="Esta rutina no te pertenece")

    nuevo_registro = {
        "alumno_id": usuario_actual["id"],
        "rutina_id": progreso.rutina_id,
        "nombre_rutina": rutina["nombre_rutina"],
        "fecha_completado": datetime.utcnow(),
        "comentario": progreso.comentario,
    }

    resultado = await progreso_collection.insert_one(nuevo_registro)

    return ProgresoRespuesta(
        id=str(resultado.inserted_id),
        alumno_id=nuevo_registro["alumno_id"],
        rutina_id=nuevo_registro["rutina_id"],
        nombre_rutina=nuevo_registro["nombre_rutina"],
        fecha_completado=nuevo_registro["fecha_completado"],
        comentario=nuevo_registro["comentario"],
    )


@router.get("/mi-historial", response_model=list[ProgresoRespuesta])
async def mi_historial(usuario_actual: dict = Depends(requerir_rol("alumno"))):
    cursor = progreso_collection.find(
        {"alumno_id": usuario_actual["id"]}
    ).sort("fecha_completado", -1)  # más reciente primero

    historial = []
    async for registro in cursor:
        historial.append(ProgresoRespuesta(
            id=str(registro["_id"]),
            alumno_id=registro["alumno_id"],
            rutina_id=registro["rutina_id"],
            nombre_rutina=registro["nombre_rutina"],
            fecha_completado=registro["fecha_completado"],
            comentario=registro.get("comentario"),
        ))
    return historial