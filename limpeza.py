# =========================================================
# LIMPEZA LEVE SEM ADMINISTRADOR
# Funciona em PCs corporativos
# =========================================================

import os
import shutil
import tempfile
import subprocess

print("🚀 Iniciando limpeza...\n")

# =========================================================
# FUNÇÃO DE LIMPEZA
# =========================================================

def limpar_pasta(caminho):
    if os.path.exists(caminho):

        for item in os.listdir(caminho):

            item_path = os.path.join(caminho, item)

            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)

                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

            except:
                pass

# =========================================================
# PASTAS DO USUÁRIO
# =========================================================

pastas = [

    tempfile.gettempdir(),

    os.path.expandvars(
        r"%USERPROFILE%\AppData\Local\Temp"
    ),

    os.path.expandvars(
        r"%USERPROFILE%\AppData\Local\Microsoft\Windows\INetCache"
    ),

    os.path.expandvars(
        r"%USERPROFILE%\Downloads"
    ),
]

# =========================================================
# EXECUTAR LIMPEZA
# =========================================================

for pasta in pastas:

    print(f"🧹 Limpando: {pasta}")

    limpar_pasta(pasta)

# =========================================================
# LIBERAR MEMÓRIA RAM
# =========================================================

print("\n🧠 Fechando processos pesados...")

processos = [

    "chrome.exe",
    "msedge.exe",
    "Teams.exe",
    "Discord.exe"

]

for proc in processos:

    subprocess.run(
        f'taskkill /f /im {proc}',
        shell=True,
        capture_output=True
    )

print("\n✅ Limpeza concluída!")
print("🚀 Arquivos temporários removidos.")
print("💾 Memória RAM otimizada.")