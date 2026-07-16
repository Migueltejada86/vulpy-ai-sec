#Traduce el CWE a "qué significa para mi app"
from agents.llm_client import llm_call



def explain_finding(hallazgo, codigo):
    prompt = f"""
    Explica este hallazgo de seguridad en Python a un dev junior.
    
    Hallazgo: {hallazgo['tipo']} en {hallazgo['archivo']}:{hallazgo['linea']}
    Código: ```python
    {codigo}
    Responde en español, 4 bullets:
    1. El problema: 
    2. Cómo se explota: 
    3. Impacto si no se arregla:
    4. Regla de oro para evitarlo:
    """
    return llm_call(prompt)
