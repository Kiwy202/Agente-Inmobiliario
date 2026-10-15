from src.infrastructure.mongo_db import MongoDBClient
from src.infrastructure.postgres_db import PostgresDBClient, Inmueble

def probar_arquitectura():
    print("--- INICIANDO CAPA MONGODB (Datos Crudos) ---")
    mongo = MongoDBClient()
    coleccion = mongo.get_collection("propiedades_raw")
    print(f"Documentos actuales en Mongo: {coleccion.count_documents({})}")
    
    print("\n--- INICIANDO CAPA POSTGRESQL (Datos Estructurados) ---")
    # Al inicializar PostgresDBClient, SQLAlchemy creará la tabla 'inmuebles_lima' automáticamente
    pg_client = PostgresDBClient()
    
    # Probamos insertar un dato limpio (simulando el proceso ETL)
    session = pg_client.get_session()
    nuevo_inmueble = Inmueble(
        origen_datos="urbania",
        tipo_propiedad="departamento",
        distrito="San Isidro",
        precio_venta=250000,
        moneda="USD",
        area_total_m2=120,
        habitaciones=3
    )
    
    session.add(nuevo_inmueble)
    session.commit()
    print(f"✅ Inmueble en {nuevo_inmueble.distrito} guardado en PostgreSQL (ID: {nuevo_inmueble.id})")
    session.close()

if __name__ == "__main__":
    probar_arquitectura()