import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales de PostgreSQL (valores por defecto seguros)
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
PG_DB = os.getenv("POSTGRES_DB", "mercado_inmobiliario")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construir URI de conexión
# Formato: postgresql://usuario:contraseña@localhost:5432/nombre_bd
POSTGRES_URI = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

# Inicializar Base para definir modelos de datos (Tablas)
Base = declarative_base()

class Inmueble(Base):
    """
    Representa la estructura relacional (tabla) en PostgreSQL donde
    almacenaremos los datos limpios y estructurados que el agente consultará.
    """
    __tablename__ = 'inmuebles_lima'

    id = Column(Integer, primary_key=True, autoincrement=True)
    origen_datos = Column(String(50))           # Ej. 'urbania', 'adondevivir'
    tipo_propiedad = Column(String(50))         # Ej. 'departamento', 'casa'
    distrito = Column(String(100), index=True)  # Indexado para búsquedas rápidas
    precio_venta = Column(Float)
    moneda = Column(String(10))                 # Ej. 'USD', 'PEN'
    area_total_m2 = Column(Float)
    habitaciones = Column(Integer, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class PostgresDBClient:
    def __init__(self):
        try:
            # Crear el motor de conexión
            self.engine = create_engine(POSTGRES_URI)
            
            # Crear las tablas en la base de datos si no existen
            Base.metadata.create_all(self.engine)
            
            # Configurar el generador de sesiones
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print(f"✅ Conexión exitosa a PostgreSQL (Base de datos: {PG_DB})")
            print("✅ Tablas sincronizadas correctamente.")
        except Exception as e:
            print(f"❌ Error al conectar a PostgreSQL. Verifica tus credenciales en el archivo .env: {e}")
            raise e

    def get_session(self):
        """
        Devuelve una nueva sesión para interactuar con la base de datos.
        Importante: Siempre cerrar la sesión después de usarla (session.close())
        """
        return self.SessionLocal()
