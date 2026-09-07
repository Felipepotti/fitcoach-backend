from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from database import rutinas_collection, usuarios_collection
from models import RutinaCrear, RutinaRespuesta, RutinaActualizar
from security import requerir_rol, obtener_usuario_actual

router = APIRouter(prefix="/rutinas", tags=["Rutinas"])


@router.post("/", response_model=RutinaRespuesta, status_code=status.HTTP_201_CREATED)
async def crear_rutina(
    rutina: RutinaCrear,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    # Verifica que el alumno_id realmente exista y sea un alumno
    alumno = await usuarios_collection.find_one({
        "_id": ObjectId(rutina.alumno_id),
        "rol": "alumno",
    })
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    nueva_rutina = {
        "entrenador_id": usuario_actual["id"],
        "alumno_id": rutina.alumno_id,
        "nombre_rutina": rutina.nombre_rutina,
        "ejercicios": [ejercicio.model_dump() for ejercicio in rutina.ejercicios],
    }

    resultado = await rutinas_collection.insert_one(nueva_rutina)

    return RutinaRespuesta(
        id=str(resultado.inserted_id),
        entrenador_id=nueva_rutina["entrenador_id"],
        alumno_id=nueva_rutina["alumno_id"],
        nombre_rutina=nueva_rutina["nombre_rutina"],
        ejercicios=rutina.ejercicios,
    )


@router.get("/mis-rutinas", response_model=list[RutinaRespuesta])
async def mis_rutinas(usuario_actual: dict = Depends(requerir_rol("alumno"))):
    cursor = rutinas_collection.find({"alumno_id": usuario_actual["id"]})
    rutinas = []
    async for r in cursor:
        rutinas.append(RutinaRespuesta(
            id=str(r["_id"]),
            entrenador_id=r["entrenador_id"],
            alumno_id=r["alumno_id"],
            nombre_rutina=r["nombre_rutina"],
            ejercicios=r["ejercicios"],
        ))
    return rutinas


@router.get("/{rutina_id}", response_model=RutinaRespuesta)
async def obtener_rutina(
    rutina_id: str,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    rutina = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Solo puede verla el alumno dueño o el entrenador que la creó
    es_dueño = usuario_actual["id"] in (rutina["alumno_id"], rutina["entrenador_id"])
    if not es_dueño:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta rutina")

    return RutinaRespuesta(
        id=str(rutina["_id"]),
        entrenador_id=rutina["entrenador_id"],
        alumno_id=rutina["alumno_id"],
        nombre_rutina=rutina["nombre_rutina"],
        ejercicios=rutina["ejercicios"],
    )

from models import RutinaActualizar  # agrega esto a tu línea de import de models


@router.put("/{rutina_id}", response_model=RutinaRespuesta)
async def actualizar_rutina(
    rutina_id: str,
    cambios: RutinaActualizar,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    rutina = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Solo el entrenador que la creó puede editarla
    if rutina["entrenador_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="No puedes editar rutinas de otro entrenador")

    datos_actualizados = {}
    if cambios.nombre_rutina is not None:
        datos_actualizados["nombre_rutina"] = cambios.nombre_rutina
    if cambios.ejercicios is not None:
        datos_actualizados["ejercicios"] = [e.model_dump() for e in cambios.ejercicios]

    if not datos_actualizados:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    await rutinas_collection.update_one(
        {"_id": ObjectId(rutina_id)},
        {"$set": datos_actualizados},
    )

    rutina_actualizada = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})

    return RutinaRespuesta(
        id=str(rutina_actualizada["_id"]),
        entrenador_id=rutina_actualizada["entrenador_id"],
        alumno_id=rutina_actualizada["alumno_id"],
        nombre_rutina=rutina_actualizada["nombre_rutina"],
        ejercicios=rutina_actualizada["ejercicios"],
    )

@router.put("/{rutina_id}", response_model=RutinaRespuesta)
async def actualizar_rutina(
    rutina_id: str,
    cambios: RutinaActualizar,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    rutina = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    # Solo el entrenador que la creó puede editarla
    if rutina["entrenador_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="No puedes editar rutinas de otro entrenador")

    datos_actualizados = {}
    if cambios.nombre_rutina is not None:
        datos_actualizados["nombre_rutina"] = cambios.nombre_rutina
    if cambios.ejercicios is not None:
        datos_actualizados["ejercicios"] = [e.model_dump() for e in cambios.ejercicios]

    if not datos_actualizados:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    await rutinas_collection.update_one(
        {"_id": ObjectId(rutina_id)},
        {"$set": datos_actualizados},
    )

    rutina_actualizada = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})

    return RutinaRespuesta(
        id=str(rutina_actualizada["_id"]),
        entrenador_id=rutina_actualizada["entrenador_id"],
        alumno_id=rutina_actualizada["alumno_id"],
        nombre_rutina=rutina_actualizada["nombre_rutina"],
        ejercicios=rutina_actualizada["ejercicios"],
    )


@router.delete("/{rutina_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_rutina(
    rutina_id: str,
    usuario_actual: dict = Depends(requerir_rol("entrenador")),
):
    rutina = await rutinas_collection.find_one({"_id": ObjectId(rutina_id)})
    if not rutina:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    if rutina["entrenador_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="No puedes eliminar rutinas de otro entrenador")

    await rutinas_collection.delete_one({"_id": ObjectId(rutina_id)})
    return None