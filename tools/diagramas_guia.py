#!/usr/bin/env python3
"""Diagramas do Guia Visual passo a passo - Computador 8 Bits v3.0 (Marcos Silva dos Santos)."""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon, Wedge

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'docs', 'imagens', 'guia')
os.makedirs(OUT, exist_ok=True)
AZ, VE, LA, RO, CI, VM, AM = '#2b6cb0', '#2f855a', '#c05621', '#6b46c1', '#4a5568', '#c53030', '#b7791f'
AUTOR = 'Computador 8 Bits v3.0 - Marcos Silva dos Santos (MarcosObel) - GPL-3.0'


def fig(w, h, titulo):
    f, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    ax.text(w / 2, h - 0.35, titulo, ha='center', va='top', fontsize=15, weight='bold', color='#1a202c')
    ax.text(w / 2, 0.15, AUTOR, ha='center', va='bottom', fontsize=7, color='#718096')
    return f, ax


def caixa(ax, x, y, w, h, t, s='', cor=AZ, fs=10, sfs=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=cor + '22', ec=cor, lw=2))
    if s:
        ax.text(x + w / 2, y + h * 0.66, t, ha='center', va='center', fontsize=fs, weight='bold', color='#1a202c')
        ax.text(x + w / 2, y + h * 0.3, s, ha='center', va='center', fontsize=sfs, color='#2d3748')
    else:
        ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, weight='bold', color='#1a202c')


def seta(ax, a, b, cor='#4a5568', lw=2, estilo='-|>', ls='-'):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=14, lw=lw, color=cor, linestyle=ls))


def num(ax, x, y, n, cor=AZ):
    ax.add_patch(Circle((x, y), 0.28, fc=cor, ec='white', lw=2, zorder=5))
    ax.text(x, y, str(n), ha='center', va='center', color='white', fontsize=11, weight='bold', zorder=6)


def salvar(f, nome):
    for ext in ('png', 'svg'):
        f.savefig(os.path.join(OUT, f'{nome}.{ext}'), dpi=130, bbox_inches='tight')
    plt.close(f)


# 1. Roteiro geral --------------------------------------------------------------
def roteiro():
    f, ax = fig(14, 6.2, 'Roteiro do projeto - do arquivo ao computador funcionando')
    etapas = [('Entender', 'arquitetura e\nsinais (doc 1)', CI), ('Fabricar', 'Gerbers no\nJLCPCB (doc 3)', AZ),
              ('Comprar', 'componentes\n(lista de materiais)', AM), ('Gravar', '4 EEPROMs\n28C16 (doc 6)', RO),
              ('Montar', 'soldar e testar\ncada placa (doc 4)', VE), ('Interligar', 'base + backplane\n58 cabos (doc 5)', LA),
              ('Ligar', 'subida por etapas\n(doc 8)', VM), ('Programar', 'RAM pelas chaves\nRUN! (doc 7)', AZ)]
    for i, (t, s, c) in enumerate(etapas):
        row, col = divmod(i, 4)
        x = 0.6 + col * 3.35
        y = 3.2 - row * 2.35
        caixa(ax, x, y, 2.7, 1.55, t, s, c, 13, 9)
        num(ax, x + 0.05, y + 1.55, i + 1, c)
        if col < 3:
            seta(ax, (x + 2.72, y + 0.78), (x + 3.33, y + 0.78))
    seta(ax, (0.6 + 3 * 3.35 + 1.35, 3.18), (0.6 + 1.35, 2.42), CI, 1.6, ls='--')
    ax.text(7, 0.55, 'Fabricar, comprar e gravar podem andar em paralelo enquanto as placas chegam da China.',
            ha='center', fontsize=9, style='italic', color='#4a5568')
    salvar(f, '01-roteiro')


