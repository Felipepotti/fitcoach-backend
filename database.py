import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]

usuarios_collection = database.get_collection("Usuarios")
rutinas_collection = database.get_collection("Rutinas")
progreso_collection = database.get_collection("progreso")