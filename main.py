import os
import sys
import json
import subprocess
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from agents.llm_client import llm
from agents.detector import run_detection, load_sbom
from agents.explainer import explain_finding
from agents.patcher import propose_patch
from agents.tester import generate_test
from agents.redteam import redteam_analysis

SBOM_FILE = "vulpy-sbom.json"

###
def load_sbom():
    """Lee el SBOM y extrae dependencias con versión"""
    if not os.path.exists(SBOM_FILE):
        return []
    with open(SBOM_FILE) as f:
        sbom = json.load(f)
    return [f"{c['name']}@{c.get('version')}" for c in sbom.get("components", [])]

# 1. ENVOLVEMOS AGENTES EN CREWAI
llm_instance = llm

sast_agent = Agent(
    role='SAST + SCA Detector',
    goal='Detectar vulnerabilidades en código y dependencias',
    backstory='Usas Semgrep y análisis de SBOM. Mapeas a OWASP Top 10.',
    llm=llm_instance,
    tools=[run_detection, load_sbom],
    verbose=True
)


redteam_agent = Agent(
    role='Red Team Lead',
    goal='Priorizar riesgos, mapear OWASP/CWE/ASVS y decidir gate',
    backstory='Piensas como atacante. Rompes builds inseguros.',
    llm=llm,
    tools=[redteam_analysis],
    verbose=True
)


explainer_agent = Agent(
    role='Security Explainer',
    goal='Explicar vulnerabilidades a devs junior en español',
    backstory='Traduces CWE a "qué significa para mi app"',
    llm=llm_instance,
    tools=[explain_finding],
    verbose=True
)

patcher_agent = Agent(
    role='Auto Patcher',
    goal='Generar parches seguros y tests',
    backstory='Senior Python Dev que arregla vulnerabilidades',
    llm=llm_instance,
    tools=[propose_patch, generate_test],
    verbose=True
)

redteam_agent = Agent(
    role='Red Team Lead',
    goal='Priorizar riesgos y decidir si el CI/CD debe fallar',
    backstory='Piensas como atacante. Sigues ASVS y OWASP',
    llm=llm_instance,
    verbose=True
)

# 2. TASKS DEL PIPELINE
deteccion_task = Task(
    description="""1. Corre SAST con semgrep en ./test_repo 
    2. Lee vulpy-sbom.json y busca CVEs. 
    Foco en chromadb@1.1.1 y click@8.1.8""",
    agent=sast_agent,
    expected_output="Lista de hallazgos SAST + SCA con archivo, linea y severidad"
)

explicacion_task = Task(
    description="Para cada hallazgo, explica: 1.Problema 2.Explotación 3.Impacto 4.Regla de oro",
    agent=explainer_agent,
    context=[deteccion_task],
    expected_output="Explicaciones en español para cada vuln"
)

patch_task = Task(
    description="Genera el código corregido + patch diff + test pytest para cada hallazgo",
    agent=patcher_agent,
    context=[explicacion_task],
    expected_output="Código corregido y tests"
)

gate_task = Task(
    description="""Consolida todo. Si hay Critical o High en SCA/SAST devuelve FAIL.
    Si no, PASS. Sigue OWASP ASVS""",
    agent=redteam_agent,
    context=[deteccion_task, explicacion_task, patch_task],
    expected_output="Reporte final + DECISION: PASS o FAIL"
)

# 3. CREW
crew = Crew(
    agents=[sast_agent, explainer_agent, patcher_agent, redteam_agent],
    tasks=[deteccion_task, explicacion_task, patch_task, gate_task],
    process=Process.sequential,
    verbose=2
)
if __name__ == "__main__":
    print("Starting Vulpy AI Security Pipeline...")
    report = "# Vulpy AI Security Report\n"
    gate_status = "PASS"
    
    try:
        if not os.path.exists(SBOM_FILE):
            subprocess.run(["cyclonedx-py", "venv", "-o", SBOM_FILE])

        result = crew.kickoff()
        result_str = str(result)
        report += f"## Results\n{result_str}\n"
        
        if "FAIL" in result_str or "Critical" in result_str or "High" in result_str:
            gate_status = "FAIL"

    except Exception as e:
        report += f"## ERROR\nEl pipeline fallo: {str(e)}\n"
        gate_status = "FAIL"
        print(f"::error::Pipeline error: {e}")

    finally:
        # ESTO SIEMPRE SE EJECUTA
        report += f"\n**Gate**: {gate_status}\n**Timestamp**: {datetime.now()}"
        with open("vulpy-report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("Report generated: vulpy-report.md")

    if gate_status == "FAIL":
        sys.exit(1)
    sys.exit(0)