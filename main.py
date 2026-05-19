"""
ARCANO MESSENGER PRO - v2.0
Sistema de Automação WhatsApp com IA e Testes

COMO USAR:
    python main.py
"""

import tkinter as tk
import sys
import os
import importlib.util

# ── Caminho absoluto da pasta 'codigo' ───────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
CODIGO = os.path.join(BASE, "codigo")

# Adiciona 'codigo' e 'codigo/bot' ao path para imports internos
for p in [CODIGO, os.path.join(CODIGO, "bot")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Carrega codigo/interface.py diretamente pelo caminho ─────
# (evita problemas com acentos e caminhos do Windows/OneDrive)
def carregar_modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod

try:
    interface_path = os.path.join(CODIGO, "interface.py")
    interface = carregar_modulo("interface", interface_path)
    ArcanoApp = interface.ArcanoApp
except Exception as e:
    print("=" * 60)
    print("ERRO ao carregar interface.py")
    print(f"Caminho tentado: {interface_path}")
    print(f"Detalhe: {e}")
    print("=" * 60)
    sys.exit(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArcanoApp(root)
    root.mainloop()