"""
tests/test_suite.py — Suite de testes integrados do sistema

Testa cada módulo automaticamente e exibe:
  ✅ etapa funcionando
  ❌ etapa com erro
  ⚠️ possível problema

Como rodar manualmente:
    python tests/test_suite.py
"""

import os
import sys
import time
import tempfile

# Garante que o módulo raiz seja encontrado ao rodar diretamente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ══════════════════════════════════════════════════════════════
# CLASSE DE RESULTADO DE TESTE
# ══════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, nome: str, ok: bool, detalhe: str = "", aviso: bool = False):
        self.nome = nome
        self.ok = ok
        self.detalhe = detalhe
        self.aviso = aviso  # True = ⚠️ (não é erro fatal, mas atenção)

    def __str__(self):
        if self.aviso:
            icone = "⚠️ "
        elif self.ok:
            icone = "✅"
        else:
            icone = "❌"

        linha = f"  {icone} {self.nome}"
        if self.detalhe:
            linha += f"\n       → {self.detalhe}"
        return linha


# ══════════════════════════════════════════════════════════════
# SUITE DE TESTES
# ══════════════════════════════════════════════════════════════

class TestSuite:
    """
    Executa todos os testes e retorna os resultados.
    Pode ser usado pela UI (passando log_callback) ou no terminal.
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self.resultados: list[TestResult] = []

    # ──────────────────────────────────────────────
    # EXECUTAR TODOS OS TESTES
    # ──────────────────────────────────────────────
    def executar_todos(self):
        """Roda todos os testes na ordem lógica."""
        self.resultados = []
        self.log("\n🧪 Iniciando bateria de testes...\n")

        testes = [
            self._testar_dependencias,
            self._testar_selenium,
            self._testar_contatos_excel,
            self._testar_contatos_csv,
            self._testar_contatos_texto,
            self._testar_antispam_delay,
            self._testar_variacao_local,
            self._testar_variacao_ia,
            self._testar_formatacao_numero,
            self._testar_abertura_browser,
        ]

        for teste in testes:
            try:
                resultado = teste()
                self.resultados.append(resultado)
                self.log(str(resultado))
            except Exception as e:
                r = TestResult(
                    nome=teste.__name__,
                    ok=False,
                    detalhe=f"Exceção inesperada: {e}"
                )
                self.resultados.append(r)
                self.log(str(r))

        self._exibir_resumo()
        return self.resultados

    # ──────────────────────────────────────────────
    # TESTE 1 — DEPENDÊNCIAS PYTHON
    # ──────────────────────────────────────────────
    def _testar_dependencias(self) -> TestResult:
        nome = "Dependências Python"
        faltando = []
        avisos = []

        pacotes_obrigatorios = {
            'selenium': 'selenium',
            'pandas': 'pandas',
            'pyperclip': 'pyperclip',
            'openpyxl': 'openpyxl',
        }
        pacotes_opcionais = {
            'anthropic': 'anthropic (IA)',
        }

        for modulo, label in pacotes_obrigatorios.items():
            try:
                __import__(modulo)
            except ImportError:
                faltando.append(label)

        for modulo, label in pacotes_opcionais.items():
            try:
                __import__(modulo)
            except ImportError:
                avisos.append(label)

        if faltando:
            return TestResult(nome, ok=False,
                              detalhe=f"Instale: pip install {' '.join(faltando)}")
        if avisos:
            return TestResult(nome, ok=True,
                              detalhe=f"Opcional não instalado: {', '.join(avisos)} — IA desativada",
                              aviso=True)
        return TestResult(nome, ok=True, detalhe="Todos os pacotes encontrados")

    # ──────────────────────────────────────────────
    # TESTE 2 — SELENIUM / CHROME
    # ──────────────────────────────────────────────
    def _testar_selenium(self) -> TestResult:
        nome = "Selenium / ChromeDriver"
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_argument("--headless")  # Roda sem abrir janela
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com")
            titulo = driver.title
            driver.quit()

            return TestResult(nome, ok=True, detalhe=f"Chrome OK — Página: '{titulo}'")

        except Exception as e:
            return TestResult(nome, ok=False,
                              detalhe=f"Verifique se Chrome e ChromeDriver estão instalados: {e}")

    # ──────────────────────────────────────────────
    # TESTE 3 — LEITURA DE EXCEL
    # ──────────────────────────────────────────────
    def _testar_contatos_excel(self) -> TestResult:
        nome = "Leitura de planilha Excel (.xlsx)"
        try:
            import pandas as pd

            # Cria um arquivo Excel temporário para teste
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
                caminho = f.name

            df = pd.DataFrame({'numero': ['11999990001', '21888880002', '31777770003']})
            df.to_excel(caminho, index=False)

            from core.contacts import ContactLoader
            loader = ContactLoader()
            contatos = loader.carregar_planilha(caminho)
            os.unlink(caminho)

            if len(contatos) == 3:
                return TestResult(nome, ok=True, detalhe=f"{len(contatos)} contatos lidos corretamente")
            else:
                return TestResult(nome, ok=False, detalhe=f"Esperava 3, leu {len(contatos)}")

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 4 — LEITURA DE CSV
    # ──────────────────────────────────────────────
    def _testar_contatos_csv(self) -> TestResult:
        nome = "Leitura de planilha CSV (.csv)"
        try:
            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
                f.write("numero\n11911111111\n21922222222\n")
                caminho = f.name

            from core.contacts import ContactLoader
            loader = ContactLoader()
            contatos = loader.carregar_planilha(caminho)
            os.unlink(caminho)

            if len(contatos) == 2:
                return TestResult(nome, ok=True, detalhe=f"{len(contatos)} contatos lidos")
            else:
                return TestResult(nome, ok=False, detalhe=f"Esperava 2, leu {len(contatos)}")

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 5 — PROCESSAR TEXTO COLADO
    # ──────────────────────────────────────────────
    def _testar_contatos_texto(self) -> TestResult:
        nome = "Processar lista de números (texto)"
        try:
            from core.contacts import ContactLoader
            loader = ContactLoader()

            texto = """
            (11) 99999-0001
            +5521888880002
            31 7 7777-0003
            numero_invalido
            123
            """
            contatos = loader.processar_texto(texto)

            if len(contatos) >= 2:
                return TestResult(nome, ok=True,
                                  detalhe=f"{len(contatos)} números válidos extraídos")
            else:
                return TestResult(nome, ok=False,
                                  detalhe=f"Extraiu apenas {len(contatos)} (esperava ≥2)")

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 6 — DELAYS ANTI-SPAM
    # ──────────────────────────────────────────────
    def _testar_antispam_delay(self) -> TestResult:
        nome = "Sistema Anti-Spam / Delays"
        try:
            from core.antispam import AntiSpam

            # Substitui delays reais por versão acelerada para teste
            import core.antispam as am
            am.DELAY_MIN = 0
            am.DELAY_MAX = 0
            am.ANTISPAM_PAUSA = 0

            spam = AntiSpam()
            spam.registrar_envio()
            spam.simular_digitacao("Olá, tudo bem?")

            return TestResult(nome, ok=True,
                              detalhe="Delays, contadores e simulação de digitação OK")
        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 7 — VARIAÇÃO LOCAL DE MENSAGEM
    # ──────────────────────────────────────────────
    def _testar_variacao_local(self) -> TestResult:
        nome = "Variação de mensagem (modo local)"
        try:
            from core.ai_variator import AIVariator
            variator = AIVariator()

            original = "Olá! Tenho uma oferta especial para você."
            variacao = variator._variar_local(original)

            if variacao and isinstance(variacao, str):
                return TestResult(nome, ok=True,
                                  detalhe=f'Variação gerada: "{variacao[:50]}..."')
            else:
                return TestResult(nome, ok=False, detalhe="Variação retornou vazio")

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 8 — VARIAÇÃO COM IA (opcional)
    # ──────────────────────────────────────────────
    def _testar_variacao_ia(self) -> TestResult:
        nome = "Variação de mensagem com IA (Anthropic)"
        try:
            from codigo.config import ANTHROPIC_API_KEY
            if not ANTHROPIC_API_KEY:
                return TestResult(nome, ok=True, aviso=True,
                                  detalhe="API Key não configurada — IA desativada (opcional)")

            from core.ai_variator import AIVariator
            variator = AIVariator()

            if not variator.ia_disponivel:
                return TestResult(nome, ok=True, aviso=True,
                                  detalhe="Módulo anthropic não instalado — usando variações locais")

            variacao = variator._variar_com_ia("Olá, tenho uma oferta especial.")
            return TestResult(nome, ok=True,
                              detalhe=f'Resposta da IA: "{variacao[:60]}..."')

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 9 — FORMATAÇÃO DE NÚMERO
    # ──────────────────────────────────────────────
    def _testar_formatacao_numero(self) -> TestResult:
        nome = "Formatação de números de telefone"
        try:
            from core.sender import MessageSender

            # Cria sender sem driver (só para testar o método estático)
            class FakeDriver:
                pass

            sender = MessageSender.__new__(MessageSender)
            sender.log = print

            casos = [
                ("11999990001", "5511999990001"),
                ("(21) 9 8888-7777", "5521988887777"),
                ("+5531977776666", "5531977776666"),
            ]

            erros = []
            for entrada, esperado in casos:
                resultado = sender.formatar_numero(entrada)
                if resultado != esperado:
                    erros.append(f"'{entrada}' → '{resultado}' (esperado '{esperado}')")

            if not erros:
                return TestResult(nome, ok=True,
                                  detalhe=f"{len(casos)} formatos testados com sucesso")
            else:
                return TestResult(nome, ok=False,
                                  detalhe="; ".join(erros))

        except Exception as e:
            return TestResult(nome, ok=False, detalhe=str(e))

    # ──────────────────────────────────────────────
    # TESTE 10 — ABERTURA DO BROWSER (headless)
    # ──────────────────────────────────────────────
    def _testar_abertura_browser(self) -> TestResult:
        nome = "Abertura do navegador (modo silencioso)"
        try:
            from core.browser import BrowserManager, SELENIUM_OK
            if not SELENIUM_OK:
                return TestResult(nome, ok=False,
                                  detalhe="Selenium não instalado")

            from selenium.webdriver.chrome.options import Options
            from selenium import webdriver

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)
            driver.get("about:blank")
            driver.quit()

            return TestResult(nome, ok=True, detalhe="Chrome abre e fecha corretamente")

        except Exception as e:
            return TestResult(nome, ok=False,
                              detalhe=f"Chrome não disponível: {e}")

    # ──────────────────────────────────────────────
    # RESUMO FINAL
    # ──────────────────────────────────────────────
    def _exibir_resumo(self):
        total = len(self.resultados)
        ok = sum(1 for r in self.resultados if r.ok and not r.aviso)
        avisos = sum(1 for r in self.resultados if r.aviso)
        erros = sum(1 for r in self.resultados if not r.ok)

        self.log("\n" + "─" * 50)
        self.log(f"📊 RESULTADO: {ok} ✅  {avisos} ⚠️  {erros} ❌  de {total} testes")
        if erros == 0:
            self.log("🎉 Sistema pronto para uso!")
        else:
            self.log("🔧 Corrija os erros acima antes de usar.")
        self.log("─" * 50 + "\n")


# ── Execução direta no terminal ──────────────────
if __name__ == "__main__":
    suite = TestSuite()
    suite.executar_todos()