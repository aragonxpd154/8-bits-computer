#!/usr/bin/env python3
"""Diagrama de funcionamento (fluxo de sinais) de cada placa -> docs/imagens/placas-funcionamento/<placa>.png/.svg

Cada diagrama mostra os blocos da placa (CIs agrupados por funcao) e por onde os sinais entram e saem.
Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, 'docs', 'imagens', 'placas-funcionamento')
AZ, VE, LA, RO, CI, VM, AM = '#2b6cb0', '#2f855a', '#c05621', '#6b46c1', '#4a5568', '#c53030', '#b7791f'
BUS, CTL, PWR = '#c05621', '#6b46c1', '#c53030'
AUTOR = 'Computador 8 Bits v3.0 - Marcos Silva dos Santos (MarcosObel) - GPL-3.0'


class D:
    def __init__(self, w, h, titulo):
        self.w, self.h = w, h
        self.f, self.ax = plt.subplots(figsize=(w, h))
        ax = self.ax
        self.f.set_size_inches(w, h + 0.7)
        ax.set_xlim(0, w); ax.set_ylim(0, h + 0.7); ax.axis('off')
        ax.text(0.3, h + 0.55, titulo, ha='left', va='top', fontsize=15, weight='bold', color='#1a202c')
        ax.text(w - 0.3, 0.12, AUTOR, ha='right', va='bottom', fontsize=7, color='#718096')
        self.b = {}

    def bloco(self, k, x, y, w, h, t, s='', cor=AZ, fs=11):
        self.b[k] = (x, y, w, h)
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.1',
                                         fc=cor + '1f', ec=cor, lw=2, zorder=2))
        if s:
            self.ax.text(x + w / 2, y + h - 0.28, t, ha='center', va='top', fontsize=fs, weight='bold', color='#1a202c', zorder=3)
            self.ax.text(x + w / 2, y + (h - 0.55) / 2, s, ha='center', va='center', fontsize=8.5, color='#2d3748',
                         zorder=3, linespacing=1.35)
        else:
            self.ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, weight='bold', color='#1a202c', zorder=3)

    def p(self, k, lado, f=0.5):
        x, y, w, h = self.b[k]
        return {'l': (x, y + h * f), 'r': (x + w, y + h * f), 't': (x + w * f, y + h), 'b': (x + w * f, y)}[lado]

    def seta(self, a, b, txt='', cor=CI, lw=2, pos=0.5, dx=0, dy=0.17, ha='center', fs=8.5, dupla=False):
        self.ax.add_patch(FancyArrowPatch(a, b, arrowstyle='<|-|>' if dupla else '-|>', mutation_scale=13, lw=lw,
                                          color=cor, zorder=1, shrinkA=0, shrinkB=0))
        if txt:
            mx, my = a[0] + (b[0] - a[0]) * pos + dx, a[1] + (b[1] - a[1]) * pos + dy
            self.ax.text(mx, my, txt, ha=ha, va='bottom', fontsize=fs, color=cor, weight='bold', zorder=4,
                         family='DejaVu Sans Mono', bbox=dict(fc='white', ec='none', pad=0.6, alpha=0.85))

    def ext(self, x, y, txt, cor=CI, ha='center', fs=9.5):
        """rotulo de um sinal que vem de/vai para outra placa"""
        self.ax.text(x, y, txt, ha=ha, va='center', fontsize=fs, color=cor, weight='bold', family='DejaVu Sans Mono',
                     bbox=dict(fc='white', ec=cor, boxstyle='round,pad=0.3', lw=1.2), zorder=5)

    def nota(self, x, y, txt, ha='left', fs=8.5):
        self.ax.text(x, y, txt, ha=ha, va='top', fontsize=fs, color='#4a5568', style='italic', linespacing=1.4)

    def salvar(self, nome):
        os.makedirs(OUT, exist_ok=True)
        for e in ('png', 'svg'):
            self.f.savefig(os.path.join(OUT, f'{nome}.{e}'), dpi=120, bbox_inches='tight')
        plt.close(self.f)


def legenda(d, y=0.45):
    x = 0.4
    for t, c in (('barramento / dados', BUS), ('controle (vem do microcódigo)', CTL), ('clock / reset', VE),
                 ('sinais internos', CI)):
        d.ax.plot([x, x + 0.45], [y, y], color=c, lw=3)
        d.ax.text(x + 0.55, y, t, va='center', fontsize=8, color='#4a5568')
        x += 0.75 + len(t) * 0.085


# ----------------------------------------------------------------------------------------------
def backplane():
    d = D(15, 7.6, 'Backplane — energia, barramento e sinais de controle')
    d.ext(1.1, 6.1, 'Fonte 5 V', PWR)
    d.bloco('sw', 2.4, 5.6, 1.7, 1.0, 'SW1', 'liga/desliga', CI)
    d.bloco('f', 4.6, 5.6, 1.9, 1.0, 'F1 PTC 3 A', 'abre em curto', PWR)
    d.bloco('d', 7.0, 5.6, 2.3, 1.0, 'D1 + C1', 'inversão / reserva', PWR)
    d.bloco('p', 10.0, 5.6, 4.6, 1.0, '+5 V / GND → 12 módulos', 'conectores P_* (+5V +5V GND GND)', PWR, 10)
    d.seta((1.75, 6.1), d.p('sw', 'l'), cor=PWR)
    d.seta(d.p('sw', 'r'), d.p('f', 'l'), cor=PWR)
    d.seta(d.p('f', 'r'), d.p('d', 'l'), cor=PWR)
    d.seta(d.p('d', 'r'), d.p('p', 'l'), '+5V', cor=PWR)
    d.bloco('bus', 3.2, 3.2, 8.6, 1.3, 'Barramento D0…D7', '8 LEDs vermelhos mostram o valor   ·   BL_* = D0…D3   BH_* = D4…D7', BUS, 12)
    mods = ['PC', 'RAM', 'IR', 'A', 'B', 'ULA', 'SAÍDA']
    for i, m in enumerate(mods):
        x = 3.6 + i * 1.25
        d.ext(x, 2.15, m, BUS, fs=8.5)
        d.seta((x, 2.42), (x, 3.2), cor=BUS, dupla=True, lw=1.6)
    d.bloco('cd', 0.4, 0.9, 3.4, 1.0, 'Decodificador', 'CD_A … CD_E (18 sinais)', CTL, 10.5)
    d.bloco('ct', 9.6, 0.9, 5.0, 1.0, 'C_* de cada módulo', 'mesma ordem de pinos do módulo', CTL, 10.5)
    d.seta(d.p('cd', 'r'), d.p('ct', 'l'), '/MAI /RMO RMI /IRI /PCO /JMP PCI HLT …', cor=CTL, pos=0.5)
    d.ext(13.2, 4.0, 'CLK RST /RST', VE)
    d.nota(12.2, 3.55, 'do Clock e do Reset\npara todos os módulos')
    d.salvar('backplane-barramento')


def clock():
    d = D(15, 7.2, 'Clock — de onde vem o CLK')
    d.bloco('ast', 2.4, 4.4, 3.0, 1.6, 'NE556 metade A', 'ASTÁVEL\nRV1 + C1 → 0,7…140 Hz', VE)
    d.bloco('mono', 2.4, 1.6, 3.0, 1.6, 'NE556 metade B', 'MONOESTÁVEL\n1 pulso de 0,12 s', VE)
    d.ext(1.0, 5.2, 'RV1\nvelocidade', CI)
    d.ext(1.0, 2.4, 'SW1\nPASSO', CI)
    d.seta((1.6, 5.2), d.p('ast', 'l'), cor=CI)
    d.seta((1.55, 2.4), d.p('mono', 'l'), cor=CI)
    d.bloco('mux', 7.0, 2.8, 2.6, 2.2, '74LS00', 'multiplexador\nMODE=1 → automático\nMODE=0 → manual', AZ)
    d.seta(d.p('ast', 'r'), d.p('mux', 'l', 0.75), cor=VE)
    d.seta(d.p('mono', 'r'), d.p('mux', 'l', 0.25), cor=VE)
    d.ext(8.3, 6.35, 'SW2 AUTO/MANUAL', CI)
    d.seta((8.3, 6.05), d.p('mux', 't'), 'MODE (74LS04)', cor=CI, dx=0.15, ha='left')
    d.bloco('hlt', 10.4, 2.8, 1.9, 2.2, 'NAND', 'bloqueia\nquando\nHLT = 1', VM)
    d.seta(d.p('mux', 'r'), d.p('hlt', 'l'), cor=VE)
    d.ext(11.35, 6.35, 'HLT', CTL)
    d.seta((11.35, 6.05), d.p('hlt', 't'), cor=CTL)
    d.bloco('inv', 13.0, 2.8, 1.6, 2.2, '74LS04', 'gera CLK\ne /CLK', AZ)
    d.seta(d.p('hlt', 'r'), d.p('inv', 'l'), cor=VE)
    d.ext(13.8, 1.6, 'CLK  /CLK → backplane', VE)
    d.seta(d.p('inv', 'b'), (13.8, 1.9), cor=VE)
    d.nota(7.0, 1.9, 'O LED azul pisca no ritmo do CLK.\nNo HLT o clock para e o computador congela.')
    d.salvar('clock-astavel-monoestavel')


def reset():
    d = D(14, 6.6, 'Reset — RST, /RST e /STCLR')
    d.bloco('btn', 0.5, 3.6, 2.6, 1.6, 'SW1 + R1 + C1', 'botão (pull-up)\n+ reset ao ligar', CI, 10)
    d.bloco('g1', 4.2, 3.7, 2.0, 1.4, 'NAND 1', 'inverte', AZ)
    d.seta(d.p('btn', 'r'), d.p('g1', 'l'), '/BTN', cor=CI)
    d.bloco('g2', 7.6, 3.7, 2.0, 1.4, 'NAND 2', 'inverte', AZ)
    d.seta(d.p('g1', 'r'), d.p('g2', 'l'), 'RST', cor=VE)
    d.ext(5.2, 6.0, 'RST → backplane', VE)
    d.seta(d.p('g1', 't'), (5.2, 5.75), cor=VE)
    d.ext(10.9, 6.0, '/RST → backplane (LED1)', VE)
    d.seta(d.p('g2', 'r', 0.8), (10.9, 5.75), cor=VE)
    d.bloco('and', 9.0, 1.1, 2.6, 1.6, 'NAND 3 + 4', '= AND\n/RST · /Y5', AZ)
    d.seta(d.p('g2', 'b'), d.p('and', 't', 0.3), '/RST', cor=VE, dx=-0.1, ha='right')
    d.ext(6.2, 1.9, '/Y5 (passo 5)', CTL)
    d.seta((7.35, 1.9), d.p('and', 'l'), cor=CTL)
    d.ext(13.0, 1.9, '/STCLR', VE)
    d.seta(d.p('and', 'r'), (12.35, 1.9), cor=VE)
    d.nota(0.5, 2.8, 'Ao ligar, C1 descarregado segura /BTN em 0\npor ≈ 0,1 s: o computador começa zerado.\n'
                     '/STCLR zera o Contador de Passos no fim\nde cada instrução ou durante o reset.')
    d.salvar('reset-circuito')


def pc():
    d = D(14, 6.6, 'Contador de Programa — endereço da próxima instrução')
    d.ext(1.2, 4.3, 'D0…D3', BUS)
    d.bloco('cnt', 3.0, 3.2, 3.2, 2.2, '74LS161', 'contador de 4 bits\nPCI=1 → +1\n/JMP=0 → carrega', AZ)
    d.seta((1.85, 4.3), d.p('cnt', 'l'), cor=BUS)
    d.ext(4.6, 6.15, 'CLK  PCI  /JMP  /RST', CTL)
    d.seta((4.6, 5.85), d.p('cnt', 't'), cor=CTL)
    d.bloco('buf', 8.4, 3.2, 2.6, 2.2, '74LS245', 'porta para o\nbarramento', AZ)
    d.seta(d.p('cnt', 'r'), d.p('buf', 'l'), 'P0…P3', cor=CI)
    d.ext(9.7, 6.15, '/PCO', CTL)
    d.seta((9.7, 5.85), d.p('buf', 't'), cor=CTL)
    d.ext(12.7, 4.3, 'D0…D7', BUS)
    d.seta(d.p('buf', 'r'), (12.05, 4.3), cor=BUS)
    d.bloco('led', 3.4, 1.0, 2.4, 1.1, '4 LEDs', 'endereço atual', VE, 10)
    d.seta(d.p('cnt', 'b'), d.p('led', 't'), cor=CI)
    d.nota(8.0, 2.6, 'D4…D7 saem em 0 (entradas no GND).\nCom /PCO = 1 o 245 fica desligado\n(alta impedância).')
    d.salvar('pc-contador-programa')


def ram():
    d = D(16, 9.0, 'RAM e MAR — modo PROG (chaves) e modo RUN (computador)')
    d.ext(1.0, 7.3, 'D0…D3', BUS)
    d.bloco('mar', 2.4, 6.6, 2.4, 1.4, 'MAR 74LS173', '/MAI + CLK', AZ, 10)
    d.seta((1.6, 7.3), d.p('mar', 'l'), cor=BUS)
    d.bloco('sa', 2.4, 4.6, 2.4, 1.2, 'SW1 DIP', 'endereço', CI, 10)
    d.bloco('ma', 6.0, 5.6, 2.4, 1.8, 'U7 74LS157', 'escolhe o\nendereço', AZ, 10)
    d.seta(d.p('mar', 'r'), d.p('ma', 'l', 0.75), 'RUN', cor=CI, fs=7.5)
    d.seta(d.p('sa', 'r'), d.p('ma', 'l', 0.25), 'PROG', cor=CI, fs=7.5)
    d.bloco('mem', 9.6, 4.0, 2.6, 3.4, 'RAM\n2× 74S189', '16 × 8 bits\n\nsaída invertida', RO, 11)
    d.seta(d.p('ma', 'r'), d.p('mem', 'l', 0.8), 'RA0…3', cor=CI)
    d.ext(1.0, 3.2, 'D0…D7', BUS)
    d.bloco('sd', 2.4, 1.3, 2.4, 1.2, 'SW3 DIP', 'dado', CI, 10)
    d.bloco('md', 6.0, 2.2, 2.4, 1.8, 'U8 U9 74LS157', 'escolhe o\ndado', AZ, 10)
    d.seta((1.6, 3.2), d.p('md', 'l', 0.75), 'RUN', cor=BUS, fs=7.5)
    d.seta(d.p('sd', 'r'), d.p('md', 'l', 0.25), 'PROG', cor=CI, fs=7.5)
    d.seta(d.p('md', 'r'), d.p('mem', 'l', 0.3), 'WD0…7', cor=CI)
    d.bloco('we', 6.0, 0.4, 2.4, 1.3, 'U10 + U11', 'pulso de escrita\nGRAVAR ou RMI·CLK', VM, 9.5)
    d.seta(d.p('we', 'r'), d.p('mem', 'b', 0.5), '/WE', cor=VM)
    d.ext(3.6, 0.75, 'CLK RMI GRAVAR', CTL, fs=8.5)
    d.seta((4.9, 0.75), d.p('we', 'l', 0.27), cor=CTL)
    d.bloco('inv', 13.0, 5.0, 2.4, 1.4, '74LS04 ×2', 'desinverte', AZ, 10)
    d.seta(d.p('mem', 'r', 0.75), d.p('inv', 'l'), cor=CI)
    d.bloco('buf', 13.0, 2.6, 2.4, 1.4, '74LS245', '/RMO', AZ, 10)
    d.seta(d.p('inv', 'b'), d.p('buf', 't'), 'Q0…7', cor=CI, dx=0.1, ha='left')
    d.ext(14.2, 1.4, 'D0…D7', BUS)
    d.seta(d.p('buf', 'b'), (14.2, 1.7), cor=BUS)
    d.ext(14.2, 7.6, 'LEDs Q7…Q0', VE)
    d.seta(d.p('inv', 't'), (14.2, 7.3), cor=CI)
    d.bloco('run', 9.6, 7.7, 2.6, 0.9, '555 PROG/RUN', '', VE, 10)
    d.ext(7.2, 8.15, 'SW2', CI)
    d.seta((7.6, 8.15), d.p('run', 'l'), cor=CI)
    d.nota(10.2, 1.25, 'RUN (do 555) vai para a seleção\nde todos os 74LS157.')
    d.salvar('ram-mar-memoria')


def registrador(nome, titulo, sinal_in, sinal_out, saida_dir, saida_txt, com_245=True, nota='', ir=False):
    d = D(14, 6.8, titulo)
    d.ext(1.1, 4.3, 'D0…D7', BUS)
    d.bloco('reg', 2.8, 3.0, 3.2, 2.6, '2× 74LS173', f'registrador 8 bits\ncarrega com {sinal_in}\nna subida do CLK', AZ)
    d.seta((1.75, 4.3), d.p('reg', 'l'), cor=BUS)
    d.ext(4.4, 6.35, f'CLK  {sinal_in}  RST', CTL)
    d.seta((4.4, 6.05), d.p('reg', 't'), cor=CTL)
    d.bloco('led', 3.2, 0.9, 2.4, 1.1, '8 LEDs', 'valor guardado', VE, 10)
    d.seta(d.p('reg', 'b'), d.p('led', 't'), cor=CI)
    if com_245:
        d.bloco('buf', 8.0, 3.0, 2.6, 1.6, '74LS245', 'operando (D0…D3)' if ir else 'porta do barramento', AZ, 10)
        d.seta(d.p('reg', 'r', 0.3), d.p('buf', 'l', 0.5), 'bits 3…0' if ir else '', cor=CI)
        d.ext(9.3, 5.6, sinal_out, CTL)
        d.seta((9.3, 5.3), d.p('buf', 't'), cor=CTL)
        d.ext(12.6, 3.8, 'D0…D7', BUS)
        d.seta(d.p('buf', 'r'), (11.95, 3.8), cor=BUS)
    d.ext(12.0, 1.4, saida_txt, saida_dir)
    d.seta(d.p('reg', 'r', 0.15) if not com_245 else (6.0, 3.25), (10.0, 1.4), 'bits 7…4' if ir else '', cor=CI, pos=0.6)
    if nota:
        d.nota(6.6, 6.4, nota)
    d.salvar(nome)


def cd():
    d = D(16, 8.0, 'Decodificador de Controle — microcódigo em 3 EEPROMs')
    d.ext(1.3, 6.2, 'OPCODE\n(do IR)', CTL)
    d.ext(1.3, 4.2, 'PASSO T0…T2\n(Contador de Passos)', VE)
    d.ext(1.3, 2.2, 'FLAGS CF ZF\n(pull-down)', CI)
    d.bloco('adr', 3.8, 1.4, 2.6, 5.6, 'Endereço', 'A0…A2 = passo\n\nA3…A6 = opcode\n\nA7 = CF\nA8 = ZF\n\nA9, A10 = 0', CI, 11)
    for y in (6.2, 4.2, 2.2):
        d.seta((2.6, y), (3.8, y), cor=CI)
    cores = (RO, LA, AZ)
    eps = [('EEPROM2 (U1)', '/IRI /RMO RMI /MAI\n/PCO /JMP PCI HLT'),
           ('EEPROM1 (U2)', 'NOT /ALUO AL0 AL1\nSUB /ACI /ACO /IRO'),
           ('EEPROM0 (U3)', '/BRI /ORI\nE0_4 E0_5 (livres)')]
    for i, (t, s) in enumerate(eps):
        y = 5.4 - i * 2.0
        d.bloco(f'e{i}', 8.0, y, 3.0, 1.5, t, '28C16 · 2 KB', cores[i], 10.5)
        d.seta((6.4, 4.2), d.p(f'e{i}', 'l'), cor=CI, lw=1.4)
        d.seta(d.p(f'e{i}', 'r'), (12.2, y + 0.75), cor=CTL)
        d.ax.text(12.35, y + 0.75, s, va='center', fontsize=9, family='DejaVu Sans Mono', color=CTL, weight='bold')
    d.nota(8.0, 1.2, 'Busca (todas as instruções):  T0 = PCO + MAI     T1 = RMO + IRI + PCI\n'
                     'Exemplo ADD:  T2 = IRO + MAI   T3 = RMO + BRI   T4 = ALUO + ACI')
    d.salvar('cd-decodificador-controle')


def cw():
    d = D(16, 7.6, 'Palavra de Controle — repete os sinais e mostra cada um num LED')
    d.bloco('cd', 0.4, 2.6, 2.6, 2.4, 'Decodificador', 'CTRL_A … CTRL_E\n(20 sinais)', CTL, 10.5)
    d.bloco('buf', 4.6, 2.2, 3.6, 3.2, '3× 74HCT541', 'buffer octal\nNÃO inverte\n/OE no GND', AZ, 11)
    d.seta(d.p('cd', 'r'), d.p('buf', 'l'), 'J2…J6', cor=CTL)
    d.bloco('bp', 12.8, 2.6, 2.8, 2.4, 'Backplane', 'CD_A … CD_E\n→ todos os módulos', CTL, 10.5)
    d.seta(d.p('buf', 'r'), d.p('bp', 'l'), 'J7…J11 (mesma pinagem)', cor=CTL, pos=0.5)
    d.bloco('la', 9.0, 5.4, 3.4, 1.4, '11 LEDs (sinais /X)', '+5V → 1 kΩ → LED → saída', VE, 9.5)
    d.bloco('lh', 9.0, 0.5, 3.4, 1.4, '7 LEDs (sinais X)', 'saída → LED → 1 kΩ → GND', VE, 9.5)
    d.seta((9.6, 3.8), d.p('la', 'b', 0.2), cor=CI, lw=1.4)
    d.seta((9.6, 3.8), d.p('lh', 't', 0.2), cor=CI, lw=1.4)
    d.ext(2.0, 6.6, 'P_CD (5 V) → J1', PWR)
    d.ext(2.0, 1.2, 'J12 → J1 do Decodificador', PWR)
    d.nota(4.4, 1.9, 'LED aceso = sinal ATIVO\n(0 V nos sinais com barra, 5 V nos outros)')
    d.salvar('cw-palavra-de-controle')


def fetch():
    d = D(14, 6.6, 'Contador de Passos — T0…T4')
    d.ext(1.2, 4.2, '/CLK', VE)
    d.bloco('cnt', 2.6, 3.1, 3.0, 2.2, '74LS161', 'conta na descida\ndo CLK', AZ)
    d.seta((1.75, 4.2), d.p('cnt', 'l'), cor=VE)
    d.ext(4.1, 6.15, '/STCLR (Reset)', VE)
    d.seta((4.1, 5.85), d.p('cnt', 't'), cor=VE)
    d.bloco('dec', 7.6, 3.1, 2.8, 2.2, '74LS138', 'decodificador\n3 → 8', AZ)
    d.seta(d.p('cnt', 'r'), d.p('dec', 'l'), 'T0 T1 T2', cor=CI)
    d.ext(12.4, 5.0, 'LEDs T0…T4 (/S0…/S4)', VE)
    d.seta(d.p('dec', 'r', 0.75), (10.85, 5.0), cor=CI)
    d.ext(12.4, 3.4, '/Y5 → Reset', CTL)
    d.seta(d.p('dec', 'r', 0.15), (11.45, 3.4), cor=CTL)
    d.ext(4.6, 1.2, 'T0 T1 T2 → Decodificador (cabo direto)', VE)
    d.seta(d.p('cnt', 'b'), (4.1, 1.48), cor=VE)
    d.nota(9.0, 2.4, 'No passo 5 o /Y5 vai a 0, o Reset gera\n/STCLR e o contador volta a T0.')
    d.salvar('fetch-contador-passos')


def alu():
    d = D(16, 8.6, 'ULA — todas as operações ao mesmo tempo, o seletor escolhe uma')
    d.ext(1.0, 6.4, 'A0…A7\n(Reg. A)', BUS)
    d.ext(1.0, 2.4, 'B0…B7\n(Reg. B)', BUS)
    ops = [('som', 'Soma / Subtração', '2× 74LS283 + 2× 74LS86\nA + B   ou   A + NOT B + 1', VE),
           ('and', 'AND', '2× 74LS08', AZ), ('or', 'OR', '2× 74LS32', AZ),
           ('xor', 'XOR / NOT', '74LS32 + 74LS86 (×2)\nA XOR (B OR NOT)', RO)]
    for i, (k, t, s, c) in enumerate(ops):
        y = 6.3 - i * 1.75
        d.bloco(k, 3.6, y, 4.0, 1.45, t, s, c, 10.5)
        d.seta((1.75, 6.4), d.p(k, 'l', 0.65), cor=BUS, lw=1.2)
        d.seta((1.75, 2.4), d.p(k, 'l', 0.35), cor=BUS, lw=1.2)
    d.ext(9.3, 8.1, 'SUB', CTL)
    d.seta((9.0, 8.1), d.p('som', 't', 0.8), cor=CTL)
    d.ext(9.0, 0.55, 'NOT', CTL)
    d.seta((8.7, 0.55), d.p('xor', 'b', 0.8), cor=CTL)
    d.bloco('sel', 9.4, 1.8, 2.4, 5.6, '4× 74LS153', 'seletor\n\nAL1 AL0\n00 soma/sub\n01 AND\n10 OR\n11 XOR/NOT', LA, 10.5)
    for k in ('som', 'and', 'or', 'xor'):
        d.seta(d.p(k, 'r'), (9.4, d.p(k, 'r')[1]), cor=CI, lw=1.5)
    d.ext(10.6, 8.1, 'AL1 AL0', CTL)
    d.seta((10.6, 7.8), d.p('sel', 't'), cor=CTL)
    d.bloco('buf', 12.8, 3.8, 2.4, 1.6, '74LS245', '/ALUO', AZ, 10.5)
    d.seta(d.p('sel', 'r', 0.55), d.p('buf', 'l'), 'R0…7', cor=CI)
    d.ext(14.0, 2.4, 'D0…D7', BUS)
    d.seta(d.p('buf', 'b'), (14.0, 2.7), cor=BUS)
    d.ext(14.0, 6.6, 'LEDs = resultado', VE)
    d.seta(d.p('buf', 't'), (14.0, 6.3), cor=CI, lw=1.2)
    d.ext(5.6, 8.1, 'CARRY → flags (futuro)', CI, fs=8.5)
    d.seta(d.p('som', 't', 0.3), (5.6, 7.85), cor=CI, lw=1.2)
    d.salvar('alu-unidade-logica-aritmetica')


def display():
    d = D(16, 7.6, 'Display Decimal — tabela na EEPROM + varredura dos 4 dígitos')
    d.ext(1.2, 5.6, 'O0…O7\n(Reg. Saída)', BUS)
    d.bloco('rom', 3.4, 3.6, 3.2, 3.0, 'EEPROM 28C16', 'A0…A7 = valor\nA8 A9 = dígito\nA10 = com sinal\n\nsaída = segmentos', RO, 11)
    d.seta((2.15, 5.6), d.p('rom', 'l', 0.67), cor=BUS)
    d.ext(1.2, 3.9, 'SW1\nCOM/SEM sinal', CI)
    d.seta((2.15, 3.9), d.p('rom', 'l', 0.1), cor=CI)
    d.bloco('res', 7.8, 4.4, 2.0, 1.4, '8× 100 Ω', 'segmentos', CI, 10)
    d.seta(d.p('rom', 'r', 0.6), d.p('res', 'l'), 'a…g, dp', cor=CI)
    d.bloco('ds', 11.0, 3.8, 3.6, 2.6, 'Display 4 dígitos', 'catodo comum\n0…255 ou −128…127', VE, 11)
    d.seta(d.p('res', 'r'), d.p('ds', 'l', 0.6), cor=CI)
    d.bloco('osc', 3.4, 0.7, 2.4, 1.6, 'NE555', '≈ 480 Hz', VE, 10)
    d.bloco('cnt', 6.6, 0.7, 2.4, 1.6, '74LS161', 'conta 0…3', AZ, 10)
    d.bloco('dec', 9.8, 0.7, 2.4, 1.6, '74LS139', 'liga 1 dígito', AZ, 10)
    d.seta(d.p('osc', 'r'), d.p('cnt', 'l'), cor=VE)
    d.seta(d.p('cnt', 'r'), d.p('dec', 'l'), 'DG0 DG1', cor=CI)
    d.seta(d.p('cnt', 't', 0.3), d.p('rom', 'b', 0.85), 'DG0 DG1', cor=CI, dx=0.1, ha='left')
    d.seta(d.p('dec', 'r'), d.p('ds', 'b', 0.5), '/DIG1…4', cor=CI, pos=0.35)
    d.nota(0.3, 2.9, 'Cada dígito acende ≈ 120×/s:\no olho vê os 4 juntos.')
    d.salvar('display-decimal')


def main():
    backplane(); clock(); reset(); pc(); ram(); cd(); cw(); fetch(); alu(); display()
    registrador('acc-registrador-a', 'Registrador A (acumulador)', '/ACI', '/ACO', BUS, 'A0…A7 → ULA (cabo direto)')
    registrador('b-registrador-b', 'Registrador B', '/BRI', '/BRO (fixo em +5 V)', BUS, 'B0…B7 → ULA (cabo direto)',
                nota='O registrador B nunca escreve no barramento:\no backplane mantém /BRO desligado.')
    registrador('ir-registrador-instrucao', 'Registrador de Instrução', '/IRI', '/IRO', CTL,
                'OPCODE → Decodificador (cabo direto)', ir=True,
                nota='Bits 7…4 = opcode (qual instrução)\nBits 3…0 = operando (endereço ou número)')
    registrador('out-registrador-saida', 'Registrador de Saída', '/ORI', '', BUS, 'O0…O7 → Display (cabo direto)',
                com_245=False, nota='Só lê o barramento (não tem 74LS245).')
    print('diagramas ->', OUT)


if __name__ == '__main__':
    main()
