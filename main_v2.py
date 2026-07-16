import os
import sys
from agents.detector import run_detection

PR_NUMBER = int(sys.argv[1])
REPO_PATH = "./test_repo" # <- escanea esta carpeta

def main():
    print(f"Revisando carpeta: {REPO_PATH}")
    
    findings = run_detection(REPO_PATH, PR_NUMBER)
    
    if not findings:
        print("### ✅ No se encontraron vulnerabilidades")
    else:
        print(f"### ⚠️ Se encontraron {len(findings)} hallazgos")

if __name__ == "__main__":
    main()