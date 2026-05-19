"""
core/contacts.py — Importa e valida contatos de CSV, Excel ou texto

Responsabilidades:
  - Ler planilhas .xlsx e .csv
  - Processar lista de números colada manualmente
  - Validar e deduplicar números
"""

import re
import os

try:
    import pandas as pd
    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False


class ContactLoader:
    """
    Carrega contatos de diferentes fontes e os normaliza.
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        self.contatos: list[str] = []

    # ──────────────────────────────────────────────
    # CARREGAR PLANILHA (xlsx ou csv)
    # ──────────────────────────────────────────────
    def carregar_planilha(self, caminho: str) -> list[str]:
        """
        Lê um arquivo Excel ou CSV.
        Procura colunas chamadas: 'numero', 'telefone', 'phone', 'cel', 'whatsapp'
        (sem diferenciar maiúsculas/minúsculas).
        """
        if not PANDAS_OK:
            self.log("❌ Pandas não instalado. Execute: pip install pandas openpyxl")
            return []

        if not os.path.exists(caminho):
            self.log(f"❌ Arquivo não encontrado: {caminho}")
            return []

        try:
            # Detecta formato pelo sufixo
            ext = os.path.splitext(caminho)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(caminho, dtype=str)
            else:
                df = pd.read_excel(caminho, dtype=str)

            # Encontra a coluna de números (flexível)
            colunas_aceitas = ['numero', 'telefone', 'phone', 'cel', 'whatsapp', 'number']
            coluna_encontrada = None

            for col in df.columns:
                if col.strip().lower() in colunas_aceitas:
                    coluna_encontrada = col
                    break

            if coluna_encontrada is None:
                # Se não achar pelo nome, usa a primeira coluna
                coluna_encontrada = df.columns[0]
                self.log(f"⚠️ Coluna 'numero' não encontrada. Usando: '{coluna_encontrada}'")

            numeros_raw = df[coluna_encontrada].dropna().tolist()
            self.contatos = self._validar_lista(numeros_raw)

            self.log(f"✅ {len(self.contatos)} contatos carregados de {os.path.basename(caminho)}")
            return self.contatos

        except Exception as e:
            self.log(f"❌ Erro ao ler planilha: {e}")
            return []

    # ──────────────────────────────────────────────
    # PROCESSAR TEXTO COLADO
    # ──────────────────────────────────────────────
    def processar_texto(self, texto: str) -> list[str]:
        """
        Extrai números de um bloco de texto livre.
        Aceita formatos: (11) 99999-9999, +5511999999999, 11999999999, etc.
        """
        # Regex ampla: captura sequências numéricas com DDI opcional
        numeros_raw = re.findall(r'[\+]?[\d][\d\s\-\(\)]{7,15}[\d]', texto)
        self.contatos = self._validar_lista(numeros_raw)
        self.log(f"✅ {len(self.contatos)} contatos processados do texto")
        return self.contatos

    # ──────────────────────────────────────────────
    # VALIDAR E DEDUPLICAR
    # ──────────────────────────────────────────────
    def _validar_lista(self, numeros_raw: list) -> list[str]:
        """
        Remove caracteres não numéricos, filtra números muito curtos
        e elimina duplicatas, preservando a ordem.
        """
        vistos = set()
        resultado = []

        for num in numeros_raw:
            # Remove tudo que não é dígito ou +
            limpo = re.sub(r'[^\d]', '', str(num))

            # Número válido: entre 10 e 15 dígitos
            if 10 <= len(limpo) <= 15:
                if limpo not in vistos:
                    vistos.add(limpo)
                    resultado.append(limpo)

        return resultado

    # ──────────────────────────────────────────────
    # TOTAL
    # ──────────────────────────────────────────────
    def total(self) -> int:
        return len(self.contatos)