# 2. Pedido das placas ---------------------------------------------------------------
def pedido():
    f, ax = fig(14, 4.8, 'Como pedir as placas (JLCPCB / PCBWay)')
    p = [('hardware/fabricacao/\n<placa>/', '<placa>-gerber.zip'), ('jlcpcb.com', 'Order now >\nAdd gerber file'),
         ('Opcoes', 'FR-4 | 2 camadas | 1,6 mm\nHASL | 1 oz | 5 pecas'), ('Carrinho', 'repita p/ as 14 placas\n1 pedido = 1 frete'),
         ('Chegada', 'inspecao visual +\ncontinuidade +5V x GND')]
    for i, (t, s) in enumerate(p):
        x = 0.4 + i * 2.75
        caixa(ax, x, 1.4, 2.3, 2.0, t, s, AZ, 11, 8.5)
        num(ax, x + 0.05, 3.4, i + 1)
        if i < 4:
            seta(ax, (x + 2.32, 2.4), (x + 2.73, 2.4))
    ax.text(7, 0.75, 'Nao precisa de montagem (PCB Assembly desligado). Placas grandes: Backplane ~205x150 mm, ULA ~220x130 mm.',
            ha='center', fontsize=9, color='#4a5568')
    salvar(f, '02-pedido-das-placas')


# 3. Polaridade -------------------------------------------------------------------
def polaridade():
    f, ax = fig(14, 7, 'Polaridade e orientacao - confira ANTES de soldar')
    # CI
    x0, y0 = 0.7, 3.6
    ax.add_patch(Rectangle((x0, y0), 3.0, 1.3, fc='#2d3748', ec='black'))
    ax.add_patch(Wedge((x0, y0 + 0.65), 0.22, -90, 90, fc='white'))
    for i in range(8):
        ax.add_patch(Rectangle((x0 + 0.2 + i * 0.35, y0 - 0.3), 0.14, 0.3, fc='#a0aec0'))
        ax.add_patch(Rectangle((x0 + 0.2 + i * 0.35, y0 + 1.3), 0.14, 0.3, fc='#a0aec0'))
    ax.add_patch(Circle((x0 + 0.35, y0 + 0.3), 0.08, fc='white'))
    ax.text(x0 + 0.27, y0 - 0.55, '1', ha='center', fontsize=10, weight='bold', color=VM)
    ax.text(x0 + 1.5, y0 + 0.65, '74LS173', color='white', ha='center', va='center', fontsize=10)
    ax.text(x0 + 1.5, y0 - 1.05, 'CI / soquete: chanfro (meia-lua) a esquerda,\npino 1 embaixo a esquerda = PAD QUADRADO',
            ha='center', fontsize=8.5)
    # LED
    x, y = 5.3, 3.4
    ax.add_patch(Wedge((x + 0.5, y + 1.6), 0.5, 0, 180, fc='#68d391', ec='#2f855a'))
    ax.add_patch(Rectangle((x, y + 1.1), 1.0, 0.5, fc='#68d391', ec='#2f855a'))
    ax.plot([x + 0.97, x + 0.97], [y + 1.1, y + 1.6], color='#22543d', lw=3)
    ax.plot([x + 0.25, x + 0.25], [y + 1.1, y - 0.2], color='#a0aec0', lw=3)
    ax.plot([x + 0.75, x + 0.75], [y + 1.1, y + 0.3], color='#a0aec0', lw=3)
    ax.text(x + 0.25, y - 0.45, 'A (+)\nperna longa', ha='center', fontsize=8)
    ax.text(x + 0.95, y + 0.05, 'K (-)\nlado chato', ha='left', fontsize=8)
    ax.text(x + 0.5, y - 1.25, 'LED: catodo (K) no\nPAD QUADRADO', ha='center', fontsize=8.5)
    # eletrolitico
    x, y = 8.2, 3.2
    ax.add_patch(Rectangle((x, y + 0.5), 1.0, 1.7, fc='#2b6cb0', ec='black'))
    ax.add_patch(Rectangle((x + 0.72, y + 0.5), 0.28, 1.7, fc='#e2e8f0', ec='black'))
    for k in range(3):
        ax.text(x + 0.86, y + 0.8 + k * 0.5, '-', ha='center', va='center', fontsize=12, weight='bold')
    ax.plot([x + 0.25, x + 0.25], [y + 0.5, y - 0.3], color='#a0aec0', lw=3)
    ax.plot([x + 0.75, x + 0.75], [y + 0.5, y + 0.1], color='#a0aec0', lw=3)
    ax.text(x + 0.25, y - 0.6, '+', ha='center', fontsize=12, weight='bold', color=VM)
    ax.text(x + 0.5, y - 1.55, 'Eletrolitico: faixa = (-)\n+ no PAD QUADRADO\nTantalo: marca = (+)', ha='center', fontsize=8.5)
    # diodo / sip / header
    x, y = 11.0, 4.6
    ax.add_patch(Rectangle((x, y), 1.6, 0.45, fc='#1a202c'))
    ax.add_patch(Rectangle((x + 1.25, y), 0.2, 0.45, fc='#e2e8f0'))
    ax.plot([x - 0.4, x], [y + 0.22] * 2, color='#a0aec0', lw=3); ax.plot([x + 1.6, x + 2.0], [y + 0.22] * 2, color='#a0aec0', lw=3)
    ax.text(x + 0.8, y - 0.35, 'Diodo: faixa = catodo (pad quadrado)', ha='center', fontsize=8.5)
    ax.add_patch(Rectangle((x - 0.2, y - 1.7), 2.2, 0.5, fc='#f6e05e', ec='black'))
    ax.add_patch(Circle((x - 0.05, y - 1.45), 0.07, fc='black'))
    ax.text(x + 0.9, y - 1.95, 'Rede resistiva SIP: ponto = pino 1 (comum)', ha='center', fontsize=8.5)
    ax.add_patch(Rectangle((x + 0.1, y - 3.2), 1.6, 0.4, fc='#1a202c'))
    for k in range(4):
        ax.add_patch(Rectangle((x + 0.25 + k * 0.4, y - 3.1), 0.12, 0.2, fc='#ecc94b'))
    ax.text(x + 0.31, y - 2.65, '1', ha='center', fontsize=10, weight='bold', color=VM)
    ax.text(x + 0.9, y - 3.55, 'Barra de pinos: pino 1 = pad quadrado (esquerda)', ha='center', fontsize=8.5)
    ax.text(7, 0.55, 'Regra que vale para TODAS as placas: o PAD QUADRADO marca pino 1 / catodo / positivo do eletrolitico.',
            ha='center', fontsize=10, weight='bold', color=VM)
    salvar(f, '03-polaridade')


