from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from typing import List
from datetime import datetime

class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)
    email: EmailStr = Field(max_length=60)
    password: str = Field(min_length=6, max_length=72)
    rol: Literal["entrenador", "alumno"]

class VincularAlumno(BaseModel):
    email: EmailStr = Field(max_length=120)

class UsuarioLogin(BaseModel):
    email: EmailStr = Field(max_length=60)
    password: str = Field(min_length=1, max_length=72)

class UsuarioRespuesta(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str


from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional, List
from datetime import datetime


class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=6, max_length=72)
    rol: Literal["entrenador", "alumno"]


class UsuarioLogin(BaseModel):
    email: EmailStr = Field(max_length=60)
    password: str = Field(min_length=1, max_length=72)


class UsuarioRespuesta(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str


class Ejercicio(BaseModel):
    nombre_ejercicio: str = Field(min_length=1, max_length=80)
    grupo_muscular: str = Field(min_length=1, max_length=50)
    series: int = Field(gt=0, le=50)
    repeticiones: int = Field(gt=0, le=200)
    descanso_segundos: int = Field(ge=0, le=3600)
    notas: Optional[str] = Field(default=None, max_length=300)


class RutinaCrear(BaseModel):
    alumno_id: str
    nombre_rutina: str = Field(min_length=2, max_length=80)
    ejercicios: List[Ejercicio]


class RutinaRespuesta(BaseModel):
    id: str
    entrenador_id: str
    alumno_id: str
    nombre_rutina: str
    ejercicios: List[Ejercicio]
    activa: bool = True


class RutinaActualizar(BaseModel):
    nombre_rutina: Optional[str] = None
    ejercicios: Optional[List[Ejercicio]] = None


class ProgresoRegistrar(BaseModel):
    rutina_id: str
    comentario: Optional[str] = Field(default=None, max_length=300)


class ProgresoRespuesta(BaseModel):
    id: str
    alumno_id: str
    rutina_id: str
    nombre_rutina: str
    fecha_completado: datetime
    comentario: Optional[str] = None


class VincularAlumno(BaseModel):
    email: EmailStr = Field(max_length=60)


class ProgresoEntrenador(BaseModel):
    id: str
    alumno_id: str
    nombre_alumno: str
    rutina_id: str
    nombre_rutina: str
    fecha_completado: datetime
    comentario: Optional[str] = None

class DatosFisicos(BaseModel):
    peso_kg: float = Field(gt=0, le=400)
    altura_cm: float = Field(gt=0, le=250)
    edad: int = Field(gt=0, le=120)
    sexo: Literal["masculino", "femenino", "otro"]
    objetivo: Literal["bajar_peso", "subir_masa", "mantener"]


class RegistroPeso(BaseModel):
    id: str
    peso_kg: float
    fecha: datetime


class PerfilFisicoRespuesta(BaseModel):
    peso_kg: Optional[float] = None
    altura_cm: Optional[float] = None
    edad: Optional[int] = None
    sexo: Optional[str] = None
    objetivo: Optional[str] = None    