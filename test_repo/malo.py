import subprocess
import os

# Vulnerabilidad 1: Command Injection
def ejecutar(cmd):
    subprocess.run(cmd, shell=True)

# Vulnerabilidad 2: Uso inseguro
os.system("rm -rf /")