# 4. Ordem de soldagem ---------------------------------------------------------------
def soldagem():
    f, ax = fig(14, 5.2, 'Ordem de soldagem - do componente mais baixo para o mais alto')
    p = [('Resistores', 'e redes SIP', AM), ('Soquetes', 'de CI (chanfro!)', CI), ('Capacitores', '100 nF ceramicos', AZ),
         ('LEDs', 'mesma altura', VE), ('Eletroliticos', 'polaridade!', LA), ('Barras', 'de pinos', RO),
         ('Chaves', 'botoes, pot., display', AZ), ('Teste 5 V', 'sem CIs', VM), ('CIs', 'nos soquetes', CI)]
    for i, (t, s, c) in enumerate(p):
        x = 0.35 + i * 1.5
        h = 0.6 + i * 0.27
        ax.add_patch(Rectangle((x, 1.0), 1.25, h, fc=c + '55', ec=c, lw=2))
        num(ax, x + 0.62, 1.0 + h + 0.4, i + 1, c)
        ax.text(x + 0.62, 1.0 + h / 2 + 0.12, t, ha='center', va='center', fontsize=8.5, weight='bold')
        ax.text(x + 0.62, 1.0 + h / 2 - 0.22, s, ha='center', va='center', fontsize=7)
    ax.text(7, 0.55, 'Soldar sempre pela face de baixo (com o texto 8BITS ... em cobre). Furo metalizado liga as duas faces.',
            ha='center', fontsize=9, color='#4a5568')
    salvar(f, '04-ordem-de-soldagem')


