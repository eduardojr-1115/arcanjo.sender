"""
core/ai_variator.py — Varia mensagens para evitar detecção de spam

Duas estratégias disponíveis:
  1. IA Real (Anthropic API) — reescreve com linguagem natural
  2. Variações Locais — modifica texto com emojis/formatação (sem internet)
"""

import random

from codigo.config import ANTHROPIC_API_KEY, IA_MODEL, IA_MAX_TOKENS


class AIVariator:
    """
    Gera variações de uma mensagem para cada envio.
    Reduz chance de banimento por mensagens idênticas repetidas.
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self._checar_ia()

    # ──────────────────────────────────────────────
    # VERIFICAR DISPONIBILIDADE DA IA
    # ──────────────────────────────────────────────
    def _checar_ia(self):
        """Verifica se a API Anthropic está configurada."""
        self.ia_disponivel = False

        if not ANTHROPIC_API_KEY:
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            self.ia_disponivel = True
            self.log("🤖 IA Anthropic conectada")
        except ImportError:
            self.log("⚠️ Módulo 'anthropic' não instalado. Usando variações locais.")

    # ──────────────────────────────────────────────
    # VARIAR MENSAGEM (ponto de entrada principal)
    # ──────────────────────────────────────────────
    def variar(self, mensagem: str, usar_ia: bool = True) -> str:
        """
        Retorna uma variação da mensagem.
        Se IA estiver ativa e disponível, usa a API.
        Caso contrário, aplica variações locais.
        """
        if usar_ia and self.ia_disponivel:
            return self._variar_com_ia(mensagem)
        else:
            return self._variar_local(mensagem)

    # ──────────────────────────────────────────────
    # VARIAÇÃO COM IA (Anthropic)
    # ──────────────────────────────────────────────
    def _variar_com_ia(self, mensagem: str) -> str:
        """
        Usa o Claude para reescrever a mensagem de forma natural.
        """
        try:
            prompt = (
                f"Reescreva a mensagem abaixo de forma ligeiramente diferente, "
                f"mantendo o mesmo significado. Use linguagem informal e natural. "
                f"Responda APENAS com a mensagem reescrita, sem explicações.\n\n"
                f"Mensagem: {mensagem}"
            )

            resposta = self.client.messages.create(
                model=IA_MODEL,
                max_tokens=IA_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            variacao = resposta.content[0].text.strip()
            self.log("🤖 Variação gerada pela IA")
            return variacao

        except Exception as e:
            self.log(f"⚠️ Erro na IA, usando variação local: {e}")
            return self._variar_local(mensagem)

    # ──────────────────────────────────────────────
    # VARIAÇÃO LOCAL (sem internet)
    # ──────────────────────────────────────────────
    def _variar_local(self, mensagem: str) -> str:
        """
        Aplica pequenas modificações ao texto:
        - Adiciona emojis
        - Formata em negrito/itálico
        - Modifica pontuação
        Escolhe aleatoriamente entre as variações.
        """
        emojis = ["✨", "👋", "🔥", "💬", "⚡", "🎯", "💡", "👍"]
        emoji = random.choice(emojis)

        variacoes = [
            mensagem,                                            # original
            f"{mensagem} {emoji}",                              # emoji no final
            f"{emoji} {mensagem}",                              # emoji no início
            f"*{mensagem}*",                                    # negrito
            mensagem.replace(".", ".."),                        # reticências
            mensagem.replace(",", " —"),                        # travessão
            mensagem + "\n\nResponda quando puder 😊",          # call-to-action
        ]

        return random.choice(variacoes)