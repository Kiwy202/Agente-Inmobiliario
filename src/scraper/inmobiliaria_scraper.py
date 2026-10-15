from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from src.infrastructure.mongo_db import MongoDBClient
import time
import re

def extraer_propiedades_urbania(distrito: str):
    print(f"--- Iniciando extracción con Debugging en {distrito} ---")
    
    mongo = MongoDBClient()
    coleccion = mongo.get_collection("propiedades_raw")
    
    distrito_formateado = distrito.lower().replace(" ", "-")
    url = f"https://urbania.pe/buscar/departamentos-en-venta-en-{distrito_formateado}"
    
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        contexto = navegador.new_context(viewport={"width": 1920, "height": 1080})
        pagina = contexto.new_page()
        
        try:
            print("1. Abriendo navegador Chrome...")
            pagina.goto(url, timeout=60000, wait_until="domcontentloaded")
            pagina.wait_for_timeout(7000)
            
            soup = BeautifulSoup(pagina.content(), 'html.parser')
            textos_precios = soup.find_all(string=re.compile(r'S/|USD'))
            print(f"Se detectaron {len(textos_precios)} posibles precios.")
            
            datos_guardados = 0
            tarjetas_procesadas = set() 
            
            for texto in textos_precios:
                precio_limpio = texto.strip()
                if len(precio_limpio) < 3 or len(precio_limpio) > 20: continue
                    
                tarjeta_madre = texto.find_parent('div')
                if not tarjeta_madre: continue
                
                # --- EL BUGFIX: ESCALADA INTELIGENTE ---
                # Ahora subimos hasta encontrar la caja que contenga la palabra 'dorm' o 'm2'
                limite_escalones = 0
                while tarjeta_madre and limite_escalones < 8:
                    texto_temporal = tarjeta_madre.get_text(separator=" ").lower()
                    if 'dorm' in texto_temporal or 'm2' in texto_temporal or 'm²' in texto_temporal:
                        break # Encontramos al "Abuelo", paramos de subir.
                    tarjeta_madre = tarjeta_madre.find_parent('div')
                    limite_escalones += 1
                
                if tarjeta_madre and tarjeta_madre not in tarjetas_procesadas:
                    tarjetas_procesadas.add(tarjeta_madre)
                    
                    try:
                        titulo_tag = tarjeta_madre.find(['h2', 'h3'])
                        titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
                        
                        texto_completo = tarjeta_madre.get_text(separator=" ").lower()
                        
                        # LOG DE DEBUGGING: Esto te mostrará en la consola negra exactamente qué texto atrapó
                        print(f"\n🔍 [DEBUG] Tarjeta capturada: {texto_completo[:100]}...") 
                        
                        # EXTRACCIÓN MEJORADA: group(1) saca solo el número puro
                        match_dorm = re.search(r'(\d+)\s*(?:dorm|hab)', texto_completo)
                        habitaciones_crudo = match_dorm.group(1) if match_dorm else "0"
                        
                        match_m2 = re.search(r'(\d+)\s*(?:m²|m2)', texto_completo)
                        area_crudo = match_m2.group(1) if match_m2 else "0"
                        
                        documento = {
                            "origen": "urbania",
                            "distrito": distrito,
                            "titulo": titulo,
                            "precio_crudo": precio_limpio,
                            "habitaciones_crudo": habitaciones_crudo,
                            "area_crudo": area_crudo,
                            "fecha_extraccion": time.time()
                        }
                        
                        coleccion.insert_one(documento)
                        datos_guardados += 1
                        
                    except Exception as e:
                        continue
                        
            print(f"\n✅ ¡Éxito! {datos_guardados} propiedades guardadas en MongoDB.")
            
        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
        finally:
            navegador.close()

if __name__ == "__main__":
    extraer_propiedades_urbania("San Isidro")