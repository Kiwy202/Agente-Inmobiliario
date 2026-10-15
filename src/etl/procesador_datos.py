import re
from src.infrastructure.mongo_db import MongoDBClient
from src.infrastructure.postgres_db import PostgresDBClient, Inmueble

def ejecutar_etl():
    print("--- Iniciando Proceso ETL Enriquecido (Mongo -> Postgres) ---")
    
    mongo = MongoDBClient()
    coleccion_mongo = mongo.get_collection("propiedades_raw")
    documentos_crudos = list(coleccion_mongo.find({"origen": "urbania"}))
    
    print(f"📦 Se leyeron {len(documentos_crudos)} documentos crudos.")
    
    pg_client = PostgresDBClient()
    session = pg_client.get_session()
    
    # IMPORTANTE: Vaciamos la tabla antigua para no crear duplicados
    session.query(Inmueble).delete()
    print("🧹 Tabla PostgreSQL formateada para carga fresca.")
    
    datos_insertados = 0
    
    for doc in documentos_crudos:
        try:
            precio_texto = doc.get("precio_crudo", "")
            distrito = doc.get("distrito", "Desconocido")
            
            # Limpieza del precio
            moneda = "USD" if "USD" in precio_texto.upper() else "PEN"
            solo_numeros_precio = re.sub(r'[^\d]', '', precio_texto)
            if not solo_numeros_precio: continue
                
            precio_matematico = float(solo_numeros_precio)
            if moneda == "PEN":
                precio_matematico = round(precio_matematico / 3.75, 2)
            
            # Limpieza de Habitaciones
            habs_texto = doc.get("habitaciones_crudo", "0")
            match_habs = re.search(r'\d+', str(habs_texto))
            habitaciones_limpias = int(match_habs.group()) if match_habs else 0
            
            # Limpieza de Área (M2)
            area_texto = doc.get("area_crudo", "0")
            match_area = re.search(r'\d+', str(area_texto))
            area_limpia = float(match_area.group()) if match_area else 0.0
            
            nuevo_inmueble = Inmueble(
                origen_datos=doc.get("origen"),
                tipo_propiedad="departamento",
                distrito=distrito,
                precio_venta=precio_matematico,
                moneda="USD",
                area_total_m2=area_limpia,
                habitaciones=habitaciones_limpias
            )
            
            session.add(nuevo_inmueble)
            datos_insertados += 1
            
        except Exception as e:
            print(f"Error transformando documento {doc.get('_id')}: {e}")
            
    session.commit()
    session.close()
    
    print(f"✅ ETL completado. {datos_insertados} inmuebles enriquecidos listos para la IA.")

if __name__ == "__main__":
    ejecutar_etl()