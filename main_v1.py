


import os
import sys
import subprocess
from github import Github
from agents.detector import run_detection
from agents.explainer import explain_finding
from agents.patcher import propose_patch
from agents.llm_client import llm_call

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = int(sys.argv[1])

def get_diff_and_files(repo, pr):
    """Baja el diff y el código de los archivos cambiados"""
    files_data = {}
    for file in pr.get_files():
        if file.filename.endswith(".py"): # solo python por ahora
            patch = file.patch
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
            files_data[file.filename] = {"patch": patch, "content": content}
    return files_data

def post_comment(pr, body):
    """Comenta en el PR"""
    pr.create_issue_comment(body)

def main():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)

    print(f"Revisando PR #{PR_NUMBER}: {pr.title}")
    files = get_diff_and_files(repo, pr)

    all_findings = []
    for filename, data in files.items():
        print(f"Analizando {filename}")

        # AGENTE 1: Detectar
        findings = run_detection(data["patch"], data["content"])

        for finding in findings:
            # AGENTE 2: Explicar
            explanation = explain_finding(finding, data["content"])

            # AGENTE 3: Parchear
            patch = propose_patch(finding, data["content"])

            comment = f"""
            ### 🤖 Security Agent Report

            **Issue**: `{finding['tipo']}` en `{filename}:{finding['linea']}`
            **Severidad**: {finding['severidad']}/5

            **¿Por qué importa?**
            {explanation}

            **Parche Sugerido:**
            ```diff
            {patch['diff']}
            **Test Sugerido:**
            {patch['test']}
            """
            post_comment(pr, comment)
            all_findings.append(finding)

    if not all_findings:
        post_comment(pr, "### ✅ Security Agent: No se encontraron vulnerabilidades críticas")
    else:
        post_comment(pr, f"### ⚠️ Se encontraron {len(all_findings)} hallazgos. Revisar arriba.")

if __name__ == "__main__":
    main()
