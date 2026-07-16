####Agente Parcheador
#Genera el fix y el test
from agents.llm_client import llm_call
import json

def propose_patch(hallazgo, codigo, contexto_repo):
    prompt = f"""
    Eres un senior Python dev. Arregla esta vulnerabilidad de forma segura.
    
    Vulnerabilidad: {hallazgo['tipo']}
    Código vulnerable:
    {codigo}
    Contexto: {contexto_repo} # ej: usa FastAPI, SQLAlchemy, bandit
    
    Devuelve:
    1. Código corregido completo
    2. Por qué este fix soluciona el problema
    3. Test pytest para verificar que el exploit ya no funciona
    Usa solo librerías del stdlib o las que ya estén en el proyecto.
    """
    response = llm_call(prompt)
    response = response.replace("```json", "").replace("```","").strip()
    return json.loads(response)