# 5. Teste de alimentacao ---------------------------------------------------------------
def teste_5v():
    f, ax = fig(14, 5.3, 'Teste de alimentacao de cada placa (antes de colocar os CIs)')
    # conector
    x, y = 0.8, 2.2
    ax.add_patch(Rectangle((x, y), 2.4, 0.6, fc='#1a202c'))
    labs = ['+5V', '+5V', 'GND', 'GND']
    for k in range(4):
        ax.add_patch(Rectangle((x + 0.18 + k * 0.6, y + 0.15), 0.25, 0.3, fc='#ecc94b'))
        ax.text(x + 0.3 + k * 0.6, y - 0.3, labs[k], ha='center', fontsize=8.5, weight='bold', color=VM if k < 2 else '#1a202c')
        ax.text(x + 0.3 + k * 0.6, y + 0.85, str(k + 1), ha='center', fontsize=9)
    ax.text(x + 1.2, y + 1.35, 'J1 ALIMENTACAO (todas as placas)', ha='center', fontsize=10, weight='bold')
    seta(ax, (3.4, 2.5), (4.4, 2.5))
    tab = [('DIP-8 (555)', '8', '1'), ('DIP-14 (74LS00/04/08/32/86/132, 556)', '14', '7'),
           ('DIP-16 (74LS138/139/153/157/161/173/283, 74S189)', '16', '8'), ('DIP-20 (74LS245)', '20', '10'),
           ('DIP-24 (28C16)', '24', '12')]
    ax.text(4.6, 3.9, 'Meca 5 V entre os pinos de cada soquete:', fontsize=10, weight='bold')
    ax.text(10.6, 3.9, 'VCC', fontsize=10, weight='bold', color=VM); ax.text(11.6, 3.9, 'GND', fontsize=10, weight='bold')
    for i, (a, b, c) in enumerate(tab):
        yy = 3.4 - i * 0.5
        ax.text(4.6, yy, a, fontsize=9); ax.text(10.75, yy, b, fontsize=9, color=VM); ax.text(11.75, yy, c, fontsize=9)
    ax.text(7, 0.6, 'Depois insira os CIs com a placa desligada. Ligue com fonte limitada (~500 mA). CI esquentando = CI invertido.',
            ha='center', fontsize=9, color=VM)
    salvar(f, '05-teste-de-alimentacao')


