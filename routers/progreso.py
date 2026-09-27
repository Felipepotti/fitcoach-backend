from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from database import progreso_collection, rutinas_collection
from models import ProgresoRegistrar, ProgresoRespuesta
from security import requerir_rol
from database import progreso_collection, rutinas_collection, usuarios_collection
from models import ProgresoRegistrar, ProgresoRespuesta, ProgresoEntrenador
from collections import defaultdict
from datetime import timedelta

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


@router.get("/mis-alumnos", response_model=list[ProgresoEntrenador])
async def progreso_de_mis_alumnos(usuario_actual: dict = Depends(requerir_rol("entrenador"))):
    # Busca los alumnos vinculados a este entrenador y arma un mapa id -> nombre
    cursor_alumnos = usuarios_collection.find({
        "rol": "alumno",
        "entrenador_id": usuario_actual["id"],
    })
    mapa_nombres = {}
    async for alumno in cursor_alumnos:
        mapa_nombres[str(alumno["_id"])] = alumno["nombre"]

    if not mapa_nombres:
        return []

    cursor_progreso = progreso_collection.find(
        {"alumno_id": {"$in": list(mapa_nombres.keys())}}
    ).sort("fecha_completado", -1).limit(30)

    resultado = []
    async for registro in cursor_progreso:
        resultado.append(ProgresoEntrenador(
            id=str(registro["_id"]),
            alumno_id=registro["alumno_id"],
            nombre_alumno=mapa_nombres.get(registro["alumno_id"], "Alumno"),
            rutina_id=registro["rutina_id"],
            nombre_rutina=registro["nombre_rutina"],
            fecha_completado=registro["fecha_completado"],
            comentario=registro.get("comentario"),
        ))
    return resultado

@router.get("/resumen-semanal")
async def resumen_semanal(usuario_actual: dict = Depends(requerir_rol("alumno"))):
    hace_8_semanas = datetime.utcnow() - timedelta(weeks=8)

    cursor = progreso_collection.find({
        "alumno_id": usuario_actual["id"],
        "fecha_completado": {"$gte": hace_8_semanas},
    })

    conteo_por_semana = defaultdict(int)
    async for registro in cursor:
        fecha = registro["fecha_completado"]
        # "año-semana", ej. "2026-35" — agrupa por semana calendario (lunes a domingo)
        clave_semana = f"{fecha.isocalendar()[0]}-{fecha.isocalendar()[1]:02d}"
        conteo_por_semana[clave_semana] += 1

    # Genera las últimas 8 semanas en orden, aunque algunas tengan 0 entrenamientos
    semanas = []
    for i in range(7, -1, -1):
        fecha_referencia = datetime.utcnow() - timedelta(weeks=i)
        clave = f"{fecha_referencia.isocalendar()[0]}-{fecha_referencia.isocalendar()[1]:02d}"
        semanas.append({
            "semana": clave,
            "entrenamientos": conteo_por_semana.get(clave, 0),
        })

    return semanas