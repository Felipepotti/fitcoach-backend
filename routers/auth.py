from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from database import usuarios_collection
from models import UsuarioRegistro, UsuarioLogin, UsuarioRespuesta
from security import encriptar_password, verificar_password, crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario: UsuarioRegistro):
    existente = await usuarios_collection.find_one({"email": usuario.email})
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = {
        "nombre": usuario.nombre,
        "email": usuario.email,
        "password": encriptar_password(usuario.password),
        "rol": usuario.rol,
    }

    resultado = await usuarios_collection.insert_one(nuevo_usuario)

    return UsuarioRespuesta(
        id=str(resultado.inserted_id),
        nombre=usuario.nombre,
        email=usuario.email,
        rol=usuario.rol,
    )

@router.post("/login")
async def login(credenciales: UsuarioLogin):
    usuario = await usuarios_collection.find_one({"email": credenciales.email})

    if not usuario or not verificar_password(credenciales.password, usuario["password"]):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token({"sub": str(usuario["_id"]), "rol": usuario["rol"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario["rol"],
        "nombre": usuario["nombre"],
    }