# 6. Arranjo na base e cabos ---------------------------------------------------------------
def base():
    f, ax = fig(14, 9, 'Arranjo dos modulos na base e cabos (todos de 4 vias, RETOS: pino 1 com pino 1)')
    ax.add_patch(Rectangle((0.4, 0.6), 13.2, 7.7, fc='#f7fafc', ec='#a0aec0', lw=1.5, ls='--'))
    ax.text(0.6, 8.05, 'BASE ~60 x 45 cm (MDF/acrilico) - espacadores M3', fontsize=8, color='#718096')
    esq = [('RESET', VM), ('CLOCK', CI), ('PC', AZ), ('RAM/MAR', AZ), ('IR', AZ), ('CONTROLE', RO), ('PALAVRA CTRL*', RO), ('PASSOS', RO)]
    dir_ = [('REG. A', VE), ('ULA', VE), ('REG. B', VE), ('SAIDA', LA), ('DISPLAY', LA)]
    pe, pd = {}, {}
    for i, (t, c) in enumerate(esq):
        y = 7.3 - i * 0.84
        caixa(ax, 0.8, y, 2.6, 0.66, t, '', c, 10); pe[t] = y
    for i, (t, c) in enumerate(dir_):
        y = 6.25 - i * 1.15
        caixa(ax, 10.6, y, 2.6, 0.85, t, '', c, 10); pd[t] = y
    ax.add_patch(FancyBboxPatch((5.2, 1.3), 3.6, 6.4, boxstyle='round,pad=0.02', fc='#fefcbf', ec=AM, lw=2.5))
    ax.text(7.0, 7.3, 'BACKPLANE', ha='center', fontsize=12, weight='bold', color='#744210')
    ax.text(7.0, 6.95, 'conectores agrupados por modulo\n+ barramento D0..D7 (LEDs)', ha='center', fontsize=8, color='#744210')
    caixa(ax, 10.6, 7.3, 2.6, 0.6, 'FONTE 5 V / 2-3 A', '', VM, 9)
    seta(ax, (10.6, 7.6), (8.8, 7.4), VM, 2)
    for t, y in pe.items():
        if t == 'CONTROLE':
            continue   # o Decodificador liga na Palavra de Controle (direto) e ela no backplane
        seta(ax, (3.4, y + 0.33), (5.2, y + 0.33), '#718096', 1.6, '<|-|>')
    seta(ax, (3.55, pe['CONTROLE'] + 0.33), (3.55, pe['PALAVRA CTRL*'] + 0.33), RO, 2.5)
    for t, y in pd.items():
        seta(ax, (10.6, y + 0.42), (8.8, y + 0.42), '#718096', 1.6, '<|-|>')
    # diretos
    seta(ax, (0.7, pe['IR'] + 0.2), (0.7, pe['CONTROLE'] + 0.5), RO, 2.5)
    ax.text(0.45, pe['IR'] - 0.25, 'opcode', fontsize=7.5, color=RO, rotation=90)
    seta(ax, (0.7, pe['PASSOS'] + 0.55), (0.7, pe['CONTROLE'] + 0.2), RO, 2.5)
    ax.text(0.45, pe['PASSOS'] + 0.4, 'T0-T2', fontsize=7.5, color=RO, rotation=90)
    seta(ax, (13.35, pd['REG. A'] + 0.3), (13.35, pd['ULA'] + 0.6), VE, 2.5)
    seta(ax, (13.35, pd['REG. B'] + 0.6), (13.35, pd['ULA'] + 0.25), VE, 2.5)
    seta(ax, (13.35, pd['SAIDA'] + 0.25), (13.35, pd['DISPLAY'] + 0.6), LA, 2.5)
    ax.text(5.2, 1.0, 'Cinza = cabo modulo <-> backplane (44)   |   Colorido = cabo DIRETO entre placas vizinhas (14)',
            fontsize=9, color='#2d3748')
    ax.text(5.2, 0.72, '* Palavra de Controle (18 LEDs) e opcional: sem ela o CONTROLE liga direto no backplane (52 cabos).',
            fontsize=8, color='#4a5568')
    salvar(f, '06-base-e-cabos')


# 7. Cabo reto ---------------------------------------------------------------
def cabo():
    f, ax = fig(12, 4.2, 'Cabo de 4 vias RETO - todos os 58 cabos sao assim')
    cores = ['#e53e3e', '#dd6b20', '#d69e2e', '#38a169']
    for side, x in (('MODULO  J2 CONTROLE', 1.2), ('BACKPLANE  C_ACC', 8.8)):
        ax.add_patch(Rectangle((x, 1.2), 2.0, 2.0, fc='#1a202c'))
        ax.text(x + 1.0, 3.45, side, ha='center', fontsize=9.5, weight='bold')
        for k, n in enumerate(['CLK', '/ACI', 'RST', '/ACO']):
            ax.add_patch(Rectangle((x + 0.8, 2.85 - k * 0.48), 0.35, 0.25, fc='#ecc94b'))
            ax.text(x + 0.2 if x < 5 else x + 1.3, 2.9 - k * 0.48, f'{k+1} {n}', color='white', fontsize=8)
    for k in range(4):
        y = 2.97 - k * 0.48
        ax.plot([3.2, 8.8], [y, y], color=cores[k], lw=4)
    ax.text(6.0, 0.7, 'Escolha uma cor para o pino 1 e use sempre a mesma: fica impossivel ligar invertido.',
            ha='center', fontsize=9.5)
    salvar(f, '07-cabo-reto')


