import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

class MongoDBClient:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGO_DB", "inmobiliaria_raw")
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # El comando ping fuerza una llamada al servidor para validar que esté vivo
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"✅ Conexión exitosa a MongoDB (Base de datos: {self.db_name})")
        except ConnectionFailure as e:
            print(f"❌ Error al conectar a MongoDB. ¿Está corriendo el servicio?: {e}")
            raise e

    def get_collection(self, collection_name):
        if self.db is None:
            self.connect()
        return self.db[collection_name]