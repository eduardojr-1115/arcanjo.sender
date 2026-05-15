"""
╔══════════════════════════════════════════════════════╗
║          ARCANO MESSENGER PRO - v2.0                 ║
║  Sistema de Automação WhatsApp com IA e Testes       ║
╚══════════════════════════════════════════════════════╝

COMO USAR:
    python main.py

DEPENDÊNCIAS:
    pip install selenium pandas openpyxl pyperclip anthropic pillow
"""

import tkinter as tk
from interface.app import ArcanoApp


if __name__ == "__main__":
    root = tk.Tk()
    app = ArcanoApp(root)
    root.mainloop()