# 8. EEPROMs ---------------------------------------------------------------
def eeproms():
    f, ax = fig(14, 5.6, 'Gravacao das EEPROMs - qual arquivo vai em qual chip')
    ax.add_patch(Rectangle((0.6, 1.2), 8.6, 3.2, fc='#c6f6d5', ec=VE, lw=2))
    ax.text(4.9, 4.1, 'Placa DECODIFICADOR DE CONTROLE', ha='center', fontsize=11, weight='bold')
    for i, (u, b, d) in enumerate([('U1', 'EEPROM2.bin', 'HLT PCI JMP PCO\nMAI RMI RMO IRI'),
                                   ('U2', 'EEPROM1.bin', 'IRO ACO ACI SUB\nAL1 AL0 ALU NOT'),
                                   ('U3', 'EEPROM0.bin', 'BRI ORI\n(+6 livres)')]):
        x = 1.0 + i * 2.75
        ax.add_patch(Rectangle((x, 2.0), 2.3, 1.1, fc='#1a202c'))
        ax.text(x + 1.15, 2.75, u, color='white', ha='center', fontsize=12, weight='bold')
        ax.text(x + 1.15, 2.35, b, color='#fbd38d', ha='center', fontsize=9)
        ax.text(x + 1.15, 1.55, d, ha='center', fontsize=7.5)
    ax.add_patch(Rectangle((10.0, 1.2), 3.4, 3.2, fc='#feebc8', ec=LA, lw=2))
    ax.text(11.7, 4.1, 'Placa DISPLAY', ha='center', fontsize=11, weight='bold')
    ax.add_patch(Rectangle((10.55, 2.0), 2.3, 1.1, fc='#1a202c'))
    ax.text(11.7, 2.75, 'U1', color='white', ha='center', fontsize=12, weight='bold')
    ax.text(11.7, 2.35, 'DISPLAY.bin', color='#fbd38d', ha='center', fontsize=9)
    ax.text(7, 0.65, 'minipro -p "AT28C16" -w firmware/microcodigo/EEPROM2.bin      (etiquete cada chip com fita!)',
            ha='center', fontsize=10, family='monospace', color=RO)
    salvar(f, '08-eeproms')


# 9. Ciclo de instrucao (ADD) ---------------------------------------------------------------
def ciclo():
    f, ax = fig(14, 7.2, 'Ciclo de uma instrucao: ADD 15 (A <- A + RAM[15])')
    passos = ['T0', 'T1', 'T2', 'T3', 'T4']
    x0, w = 2.6, 2.1
    # clock
    y = 5.7
    ax.text(0.3, y + 0.25, 'CLK', fontsize=10, weight='bold')
    xs, ys = [x0], [y]
    for i in range(5):
        a = x0 + i * w
        xs += [a, a + w / 2, a + w / 2, a + w]; ys += [y + 0.5, y + 0.5, y, y]
    ax.plot(xs[1:], ys[1:], color='#1a202c', lw=2)
    for i, t in enumerate(passos):
        a = x0 + i * w
        ax.add_patch(Rectangle((a, 4.6), w, 0.6, fc=['#bee3f8', '#bee3f8', '#c6f6d5', '#c6f6d5', '#c6f6d5'][i], ec='white'))
        ax.text(a + w / 2, 4.9, t, ha='center', va='center', fontsize=11, weight='bold')
    ax.text(0.3, 4.85, 'PASSO', fontsize=10, weight='bold')
    ax.text(x0 + w, 5.35, 'BUSCA (igual para todas)', ha='center', fontsize=8, color=AZ)
    ax.text(x0 + 3.5 * w, 5.35, 'EXECUCAO (depende do opcode)', ha='center', fontsize=8, color=VE)
    sinais = [('PCO MAI', 'PC -> MAR'), ('RMO IRI PCI', 'RAM -> IR\nPC + 1'), ('IRO MAI', '15 -> MAR'),
              ('RMO BRI', 'RAM[15] -> B'), ('ALU ACI', 'A + B -> A')]
    for i, (s, d) in enumerate(sinais):
        a = x0 + i * w
        caixa(ax, a + 0.08, 2.4, w - 0.16, 1.9, s, d, [AZ, AZ, VE, VE, VE][i], 10, 8.5)
    ax.text(0.3, 3.3, 'SINAIS\nATIVOS', fontsize=10, weight='bold')
    ax.text(7, 1.6, 'Na subida do CLK os registradores copiam o barramento; na descida o contador de passos avanca.',
            ha='center', fontsize=9.5)
    ax.text(7, 1.15, 'Depois de T4, o sinal /Y5 zera o contador e comeca a proxima instrucao em T0.',
            ha='center', fontsize=9.5)
    salvar(f, '09-ciclo-de-instrucao')


