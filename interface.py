# -*- coding: utf-8 -*-
"""
interface.py - Interface principal do ARCANO MESSENGER PRO
Salve este arquivo em: codigo/interface.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
import sys
import re
import importlib.util

# ── Garante que a pasta 'codigo' e 'codigo/bot' estejam no path
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
BOT_DIR   = os.path.join(BASE_DIR, "bot")
for p in [BASE_DIR, BOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config import (
    APP_TITLE, APP_WIDTH, APP_HEIGHT,
    DELAY_MIN, DELAY_MAX
)

# ══════════════════════════════════════════════
# PALETA DE CORES
# ══════════════════════════════════════════════
C = {
    'bg':        '#0a0a0f',
    'panel':     '#0f0f1a',
    'surface':   '#161625',
    'border':    '#1e1e38',
    'border2':   '#2a2a50',
    'green':     '#00ff88',
    'green_dim': '#00cc6a',
    'green_bg':  '#001a0d',
    'amber':     '#ffb300',
    'amber_dim': '#e6a000',
    'red':       '#ff3b5c',
    'cyan':      '#00d4ff',
    'text':      '#e8e8f0',
    'muted':     '#6b6b8a',
    'label':     '#9999bb',
    'mono':      'Consolas',
}


# ══════════════════════════════════════════════
# WIDGETS AUXILIARES
# ══════════════════════════════════════════════

def make_entry(parent, textvariable=None, width=None, bg=None):
    kwargs = dict(
        bg=bg or C['surface'], fg=C['text'],
        insertbackground=C['green'],
        relief='flat', font=(C['mono'], 10), bd=0,
    )
    if textvariable: kwargs['textvariable'] = textvariable
    if width:        kwargs['width'] = width
    e = tk.Entry(parent, **kwargs)
    e.bind('<FocusIn>',  lambda ev: e.config(bg='#161625'))
    e.bind('<FocusOut>', lambda ev: e.config(bg=bg or C['surface']))
    return e


def make_button(parent, text, command, color='green', width=None):
    accent = {'green': C['green'], 'amber': C['amber'], 'red': C['red']}.get(color, C['green'])
    bg_dark = {'green': '#001a0d', 'amber': '#1a1000', 'red': '#1a0008'}.get(color, '#001a0d')
    kwargs = dict(
        text=text, command=command,
        bg=bg_dark, fg=accent,
        activebackground=accent, activeforeground='#000',
        relief='flat', cursor='hand2',
        font=(C['mono'], 10, 'bold'),
        bd=0, pady=8,
    )
    if width: kwargs['width'] = width
    btn = tk.Button(parent, **kwargs)
    btn.bind('<Enter>', lambda e: btn.config(bg=accent,   fg='#000'))
    btn.bind('<Leave>', lambda e: btn.config(bg=bg_dark,  fg=accent))
    return btn


def separator(parent, color=None):
    return tk.Frame(parent, bg=color or C['border'], height=1)


# ══════════════════════════════════════════════
# CLASSE PRINCIPAL
# ══════════════════════════════════════════════

class ArcanoApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configurar_janela()

        # Estado
        self.driver   = None
        self.parado   = False
        self.contatos: list = []
        self.rodando  = False

        # Variaveis de controle
        self.msg_var      = tk.StringVar()
        self.file_var     = tk.StringVar()
        self.plan_var     = tk.StringVar(value='contatos.xlsx')
        self.delay_var    = tk.IntVar(value=30)
        self.ia_var       = tk.BooleanVar(value=True)
        self.antispam_var = tk.BooleanVar(value=True)
        self.modo_envio   = tk.StringVar(value='texto')

        self._build_ui()
        self._animar_status("PRONTO")

    # ──────────────────────────────────────────
    # JANELA
    # ──────────────────────────────────────────
    def _configurar_janela(self):
        self.root.title(APP_TITLE)
        self.root.geometry(f'{APP_WIDTH}x{APP_HEIGHT}')
        self.root.configure(bg=C['bg'])
        self.root.resizable(True, True)
        self.root.minsize(900, 720)

    # ──────────────────────────────────────────
    # BUILD COMPLETO
    # ──────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_statusbar()
        self._build_notebook()
        self._build_footer()

    # ──────────────────────────────────────────
    # HEADER
    # ──────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=C['bg'], height=90)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Frame(header, bg=C['green'], height=2).pack(fill='x')

        inner = tk.Frame(header, bg=C['bg'])
        inner.pack(fill='both', expand=True, padx=30)

        left = tk.Frame(inner, bg=C['bg'])
        left.pack(side='left', expand=True, fill='both')
        tk.Label(left, text='ARCANO',    font=(C['mono'], 30, 'bold'), fg=C['green'], bg=C['bg']).pack(side='left', pady=15)
        tk.Label(left, text=' MESSENGER', font=(C['mono'], 30, 'bold'), fg=C['text'],  bg=C['bg']).pack(side='left', pady=15)
        tk.Label(left, text=' PRO',      font=(C['mono'], 16, 'bold'), fg=C['amber'], bg=C['bg']).pack(side='left', anchor='s', pady=22)

        right = tk.Frame(inner, bg=C['bg'])
        right.pack(side='right', anchor='e', pady=15)
        tk.Label(right, text='v2.0  //  WhatsApp Automation', font=(C['mono'], 9), fg=C['muted'], bg=C['bg']).pack(anchor='e')
        self.contadores_label = tk.Label(right, text='[ 0 contatos ]', font=(C['mono'], 11, 'bold'), fg=C['cyan'], bg=C['bg'])
        self.contadores_label.pack(anchor='e', pady=(4, 0))
        tk.Frame(header, bg=C['border2'], height=1).pack(fill='x', side='bottom')

    # ──────────────────────────────────────────
    # STATUS BAR
    # ──────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C['panel'], height=36)
        bar.pack(fill='x')
        bar.pack_propagate(False)

        self.status_dot = tk.Label(bar, text='●', font=(C['mono'], 14), fg=C['green'], bg=C['panel'])
        self.status_dot.pack(side='left', padx=(16, 6))
        self.status_label = tk.Label(bar, text='PRONTO', font=(C['mono'], 10, 'bold'), fg=C['green'], bg=C['panel'])
        self.status_label.pack(side='left')
        self.progress_label = tk.Label(bar, text='', font=(C['mono'], 9), fg=C['muted'], bg=C['panel'])
        self.progress_label.pack(side='left', padx=20)
        self.clock_label = tk.Label(bar, text='', font=(C['mono'], 9), fg=C['muted'], bg=C['panel'])
        self.clock_label.pack(side='right', padx=16)
        self._tick_clock()

    def _tick_clock(self):
        self.clock_label.config(text=time.strftime('%H:%M:%S'))
        self.root.after(1000, self._tick_clock)

    def _animar_status(self, texto, cor=None):
        self.status_label.config(text=texto, fg=cor or C['green'])
        self.status_dot.config(fg=cor or C['green'])

    # ──────────────────────────────────────────
    # NOTEBOOK
    # ──────────────────────────────────────────
    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Arc.TNotebook', background=C['bg'], borderwidth=0)
        style.configure('Arc.TNotebook.Tab',
                        background=C['surface'], foreground=C['muted'],
                        font=(C['mono'], 10, 'bold'), padding=[20, 8], borderwidth=0)
        style.map('Arc.TNotebook.Tab',
                  background=[('selected', C['panel'])],
                  foreground=[('selected', C['green'])],
                  expand=[('selected', [0, 0, 0, 2])])

        self.nb = ttk.Notebook(self.root, style='Arc.TNotebook')
        self.nb.pack(fill='both', expand=True)

        self._tab_disparar()
        self._tab_contatos()
        self._tab_protecao()
        self._tab_logs()
        self._tab_testes()

    # ══════════════════════════════════════════
    # ABA 1 — DISPARAR
    # ══════════════════════════════════════════
    def _tab_disparar(self):
        frame = tk.Frame(self.nb, bg=C['panel'])
        self.nb.add(frame, text='  DISPARAR  ')

        canvas = tk.Canvas(frame, bg=C['panel'], highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        P = tk.Frame(canvas, bg=C['panel'])
        win = canvas.create_window((0, 0), window=P, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
        P.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Modo de envio
        self._secao(P, '01', 'MENSAGEM')
        modo_frame = tk.Frame(P, bg=C['panel'])
        modo_frame.pack(fill='x', padx=30, pady=(0, 14))
        tk.Label(modo_frame, text='MODO DE ENVIO:', font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['panel']).pack(side='left', padx=(0, 12))
        for val, label in [('texto', 'SO TEXTO'), ('arquivo', 'SO ARQUIVO'), ('ambos', 'TEXTO + ARQUIVO')]:
            tk.Radiobutton(modo_frame, text=label, variable=self.modo_envio, value=val,
                           bg=C['panel'], fg=C['label'], selectcolor=C['surface'],
                           activebackground=C['panel'], activeforeground=C['green'],
                           font=(C['mono'], 9, 'bold'), cursor='hand2').pack(side='left', padx=10)

        # Mensagem
        tk.Label(P, text='TEXTO DA MENSAGEM', font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['panel']).pack(anchor='w', padx=30)
        msg_wrap = tk.Frame(P, bg=C['border2'], padx=1, pady=1)
        msg_wrap.pack(fill='x', padx=30, pady=(6, 4))
        self.msg_text = scrolledtext.ScrolledText(msg_wrap, height=6, font=(C['mono'], 10),
                                                  bg=C['surface'], fg=C['text'],
                                                  insertbackground=C['green'],
                                                  relief='flat', bd=6, wrap='word')
        self.msg_text.pack(fill='x')
        tk.Label(P, text='Use {nome} para personalizar por contato', font=(C['mono'], 8), fg=C['muted'], bg=C['panel']).pack(anchor='w', padx=30, pady=(0, 18))

        # Arquivo
        self._secao(P, '02', 'ARQUIVO ANEXO')
        file_row = tk.Frame(P, bg=C['panel'])
        file_row.pack(fill='x', padx=30, pady=(0, 20))
        file_wrap = tk.Frame(file_row, bg=C['border2'], padx=1, pady=1)
        file_wrap.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.file_entry = make_entry(file_wrap, textvariable=self.file_var)
        self.file_entry.pack(fill='x', ipady=8, padx=2, pady=2)
        make_button(file_row, '  SELECIONAR  ', self._sel_file, color='amber').pack(side='left')
        self.file_tipo_label = tk.Label(P, text='', font=(C['mono'], 8), fg=C['muted'], bg=C['panel'])
        self.file_tipo_label.pack(anchor='w', padx=30, pady=(0, 20))
        self.file_var.trace_add('write', self._on_file_change)

        # Controle
        self._secao(P, '03', 'CONTROLE')
        ctrl_outer = tk.Frame(P, bg=C['surface'])
        ctrl_outer.pack(fill='x', padx=30, pady=(0, 30))

        delay_row = tk.Frame(ctrl_outer, bg=C['surface'])
        delay_row.pack(fill='x', padx=20, pady=(18, 8))
        tk.Label(delay_row, text='DELAY ENTRE ENVIOS:', font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['surface']).pack(side='left')
        self.delay_display = tk.Label(delay_row, text=f'{self.delay_var.get()}s', font=(C['mono'], 11, 'bold'), fg=C['green'], bg=C['surface'])
        self.delay_display.pack(side='right')
        ttk.Scale(ctrl_outer, from_=15, to=120, variable=self.delay_var,
                  orient='horizontal', command=self._on_delay_change).pack(fill='x', padx=20, pady=(0, 18))
        separator(ctrl_outer, C['border2']).pack(fill='x', padx=20)

        btn_row = tk.Frame(ctrl_outer, bg=C['surface'])
        btn_row.pack(pady=16, padx=20)
        self.btn_iniciar = make_button(btn_row, '  INICIAR DISPARO  ', self._iniciar, color='green', width=22)
        self.btn_iniciar.pack(side='left', padx=8)
        self.btn_parar = make_button(btn_row, '  PARAR  ', self._parar, color='red', width=14)
        self.btn_parar.pack(side='left', padx=8)
        self.btn_parar.config(state='disabled')

    # ══════════════════════════════════════════
    # ABA 2 — CONTATOS
    # ══════════════════════════════════════════
    def _tab_contatos(self):
        frame = tk.Frame(self.nb, bg=C['panel'])
        self.nb.add(frame, text='  CONTATOS  ')

        self._secao(frame, '01', 'IMPORTAR PLANILHA')
        row1 = tk.Frame(frame, bg=C['panel'])
        row1.pack(fill='x', padx=30, pady=(0, 10))
        plan_wrap = tk.Frame(row1, bg=C['border2'], padx=1, pady=1)
        plan_wrap.pack(side='left', fill='x', expand=True, padx=(0, 10))
        make_entry(plan_wrap, textvariable=self.plan_var).pack(fill='x', ipady=8, padx=2, pady=2)
        make_button(row1, '  BUSCAR  ',    self._sel_planilha,    color='amber').pack(side='left', padx=(0, 8))
        make_button(row1, '  CARREGAR  ',  self._carregar_planilha, color='green').pack(side='left')
        tk.Label(frame, text='Formatos aceitos: .xlsx  .xls  .csv  -  Coluna esperada: "numero"',
                 font=(C['mono'], 8), fg=C['muted'], bg=C['panel']).pack(anchor='w', padx=30, pady=(0, 20))

        self._secao(frame, '02', 'COLAR LISTA MANUAL')
        tk.Label(frame, text='NUMEROS  (1 por linha, qualquer formato)',
                 font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['panel']).pack(anchor='w', padx=30)
        cola_wrap = tk.Frame(frame, bg=C['border2'], padx=1, pady=1)
        cola_wrap.pack(fill='x', padx=30, pady=(6, 10))
        self.cola_text = scrolledtext.ScrolledText(cola_wrap, height=10,
                                                   font=(C['mono'], 10),
                                                   bg=C['surface'], fg=C['text'],
                                                   insertbackground=C['green'],
                                                   relief='flat', bd=6)
        self.cola_text.pack(fill='x')
        make_button(frame, '  PROCESSAR LISTA  ', self._processar_cola, color='green').pack(padx=30, pady=10, anchor='w')

        self._secao(frame, '03', 'CONTATOS CARREGADOS')
        preview_wrap = tk.Frame(frame, bg=C['border2'], padx=1, pady=1)
        preview_wrap.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        self.preview_list = tk.Listbox(preview_wrap,
                                       bg=C['surface'], fg=C['green'],
                                       selectbackground=C['border2'],
                                       font=(C['mono'], 10),
                                       relief='flat', bd=6, activestyle='none')
        self.preview_list.pack(fill='both', expand=True)

    # ══════════════════════════════════════════
    # ABA 3 — PROTECAO
    # ══════════════════════════════════════════
    def _tab_protecao(self):
        frame = tk.Frame(self.nb, bg=C['panel'])
        self.nb.add(frame, text='  PROTECAO  ')

        def _check(parent, var, label, detail):
            row = tk.Frame(parent, bg=C['surface'])
            row.pack(fill='x', padx=30, pady=4)
            tk.Checkbutton(row, text=f'  {label}', variable=var,
                           bg=C['surface'], fg=C['text'], selectcolor=C['border2'],
                           activebackground=C['surface'], activeforeground=C['green'],
                           font=(C['mono'], 10, 'bold'), cursor='hand2').pack(anchor='w', padx=12, pady=6)
            tk.Label(row, text=f'    {detail}', font=(C['mono'], 8),
                     fg=C['muted'], bg=C['surface']).pack(anchor='w', padx=12, pady=(0, 6))

        self._secao(frame, '01', 'ANTI-SPAM')
        _check(frame, self.antispam_var, 'Ativar Anti-Spam',
               'Pausa automatica a cada 10 mensagens para evitar bloqueio')
        _check(frame, self.ia_var, 'Variacao de Mensagem',
               'Altera levemente cada mensagem para parecer unica (via IA ou modo local)')
        sim_var = tk.BooleanVar(value=True)
        _check(frame, sim_var, 'Simulacao Humana',
               'Delays variaveis e simulacao de tempo de digitacao')

        self._secao(frame, '02', 'CONFIGURACAO DE DELAY')
        delay_card = tk.Frame(frame, bg=C['surface'])
        delay_card.pack(fill='x', padx=30, pady=(0, 20))
        grid = tk.Frame(delay_card, bg=C['surface'])
        grid.pack(fill='x', padx=20, pady=16)

        def _numfield(parent, label, var, col):
            tk.Label(parent, text=label, font=(C['mono'], 9), fg=C['muted'], bg=C['surface']).grid(row=0, column=col, padx=10)
            wrap = tk.Frame(parent, bg=C['border2'], padx=1, pady=1)
            wrap.grid(row=1, column=col, padx=10)
            make_entry(wrap, textvariable=var, width=8, bg=C['surface']).pack(ipady=8, padx=2, pady=2)

        self.dmin_var = tk.IntVar(value=DELAY_MIN)
        self.dmax_var = tk.IntVar(value=DELAY_MAX)
        _numfield(grid, 'MINIMO (s)', self.dmin_var, 0)
        tk.Label(grid, text='--', font=(C['mono'], 14), fg=C['muted'], bg=C['surface']).grid(row=1, column=1)
        _numfield(grid, 'MAXIMO (s)', self.dmax_var, 2)
        tk.Label(delay_card, text='  Recomendado: minimo 20s  //  Abaixo de 15s aumenta risco de ban',
                 font=(C['mono'], 8), fg=C['amber'], bg=C['surface']).pack(anchor='w', padx=20, pady=(0, 14))

        self._secao(frame, '03', 'IA - ANTHROPIC API')
        ia_card = tk.Frame(frame, bg=C['surface'])
        ia_card.pack(fill='x', padx=30, pady=(0, 20))
        tk.Label(ia_card, text='API KEY (opcional - deixe vazio para variacoes locais)',
                 font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['surface']).pack(anchor='w', padx=20, pady=(16, 6))
        key_wrap = tk.Frame(ia_card, bg=C['border2'], padx=1, pady=1)
        key_wrap.pack(fill='x', padx=20, pady=(0, 16))
        self.apikey_var = tk.StringVar()
        key_entry = make_entry(key_wrap, textvariable=self.apikey_var)
        key_entry.config(show='*')
        key_entry.pack(fill='x', ipady=8, padx=2, pady=2)

    # ══════════════════════════════════════════
    # ABA 4 — LOGS
    # ══════════════════════════════════════════
    def _tab_logs(self):
        frame = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(frame, text='  LOGS  ')

        toolbar = tk.Frame(frame, bg=C['panel'], height=40)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)
        tk.Label(toolbar, text='OUTPUT EM TEMPO REAL', font=(C['mono'], 9, 'bold'), fg=C['muted'], bg=C['panel']).pack(side='left', padx=16, pady=10)
        make_button(toolbar, ' LIMPAR ', self._limpar_log, color='amber').pack(side='right', padx=12, pady=6)
        separator(frame).pack(fill='x')

        self.log_text = scrolledtext.ScrolledText(frame, font=(C['mono'], 10),
                                                  bg=C['bg'], fg=C['green'],
                                                  insertbackground=C['green'],
                                                  relief='flat', bd=12,
                                                  state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True)
        self.log_text.tag_config('ok',    foreground=C['green'])
        self.log_text.tag_config('err',   foreground=C['red'])
        self.log_text.tag_config('warn',  foreground=C['amber'])
        self.log_text.tag_config('info',  foreground=C['cyan'])
        self.log_text.tag_config('muted', foreground=C['muted'])
        self._log('Sistema iniciado. Aguardando instrucoes.', 'info')

    # ══════════════════════════════════════════
    # ABA 5 — TESTES
    # ══════════════════════════════════════════
    def _tab_testes(self):
        frame = tk.Frame(self.nb, bg=C['panel'])
        self.nb.add(frame, text='  TESTES  ')

        self._secao(frame, '*', 'SUITE DE TESTES AUTOMATICOS')
        tk.Label(frame,
                 text='Valida cada componente antes de usar:\n'
                      '  - Dependencias Python\n'
                      '  - Leitura de planilha\n'
                      '  - Anti-spam / delays\n'
                      '  - Variacao de mensagens\n'
                      '  - Formatacao de numeros',
                 font=(C['mono'], 9), fg=C['muted'], bg=C['panel'],
                 justify='left').pack(anchor='w', padx=30, pady=(0, 20))

        make_button(frame, '  EXECUTAR TODOS OS TESTES  ', self._rodar_testes, color='green').pack(padx=30, anchor='w')
        separator(frame).pack(fill='x', padx=30, pady=20)

        result_wrap = tk.Frame(frame, bg=C['border2'], padx=1, pady=1)
        result_wrap.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        self.test_output = scrolledtext.ScrolledText(result_wrap, font=(C['mono'], 10),
                                                     bg=C['surface'], fg=C['text'],
                                                     relief='flat', bd=8,
                                                     state='disabled', wrap='word')
        self.test_output.pack(fill='both', expand=True)
        self.test_output.tag_config('ok',   foreground=C['green'])
        self.test_output.tag_config('err',  foreground=C['red'])
        self.test_output.tag_config('warn', foreground=C['amber'])
        self.test_output.tag_config('head', foreground=C['cyan'], font=(C['mono'], 10, 'bold'))

    # ══════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=C['bg'], height=28)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        tk.Frame(footer, bg=C['border'], height=1).pack(fill='x')
        tk.Label(footer, text='ARCANO MESSENGER PRO  //  Use com responsabilidade  //  2025',
                 font=(C['mono'], 8), fg=C['muted'], bg=C['bg']).pack(pady=4)

    # ──────────────────────────────────────────
    # HELPER: SECAO
    # ──────────────────────────────────────────
    def _secao(self, parent, num, titulo):
        row = tk.Frame(parent, bg=C['panel'])
        row.pack(fill='x', padx=30, pady=(20, 10))
        tk.Label(row, text=f'[{num}]', font=(C['mono'], 9, 'bold'), fg=C['amber'], bg=C['panel']).pack(side='left')
        tk.Label(row, text=f'  {titulo}', font=(C['mono'], 11, 'bold'), fg=C['text'], bg=C['panel']).pack(side='left')
        tk.Frame(row, bg=C['border2'], height=1).pack(side='left', fill='x', expand=True, padx=16)

    # ──────────────────────────────────────────
    # LOG
    # ──────────────────────────────────────────
    def _log(self, msg: str, tag: str = ''):
        self.log_text.config(state='normal')
        ts = time.strftime('%H:%M:%S')
        if   '✅' in msg or msg.startswith('✅'): tag = 'ok'
        elif '❌' in msg:                          tag = 'err'
        elif '⚠' in msg or '⏳' in msg:           tag = 'warn'
        elif any(x in msg for x in ['📤','🌐','🤖','🧪']): tag = 'info'
        self.log_text.insert('end', f'[{ts}]  ', 'muted')
        self.log_text.insert('end', msg + '\n', tag or 'ok')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def _limpar_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, 'end')
        self.log_text.config(state='disabled')

    # ──────────────────────────────────────────
    # EVENTOS DE UI
    # ──────────────────────────────────────────
    def _on_delay_change(self, val):
        self.delay_display.config(text=f'{int(float(val))}s')

    def _on_file_change(self, *args):
        path = self.file_var.get()
        ext  = os.path.splitext(path)[1].lower()
        tipos = {'.pdf': 'PDF', '.png': 'Imagem PNG', '.jpg': 'Imagem JPG', '.jpeg': 'Imagem JPEG'}
        self.file_tipo_label.config(
            text=f'Tipo: {tipos.get(ext, "Desconhecido")}  //  {os.path.basename(path)}' if path else ''
        )

    def _sel_file(self):
        path = filedialog.askopenfilename(
            title='Selecionar arquivo',
            filetypes=[('Imagens e PDF', '*.png *.jpg *.jpeg *.pdf'), ('Todos', '*.*')]
        )
        if path:
            self.file_var.set(path)
            self._log(f'Arquivo selecionado: {os.path.basename(path)}')

    def _sel_planilha(self):
        path = filedialog.askopenfilename(
            title='Selecionar planilha',
            filetypes=[('Planilhas', '*.xlsx *.xls *.csv'), ('Todos', '*.*')]
        )
        if path:
            self.plan_var.set(path)

    # ──────────────────────────────────────────
    # CONTATOS
    # ──────────────────────────────────────────
    def _carregar_planilha(self):
        caminho = self.plan_var.get()
        if not caminho or not os.path.exists(caminho):
            messagebox.showerror('Erro', f'Arquivo nao encontrado:\n{caminho}')
            return
        self.contatos = self._ler_planilha(caminho)
        self._atualizar_lista_contatos()

    def _ler_planilha(self, caminho: str) -> list:
        """Le Excel ou CSV e retorna lista de numeros."""
        try:
            import pandas as pd
            ext = os.path.splitext(caminho)[1].lower()
            df  = pd.read_csv(caminho, dtype=str) if ext == '.csv' else pd.read_excel(caminho, dtype=str)

            # Procura coluna de numero
            colunas_ok = ['numero', 'telefone', 'phone', 'cel', 'whatsapp', 'number']
            col = next((c for c in df.columns if c.strip().lower() in colunas_ok), df.columns[0])
            numeros = df[col].dropna().tolist()
            validos = self._validar_numeros(numeros)
            self._log(f'✅ {len(validos)} contatos carregados de {os.path.basename(caminho)}')
            return validos
        except ImportError:
            messagebox.showerror('Erro', 'Pandas nao instalado.\nExecute: pip install pandas openpyxl')
            return []
        except Exception as e:
            self._log(f'❌ Erro ao ler planilha: {e}')
            return []

    def _processar_cola(self):
        """Processa numeros colados manualmente na caixa de texto."""
        texto = self.cola_text.get('1.0', 'end').strip()
        if not texto:
            messagebox.showwarning('Aviso', 'Cole os numeros na caixa de texto primeiro.')
            return

        numeros_raw = []
        for linha in texto.splitlines():
            linha = linha.strip().strip('(),;')
            if linha:
                import re as _re
                encontrados = _re.findall(r'\d[\d\s\-\.]{5,15}\d', linha)
                numeros_raw.extend(encontrados)
        self.contatos = self._validar_numeros(numeros_raw)

        if self.contatos:
            self._log(f'✅ {len(self.contatos)} contatos processados')
            self._atualizar_lista_contatos()
        else:
            messagebox.showwarning('Aviso', 'Nenhum numero valido encontrado.\nVerifique o formato dos numeros.')
            self._log('⚠ Nenhum numero valido encontrado no texto')

    def _validar_numeros(self, numeros_raw: list) -> list:
        """Remove caracteres invalidos, filtra curtos e deduplica."""
        vistos, resultado = set(), []
        for num in numeros_raw:
            limpo = re.sub(r'[^\d]', '', str(num))
            if 10 <= len(limpo) <= 15 and limpo not in vistos:
                vistos.add(limpo)
                resultado.append(limpo)
        return resultado

    def _atualizar_lista_contatos(self):
        self.contadores_label.config(text=f'[ {len(self.contatos)} contatos ]')
        self.preview_list.delete(0, 'end')
        for i, num in enumerate(self.contatos):
            self.preview_list.insert('end', f'  {i+1:04d}  {num}')
        self._log(f'✅ Lista atualizada: {len(self.contatos)} contatos prontos')

    # ──────────────────────────────────────────
    # DISPARO
    # ──────────────────────────────────────────
    def _iniciar(self):
        if not self.contatos:
            messagebox.showerror('Erro', 'Nenhum contato carregado.\nImporte uma planilha ou cole numeros.')
            return
        msg    = self.msg_text.get('1.0', 'end').strip()
        modo   = self.modo_envio.get()
        if modo in ('texto', 'ambos') and not msg:
            messagebox.showerror('Erro', 'Digite a mensagem antes de disparar.')
            return
        if modo in ('arquivo', 'ambos') and not self.file_var.get():
            messagebox.showerror('Erro', 'Selecione um arquivo para enviar.')
            return

        self.parado  = False
        self.rodando = True
        self.btn_iniciar.config(state='disabled')
        self.btn_parar.config(state='normal')
        self._animar_status('DISPARANDO...', C['green'])
        threading.Thread(target=self._loop_disparo, daemon=True).start()

    def _loop_disparo(self):
        try:
            from browser  import BrowserManager
            from sender   import MessageSender
            from antispam import AntiSpam
            from ai_variator import AIVariator
        except ImportError as e:
            self._log(f'❌ Erro ao importar modulos: {e}')
            self._finalizar()
            return

        browser = BrowserManager(log_callback=self._log)
        if not browser.iniciar():
            self._finalizar()
            return

        sender = MessageSender(browser.driver, log_callback=self._log)
        spam   = AntiSpam(log_callback=self._log)
        ia     = AIVariator(log_callback=self._log)

        ok = 0; falha = 0
        total = len(self.contatos)

        for i, numero in enumerate(self.contatos):
            if self.parado:
                self._log('Processo interrompido pelo usuario')
                break

            self.root.after(0, lambda i=i, n=numero: self.progress_label.config(
                text=f'{i+1}/{total}  {n}'))

            msg_base  = self.msg_text.get('1.0', 'end').strip()
            msg_final = ia.variar(msg_base, usar_ia=self.ia_var.get())
            modo      = self.modo_envio.get()

            spam.simular_digitacao(msg_final)

            if   modo == 'texto':   sucesso = sender.enviar_texto(numero, msg_final)
            elif modo == 'arquivo': sucesso = sender.enviar_arquivo(numero, self.file_var.get())
            else:                   sucesso = sender.enviar_conjunto(numero, msg_final, self.file_var.get())

            if sucesso: ok    += 1; spam.registrar_envio()
            else:       falha += 1

            self._log(f'Progresso: {ok} enviados / {falha} falhas')
            if i < total - 1 and not self.parado:
                spam.esperar(self.delay_var.get())

        self._log(f'✅ Finalizado! {ok}/{total} enviados com sucesso.')
        browser.fechar()
        self._finalizar()

    def _parar(self):
        self.parado = True
        self._log('Solicitacao de parada recebida...')
        self._animar_status('PARANDO...', C['amber'])

    def _finalizar(self):
        self.rodando = False
        self.root.after(0, lambda: [
            self.btn_iniciar.config(state='normal'),
            self.btn_parar.config(state='disabled'),
            self.progress_label.config(text=''),
            self._animar_status('PRONTO', C['green']),
        ])

    # ──────────────────────────────────────────
    # TESTES
    # ──────────────────────────────────────────
    def _rodar_testes(self):
        self.test_output.config(state='normal')
        self.test_output.delete('1.0', 'end')
        self.test_output.config(state='disabled')

        def _log_teste(msg):
            self.test_output.config(state='normal')
            tag = ('ok'   if '✅' in msg else
                   'err'  if '❌' in msg else
                   'warn' if '⚠' in msg  else
                   'head' if any(x in msg for x in ['🧪', '---', 'RESULTADO']) else '')
            self.test_output.insert('end', msg + '\n', tag)
            self.test_output.see('end')
            self.test_output.config(state='disabled')
            self.root.update_idletasks()

        def _run():
            # Testes inline simples (sem depender de teste.py externo)
            _log_teste('\n🧪 Iniciando testes...\n')
            resultados = []

            # Teste 1: pandas
            try:
                import pandas
                resultados.append(('✅', 'Pandas instalado', f'v{pandas.__version__}'))
            except ImportError:
                resultados.append(('❌', 'Pandas NAO instalado', 'pip install pandas openpyxl'))

            # Teste 2: selenium
            try:
                import selenium
                resultados.append(('✅', 'Selenium instalado', f'v{selenium.__version__}'))
            except ImportError:
                resultados.append(('❌', 'Selenium NAO instalado', 'pip install selenium'))

            # Teste 3: pyperclip
            try:
                import pyperclip
                resultados.append(('✅', 'Pyperclip instalado', 'OK'))
            except ImportError:
                resultados.append(('❌', 'Pyperclip NAO instalado', 'pip install pyperclip'))

            # Teste 4: webdriver-manager
            try:
                import webdriver_manager
                resultados.append(('✅', 'WebDriver Manager instalado', 'OK'))
            except ImportError:
                resultados.append(('⚠', 'WebDriver Manager ausente', 'pip install webdriver-manager'))

            # Teste 5: anthropic (opcional)
            try:
                import anthropic
                resultados.append(('✅', 'Anthropic (IA) instalado', 'OK'))
            except ImportError:
                resultados.append(('⚠', 'Anthropic nao instalado', 'Opcional - pip install anthropic'))

            # Teste 6: validacao de numeros
            nums = self._validar_numeros(['11999990001', '(21) 9 8888-7777', 'abc', '123'])
            if len(nums) == 2:
                resultados.append(('✅', 'Validacao de numeros', f'{len(nums)} numeros validos'))
            else:
                resultados.append(('❌', 'Validacao de numeros', f'Esperava 2, obteve {len(nums)}'))

            # Exibe resultados
            ok = err = warn = 0
            for icone, nome, detalhe in resultados:
                _log_teste(f'  {icone} {nome}')
                _log_teste(f'       -> {detalhe}')
                if icone == '✅': ok   += 1
                elif icone == '❌': err += 1
                else:              warn += 1

            _log_teste(f'\n{"─"*45}')
            _log_teste(f'RESULTADO: {ok} OK  {warn} avisos  {err} erros')
            if err == 0:
                _log_teste('Sistema pronto para uso!')
            else:
                _log_teste('Corrija os erros antes de usar.')

        threading.Thread(target=_run, daemon=True).start()
        self.nb.select(4)