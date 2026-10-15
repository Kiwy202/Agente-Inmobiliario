from langchain_core.tools import tool
from sqlalchemy import text
from src.infrastructure.postgres_db import PostgresDBClient
from typing import Optional

# Usamos Optional[int] para que la IA entienda perfectamente que puede dejar este campo vacío
@tool
def analizar_mercado_inmobiliario(distrito: str, habitaciones: Optional[int] = None) -> str:
    """
    Útil para consultar estadísticas completas de inmuebles en un distrito.
    Devuelve el precio promedio, el precio por m2, y los rangos de precio (económico y premium).
    """
    print(f"\n⚙️ [Tool Executing] Analizando {distrito} | Habs: {habitaciones}")
    
    pg_client = PostgresDBClient()
    session = pg_client.get_session()
    
    try:
        query = """
            SELECT 
                COUNT(*) as total_anuncios,
                ROUND(AVG(precio_venta)::numeric, 2) as promedio_usd,
                ROUND(MIN(precio_venta)::numeric, 2) as economico_usd,
                ROUND(MAX(precio_venta)::numeric, 2) as premium_usd,
                ROUND(AVG(precio_venta / NULLIF(area_total_m2, 0))::numeric, 2) as promedio_m2_usd
            FROM inmuebles_lima 
            WHERE distrito ILIKE :dist
              -- FILTROS DE CALIDAD DE DATOS (Data Quality)
              AND precio_venta BETWEEN 30000 AND 5000000 -- Depas entre 30k y 5M USD
              AND area_total_m2 > 15                     -- Ignorar cocheras o errores de 0 m2
        """
        
        params = {"dist": f"%{distrito}%"}
        if habitaciones is not None:
            query += " AND habitaciones = :habs"
            params["habs"] = habitaciones
            
        # EL BUGFIX: .mappings() obliga a SQL a devolver un diccionario limpio, no una tupla cruda
        resultado = session.execute(text(query), params).mappings().fetchone()
        
        # Validamos si la consulta vino vacía
        if not resultado or resultado['total_anuncios'] == 0:
            return f"No encontré datos en la base de datos para {distrito} con esas características."
            
        # Construimos el texto inyectando las llaves del diccionario
        respuesta_ia = (
            f"Datos de {distrito} basados en {resultado['total_anuncios']} anuncios:\n"
            f"- Precio Promedio: ${resultado['promedio_usd']} USD\n"
            f"- Segmento Económico (Desde): ${resultado['economico_usd']} USD\n"
            f"- Segmento Premium (Hasta): ${resultado['premium_usd']} USD\n"
            f"- Precio Promedio por m2: ${resultado['promedio_m2_usd']} USD/m2\n"
        )
        
        print(f"✅ [Tool Success] Calculo SQL exitoso. Devolviendo texto al LLM...")
        return respuesta_ia

    except Exception as e:
        error_msg = f"Error SQL interno: {str(e)}"
        print(f"❌ [Tool Error] {error_msg}")
        return error_msg
    finally:
        session.close()

# --- ZONA DE PRUEBAS BACKEND (Aislador de errores) ---
if __name__ == "__main__":
    print("Iniciando prueba directa a la Base de Datos (Sin IA)...\n")
    
    print("--- Prueba 1: Todo el distrito ---")
    resultado_1 = analizar_mercado_inmobiliario.invoke({"distrito": "San Isidro"})
    print(resultado_1)
    
    print("\n--- Prueba 2: Filtrando por 3 habitaciones ---")
    resultado_2 = analizar_mercado_inmobiliario.invoke({"distrito": "San Isidro", "habitaciones": 3})
    print(resultado_2)