from .llm_client import llm_call

def redteam_analysis(sast_results, sca_results):
    """AGENTE 5: Red Team - OWASP, CWE, ASVS, Exploitability"""
    
    prompt = f"""
    Eres un Red Team Engineer certificado en OWASP ASVS.
    
    Entrada SAST: {sast_results}
    Entrada SCA: {sca_results}
    
    Devuelve JSON con:
    {{
      "top_risks": [
        {{"vuln": "", "owasp": "A03:2021", "cwe": "CWE-78", "severity": "High", "exploitable": true, "attack_vector": ""}}
      ],
      "compliance": {{"owasp_coverage": "", "asvs_level": "L2"}},
      "ci_gate": "FAIL", // FAIL si Critical/High, PASS si no
      "justification": "Por qué rompemos el build"
    }}
    
    Reglas: 
    - chromadb@1.1.1 = CVE-2026-45829 = SQLi = A03:2021 = Critical
    - click@8.1.8 = CVE-2026-7246 = Command Injection = A03:2021 = High
    """
    response = llm_call(prompt)
    return json.loads(response.replace("```json", "").replace("```","").strip())