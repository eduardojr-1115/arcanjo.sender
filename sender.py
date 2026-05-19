"""
core/sender.py — Envia mensagens, imagens e PDFs via WhatsApp Web

Responsabilidades:
  - Navegar até o contato pelo número
  - Enviar texto (com suporte a Ctrl+V para evitar problemas de encoding)
  - Enviar imagem e PDF via campo de anexo
  - Simular digitação humana com delays
"""

import time
import re
import pyperclip

SELENIUM_OK = False
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    SELENIUM_OK = True
except ImportError:
    pass

from codigo.config import DELAY_TYPING, DELAY_AFTER_SEND, WHATSAPP_TIMEOUT


class MessageSender:
    """
    Envia mensagens e arquivos para um número via WhatsApp Web.
    Requer que BrowserManager já tenha aberto o navegador.
    """

    def __init__(self, driver, log_callback=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, WHATSAPP_TIMEOUT)
        self.log = log_callback or print

    # ──────────────────────────────────────────────
    # FORMATAR NÚMERO
    # ──────────────────────────────────────────────
    def formatar_numero(self, numero: str) -> str:
        """
        Remove caracteres inválidos e garante DDI 55 (Brasil).
        Exemplo: "(11) 99999-9999" → "5511999999999"
        """
        numero = re.sub(r'[^\d+]', '', str(numero))
        if not numero.startswith('55'):
            numero = '55' + numero.lstrip('0')
        return numero

    # ──────────────────────────────────────────────
    # ABRIR CONVERSA
    # ──────────────────────────────────────────────
    def _abrir_conversa(self, numero: str) -> bool:
        """Navega para a conversa com o número pelo link direto."""
        try:
            url = f"https://web.whatsapp.com/send?phone={numero}"
            self.driver.get(url)

            # Aguarda o campo de texto aparecer (confirma que a conversa abriu)
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab]')
                )
            )
            time.sleep(DELAY_TYPING)
            return True

        except Exception as e:
            self.log(f"⚠️ Não foi possível abrir conversa: {e}")
            return False

    # ──────────────────────────────────────────────
    # ENVIAR TEXTO
    # ──────────────────────────────────────────────
    def enviar_texto(self, numero: str, mensagem: str) -> bool:
        """
        Envia uma mensagem de texto.
        Usa Ctrl+V para colar, evitando problemas com emojis e acentos.
        """
        try:
            num = self.formatar_numero(numero)
            self.log(f"📤 Texto → {num}")

            if not self._abrir_conversa(num):
                return False

            # Copia a mensagem para a área de transferência
            pyperclip.copy(mensagem)

            # Localiza o campo de texto
            caixa = self.driver.find_element(
                By.XPATH,
                '//div[@contenteditable="true"][@data-tab]'
            )
            caixa.click()
            time.sleep(0.5)

            # Cola e envia
            caixa.send_keys(Keys.CONTROL + "v")
            time.sleep(0.8)
            caixa.send_keys(Keys.ENTER)
            time.sleep(DELAY_AFTER_SEND)

            self.log(f"✅ Texto enviado → {num}")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao enviar texto para {numero}: {e}")
            return False

    # ──────────────────────────────────────────────
    # ENVIAR ARQUIVO (imagem ou PDF)
    # ──────────────────────────────────────────────
    def enviar_arquivo(self, numero: str, caminho_arquivo: str,
                       legenda: str = "") -> bool:
        """
        Envia uma imagem ou PDF.
        caminho_arquivo: caminho absoluto no disco.
        legenda: texto opcional junto ao arquivo.
        """
        try:
            import os
            if not os.path.exists(caminho_arquivo):
                self.log(f"❌ Arquivo não encontrado: {caminho_arquivo}")
                return False

            num = self.formatar_numero(numero)
            self.log(f"📎 Arquivo → {num} ({os.path.basename(caminho_arquivo)})")

            if not self._abrir_conversa(num):
                return False

            # Clica no botão de clipe (anexo)
            clipe = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//span[@data-icon="attach-menu-plus"]')
                )
            )
            clipe.click()
            time.sleep(1)

            # Seleciona o input de arquivo
            input_arquivo = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
                               '|//input[@accept=".pdf,.doc,.docx"]'
                               '|//input[@type="file"]')
                )
            )
            input_arquivo.send_keys(caminho_arquivo)
            time.sleep(2)

            # Adiciona legenda se houver
            if legenda:
                pyperclip.copy(legenda)
                try:
                    campo_legenda = self.driver.find_element(
                        By.XPATH, '//div[@contenteditable="true"][@data-tab]'
                    )
                    campo_legenda.send_keys(Keys.CONTROL + "v")
                    time.sleep(0.5)
                except Exception:
                    pass  # Legenda é opcional

            # Botão enviar
            enviar_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//span[@data-icon="send"]')
                )
            )
            enviar_btn.click()
            time.sleep(DELAY_AFTER_SEND)

            self.log(f"✅ Arquivo enviado → {num}")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao enviar arquivo para {numero}: {e}")
            return False

    # ──────────────────────────────────────────────
    # ENVIAR CONJUNTO (texto + arquivo)
    # ──────────────────────────────────────────────
    def enviar_conjunto(self, numero: str, mensagem: str,
                        caminho_arquivo: str) -> bool:
        """
        Envia texto e arquivo para o mesmo contato.
        """
        ok_texto = self.enviar_texto(numero, mensagem)
        time.sleep(2)
        ok_arquivo = self.enviar_arquivo(numero, caminho_arquivo)
        return ok_texto and ok_arquivo