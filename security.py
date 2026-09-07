import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60 * 24  # 24 horas

def encriptar_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hash: str) -> bool:
    return pwd_context.verify(password_plano, password_hash)

def crear_token(datos: dict) -> str:
    a_codificar = datos.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=EXPIRACION_MINUTOS)
    a_codificar.update({"exp": expiracion})
    return jwt.encode(a_codificar, SECRET_KEY, algorithm=ALGORITHM)


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

bearer_scheme = HTTPBearer()

def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    token = credenciales.credentials
    credenciales_excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        rol: str = payload.get("rol")
        if user_id is None or rol is None:
            raise credenciales_excepcion
        return {"id": user_id, "rol": rol}
    except JWTError:
        raise credenciales_excepcion


def requerir_rol(rol_requerido: str):
    def verificador(usuario: dict = Depends(obtener_usuario_actual)) -> dict:
        if usuario["rol"] != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso restringido a usuarios con rol '{rol_requerido}'",
            )
        return usuario
    return verificador