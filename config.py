"""
config.py — Configurações globais do sistema
Altere aqui para personalizar comportamento do bot.
"""

# ──────────────────────────────────────────────
# DELAYS (em segundos)
# ──────────────────────────────────────────────
DELAY_MIN = 20          # Pausa mínima entre mensagens
DELAY_MAX = 60          # Pausa máxima entre mensagens
DELAY_TYPING = 1.5      # Simula tempo de digitação
DELAY_AFTER_SEND = 2    # Aguarda após enviar

# ──────────────────────────────────────────────
# ANTI-SPAM
# ──────────────────────────────────────────────
ANTISPAM_BLOCO = 10     # Pausa extra a cada N mensagens
ANTISPAM_PAUSA = 120    # Pausa extra em segundos

# ──────────────────────────────────────────────
# WHATSAPP WEB
# ──────────────────────────────────────────────
WHATSAPP_URL = "https://web.whatsapp.com"
WHATSAPP_TIMEOUT = 20   # Segundos aguardando elementos

# ──────────────────────────────────────────────
# IA (Anthropic)
# ──────────────────────────────────────────────
# Coloque sua API KEY aqui ou deixe vazio para usar
# variações locais simples
ANTHROPIC_API_KEY = ""
IA_MODEL = "claude-sonnet-4-20250514"
IA_MAX_TOKENS = 200

# ──────────────────────────────────────────────
# INTERFACE
# ──────────────────────────────────────────────
APP_TITLE = "⚡ ARCANO MESSENGER PRO ⚡"
APP_WIDTH = 1050
APP_HEIGHT = 870
APP_RESIZABLE = True