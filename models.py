from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from typing import List
from datetime import datetime

class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=6)
    rol: Literal["entrenador", "alumno"]

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioRespuesta(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str


class Ejercicio(BaseModel):
    nombre_ejercicio: str
    grupo_muscular: str
    series: int = Field(gt=0)
    repeticiones: int = Field(gt=0)
    descanso_segundos: int = Field(ge=0)
    notas: Optional[str] = None

class RutinaCrear(BaseModel):
    alumno_id: str
    nombre_rutina: str
    ejercicios: List[Ejercicio]

class RutinaRespuesta(BaseModel):
    id: str
    entrenador_id: str
    alumno_id: str
    nombre_rutina: str
    ejercicios: List[Ejercicio]

class ProgresoRegistrar(BaseModel):
    rutina_id: str
    comentario: Optional[str] = None

class ProgresoRespuesta(BaseModel):
    id: str
    alumno_id: str
    rutina_id: str
    nombre_rutina: str
    fecha_completado: datetime
    comentario: Optional[str] = None

class RutinaActualizar(BaseModel):
    nombre_rutina: Optional[str] = None
    ejercicios: Optional[List[Ejercicio]] = None    