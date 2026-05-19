"""
core/browser.py — Gerencia o navegador Chrome via Selenium

Responsabilidades:
  - Iniciar o Chrome com as opções corretas
  - Abrir o WhatsApp Web
  - Aguardar o login via QR Code
  - Fechar o navegador com segurança
"""

import time

# Importação segura do Selenium (pode não estar instalado)
SELENIUM_OK = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    SELENIUM_OK = True
except ImportError:
    pass

from codigo.config import WHATSAPP_URL, WHATSAPP_TIMEOUT


class BrowserManager:
    """
    Gerencia o ciclo de vida do Chrome e da sessão WhatsApp Web.
    """

    def __init__(self, log_callback=None):
        """
        log_callback: função que recebe uma string para exibir no log da UI.
        Exemplo: log_callback("✅ Navegador iniciado")
        """
        self.driver = None
        self.wait = None
        self.log = log_callback or print  # usa print se não houver UI

    # ──────────────────────────────────────────────
    # INICIALIZAR
    # ──────────────────────────────────────────────
    def iniciar(self) -> bool:
        """
        Abre o Chrome e navega para o WhatsApp Web.
        Retorna True se conseguiu, False se houve erro.
        """
        if not SELENIUM_OK:
            self.log("❌ Selenium não instalado. Execute: pip install selenium")
            return False

        try:
            self.log("🌐 Iniciando navegador Chrome...")

            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            # Mantém o navegador aberto após o script encerrar
            options.add_experimental_option("detach", True)

            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, WHATSAPP_TIMEOUT)

            # Disfarça a automação para evitar detecção
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            self.driver.get(WHATSAPP_URL)
            self.log("✅ WhatsApp Web aberto. Escaneie o QR Code.")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao abrir navegador: {e}")
            return False

    # ──────────────────────────────────────────────
    # FECHAR
    # ──────────────────────────────────────────────
    def fechar(self):
        """Fecha o navegador com segurança."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.log("🔴 Navegador fechado.")
        except Exception as e:
            self.log(f"⚠️ Erro ao fechar navegador: {e}")

    # ──────────────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────────────
    def esta_ativo(self) -> bool:
        """Verifica se o driver ainda está respondendo."""
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False