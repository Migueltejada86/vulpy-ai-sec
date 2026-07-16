# AGENTE 1 DETECTOR 
import subprocess
import json
import os
import tempfile
from agents.llm_client import llm_call
from agents.tester import generate_test

def run_semgrep_on_code(code, filename="temp.py"):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    result = subprocess.run(
        ["semgrep", "--json", "--config=p/python", "--config=p/security-audit", tmp_path],
        capture_output=True, text=True
    )
    os.remove(tmp_path)

    if result.returncode not in [0, 1]:
        return []
    return json.loads(result.stdout)["results"]

def llm_filter(findings, diff):
    prompt = f"""
    Eres un revisor de seguridad para Python. 
    Filtra estos hallazgos de Semgrep y quédate solo con severidad media-alta.
    Elimina falsos positivos obvios.
    Devuelve JSON: [{{"archivo": "", "linea": 0, "tipo": "", "severidad": 0, "evidencia":""}}]
    
    Hallazgos: {findings}
    Diff: {diff}
    """
    response = llm_call(prompt)
    response = response.replace("```json", "").replace("```","").strip()
    try:
        return json.loads(response)
    except:
        return findings

def run_detection(repo_path, pr_number):
    print(f"[*] Revisando PR #{pr_number} en {repo_path}")
    
    result = subprocess.run(
        ["semgrep", "--json", "--config=p/python", repo_path],
        capture_output=True, text=True
    )
    
    if result.returncode not in [0, 1]:
        print("[-] Error en semgrep")
        return []
    
    findings_raw = json.loads(result.stdout)["results"]
    findings_final = []
    
    if findings_raw:
        print(f"[!] {len(findings_raw)} hallazgos. Filtrando con LLM...")
        filtered = llm_filter(findings_raw, "")
        
        for f in filtered:
            # Compatibilidad con ambos formatos
            file = f.get("path") or f.get("archivo")
            line = f.get("start", {}).get("line") or f.get("linea")
            code = f.get("extra", {}).get("lines")
            
            try:
                with open(file, 'r', encoding='utf-8') as fp:
                    file_content = fp.read()
            except:
                file_content = code
            
            explanation = llm_call(f"Explica esta vulnerabilidad de seguridad en español, breve y con riesgo: {f}")
            
            patch_prompt = f"""Eres un senior dev. Dame un parche en formato diff para arreglar esto:
            Archivo: {file}
            Linea: {line}
            Codigo: {file_content}
            Vulnerabilidad: {f.get('extra', {}).get('message') or f.get('tipo')}
            Devuelve solo el diff."""
            patch = llm_call(patch_prompt)
            
            test_sugerido = generate_test({"file": file, "patch": patch}, file_content)

            patch_limpio = patch.replace("```diff", "").replace("```", "").strip()
            test_limpio = test_sugerido.replace("```python", "").replace("```", "").strip()

           

            print(f"\n--- HALLAZGO ---")
            print(f"Archivo: {file}:{line}")
            print(f"Explicacion: {explanation}")
            print(f"\n**Parche Sugerido:**\n```diff\n{patch_limpio}\n```")
            print(f"\n**Test Sugerido:**\n```python\n{test_limpio}\n```")
            findings_final.append({"file": file, "line": line, "explanation": explanation, "patch": patch})
    else:
        print("[+] Sin vulnerabilidades detectadas")
    
    return findings_final