# 10. Programar a RAM ---------------------------------------------------------------
def programar():
    f, ax = fig(14, 6.4, 'Gravando um byte na RAM pelas chaves  (exemplo: endereco 1 = ADD 5 = 0100 0101)')

    def dip(x, y, bits, rot):
        n = len(bits)
        ax.add_patch(Rectangle((x, y), n * 0.55 + 0.2, 1.2, fc='#c53030', ec='black'))
        for i, b in enumerate(bits):
            xx = x + 0.15 + i * 0.55
            ax.add_patch(Rectangle((xx, y + 0.2), 0.35, 0.8, fc='white', ec='black'))
            ax.add_patch(Rectangle((xx + 0.04, y + (0.6 if b else 0.24)), 0.27, 0.36, fc='#1a202c'))
            ax.text(xx + 0.17, y - 0.25, rot[i], ha='center', fontsize=8)
        ax.text(x + n * 0.55 + 0.35, y + 0.95, 'ON = 1', fontsize=8)
    dip(1.0, 3.5, [0, 0, 0, 1], ['A3', 'A2', 'A1', 'A0'])
    ax.text(1.0, 5.0, 'END (DIP 4)  = 0001', fontsize=11, weight='bold')
    dip(5.2, 3.5, [0, 1, 0, 0, 0, 1, 0, 1], ['D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'])
    ax.text(5.2, 5.0, 'DADO (DIP 8) = 0100 0101  (ADD 5)', fontsize=11, weight='bold')
    ax.add_patch(Circle((12.3, 4.1), 0.55, fc='#2d3748', ec='black'))
    ax.add_patch(Circle((12.3, 4.1), 0.35, fc='#e2e8f0'))
    ax.text(12.3, 3.2, 'GRAVAR', ha='center', fontsize=10, weight='bold')
    passos = ['1. Clock em MANUAL', '2. RAM em PROG (LED vermelho)', '3. Ajuste END e DADO', '4. Aperte GRAVAR',
              '5. Repita para cada linha do montador', '6. PROG -> RUN, RESET, clock em AUTO']
    for i, p in enumerate(passos):
        ax.text(1.0 + (i % 3) * 4.3, 1.9 - (i // 3) * 0.55, p, fontsize=10)
    ax.text(7, 0.75, 'A tabela de chaves de cada programa sai pronta do montador: python3 firmware/ferramentas/montador.py programa.asm',
            ha='center', fontsize=9, family='monospace', color=AZ)
    salvar(f, '10-programar-a-ram')


# 11. Subida do sistema ---------------------------------------------------------------
def subida():
    f, ax = fig(14, 5.4, 'Subida do sistema por etapas - ligue um modulo de cada vez')
    p = [('Backplane', 'LED de energia\n5 V nos P_xxx', VM), ('Clock', 'LED pisca\n(HLT ligado)', CI),
         ('Reset +\nPassos', 'T0..T4 andam\ne voltam a T0', RO), ('PC', 'conta com\nPCI = 1', AZ),
         ('RAM/MAR', 'grava e le\nem PROG', AZ), ('IR +\nControle', 'busca T0/T1\nfunciona', RO),
         ('A, B, ULA,\nSaida, Display', 'rode\n01-soma.asm', VE)]
    for i, (t, s, c) in enumerate(p):
        x = 0.3 + i * 1.95
        caixa(ax, x, 1.6, 1.7, 2.3, t, s, c, 9.5, 8)
        num(ax, x + 0.85, 4.2, i + 1, c)
        if i < 6:
            seta(ax, (x + 1.72, 2.75), (x + 1.93, 2.75))
    ax.text(7, 0.85, 'Compare cada passo com o emulador:  python3 firmware/ferramentas/emulador.py programas/01-soma.asm --passos',
            ha='center', fontsize=9, family='monospace', color=AZ)
    salvar(f, '11-subida-do-sistema')


if __name__ == '__main__':
    for fn in (roteiro, pedido, polaridade, soldagem, teste_5v, base, cabo, eeproms, ciclo, programar, subida):
        fn()
    print('ok', OUT)
