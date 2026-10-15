import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from src.agent.tools import analizar_mercado_inmobiliario

# 1. CARGA DE ENTORNO
load_dotenv()

def iniciar_agente_inmobiliario():
    # 2. EL CEREBRO
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)
    
    # 3. LAS MANOS
    herramientas = [analizar_mercado_inmobiliario]
    
    # 4. EL MOTOR
    agente = create_agent(llm, herramientas)
    
    return agente

if __name__ == "__main__":
    agente = iniciar_agente_inmobiliario()
    print("🤖 Agente Inmobiliario iniciado. (Escribe 'salir' para terminar)")
    
    # 5. REGLAS BASE
    instrucciones = SystemMessage(content=(
        "Eres un analista inmobiliario experto en Lima, Perú. "
        "REGLA 1: Usa siempre tus herramientas para consultar la base de datos antes de dar un precio. "
        "REGLA 2: Si no encuentras el distrito en la base de datos, di 'No tengo información sobre ese distrito', nunca inventes números."
    ))
    
    # 6. HISTORIAL DE MEMORIA
    historial_chat = [instrucciones]
    
    # 7. BUCLE CONTINUO
    while True:
        pregunta = input("\nTú: ")
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("Cerrando sistema...")
            break
            
        if not pregunta.strip():
            continue
            
        historial_chat.append(("user", pregunta))
            
        try:
            respuesta = agente.invoke({"messages": historial_chat})
            
            # --- EL BUGFIX ESTÁ AQUÍ ---
            # Atrapamos la "caja" que nos manda la IA
            contenido_bruto = respuesta['messages'][-1].content
            
            # Si la caja es una lista (como te salió en la consola), abrimos el primer elemento [0] y sacamos la clave 'text'
            if isinstance(contenido_bruto, list):
                respuesta_texto = contenido_bruto[0].get('text', str(contenido_bruto))
            # Si no es una lista, significa que la IA ya nos dio el texto limpio
            else:
                respuesta_texto = contenido_bruto
            # ---------------------------
            
            # Imprimimos el texto limpio sin corchetes ni basura JSON
            print(f"\nAgente: {respuesta_texto}")
            
            historial_chat.append(("assistant", respuesta_texto))
            
        except Exception as e:
            print(f"\n[Error de sistema]: Revisa tu conexión o tu API Key. Detalle: {e}")
            historial_chat.pop()