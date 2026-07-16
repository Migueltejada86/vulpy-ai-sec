from .llm_client import llm_call

def generate_test(finding, file_content):
    """AGENTE 4: Genera un pytest para validar el parche"""
    
    prompt = f"""
    Eres un QA senior en Python. Genera un test unitario con pytest para validar que este parche arregla la vulnerabilidad.
    
    Archivo: {finding['file']}
    Vulnerabilidad: Command Injection con shell=True
    Codigo actual: {file_content}
    Parche aplicado: {finding['patch']}
    
    Requisitos:
    1. Usa pytest
    2. El test debe fallar con el codigo vulnerable y pasar con el parche
    3. Solo devuelve el codigo del test
    """
    
    test_code = llm_call(prompt)
    return test_code