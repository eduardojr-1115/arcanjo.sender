"""
core/antispam.py — Gerencia delays e proteção anti-ban

Estratégias:
  - Delay aleatório entre mensagens
  - Pausa longa a cada N mensagens (simula comportamento humano)
  - Simulação de "digitação" com atrasos variáveis
"""

import time
import random

from codigo.config import DELAY_MIN, DELAY_MAX, ANTISPAM_BLOCO, ANTISPAM_PAUSA


class AntiSpam:
    """
    Controla o ritmo de envio para parecer humano e evitar banimento.
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self.contador = 0          # Quantas mensagens foram enviadas nesta sessão
        self.ativo = True          # Liga/desliga o controle

    # ──────────────────────────────────────────────
    # DELAY ENTRE MENSAGENS
    # ──────────────────────────────────────────────
    def esperar(self, delay_max: int = None):
        """
        Aguarda um tempo aleatório entre DELAY_MIN e delay_max.
        Parâmetro delay_max permite sobrescrever o padrão da config.
        """
        if not self.ativo:
            return

        maximo = delay_max or DELAY_MAX
        tempo = random.randint(DELAY_MIN, maximo)

        self.log(f"⏳ Aguardando {tempo}s antes do próximo envio...")
        time.sleep(tempo)

    # ──────────────────────────────────────────────
    # REGISTRAR ENVIO (verifica pausa longa)
    # ──────────────────────────────────────────────
    def registrar_envio(self):
        """
        Deve ser chamado após cada envio bem-sucedido.
        A cada ANTISPAM_BLOCO envios, aplica uma pausa extra longa.
        """
        self.contador += 1

        if self.ativo and self.contador % ANTISPAM_BLOCO == 0:
            self.log(
                f"🛡️ Anti-spam: {self.contador} mensagens enviadas. "
                f"Pausa longa de {ANTISPAM_PAUSA}s..."
            )
            time.sleep(ANTISPAM_PAUSA)

    # ──────────────────────────────────────────────
    # SIMULAR DIGITAÇÃO
    # ──────────────────────────────────────────────
    def simular_digitacao(self, mensagem: str):
        """
        Aguarda um tempo proporcional ao tamanho da mensagem.
        Simula um humano digitando (~40 palavras por minuto).
        """
        if not self.ativo:
            return

        palavras = len(mensagem.split())
        # ~40 palavras/min = 1.5s por palavra, com variação
        tempo = (palavras / 40) * 60 * random.uniform(0.5, 1.5)
        # Limita entre 1s e 8s para não travar demais
        tempo = max(1.0, min(tempo, 8.0))

        self.log(f"⌨️ Simulando digitação ({tempo:.1f}s)...")
        time.sleep(tempo)

    # ──────────────────────────────────────────────
    # RESET
    # ──────────────────────────────────────────────
    def reset(self):
        """Zera o contador (use ao iniciar nova sessão)."""
        self.contador = 0
        self.log("🔄 Contador anti-spam resetado")