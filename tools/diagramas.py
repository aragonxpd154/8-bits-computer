#!/usr/bin/env python3
"""Gera o diagrama de blocos do Computador 8 Bits (SVG/PNG/PDF) - Marcos Silva dos Santos."""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'docs', 'imagens')

AZUL, VERDE, LARANJA, CINZA, ROXO = '#2b6cb0', '#2f855a', '#c05621', '#4a5568', '#6b46c1'


def bloco(ax, x, y, w, h, titulo, sub, cor):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.15', fc=cor + '22', ec=cor, lw=2))
    ax.text(x + w / 2, y + h * 0.62, titulo, ha='center', va='center', fontsize=11, weight='bold', color='#1a202c')
    ax.text(x + w / 2, y + h * 0.28, sub, ha='center', va='center', fontsize=7.5, color='#2d3748')


def seta(ax, x1, y1, x2, y2, cor, txt='', dupla=False, off=(0, 0.12), ls='-'):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='<|-|>' if dupla else '-|>', mutation_scale=12, lw=1.8,
                        color=cor, linestyle=ls)
    ax.add_patch(a)
    if txt:
        ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], txt, ha='center', va='bottom', fontsize=7, color=cor)


def main():
    fig, ax = plt.subplots(figsize=(13, 10.4))
    ax.set_xlim(0, 13); ax.set_ylim(0, 10.4); ax.axis('off')
    # barramento
    ax.add_patch(FancyBboxPatch((5.9, 0.9), 1.2, 7.4, boxstyle='round,pad=0.02', fc='#fefcbf', ec='#b7791f', lw=2))
    ax.text(6.5, 4.6, 'BARRAMENTO\nD0 ... D7\n(backplane)', ha='center', va='center', fontsize=10, weight='bold',
            color='#744210', rotation=90)
    W, H = 3.3, 1.05
    esq = [('CLOCK', 'NE556 astavel/monoestavel\nCLK, ~CLK, HLT', CINZA, 7.6, None),
           ('PC', 'Contador de programa\n74LS161 + 74LS245', AZUL, 6.35, 'dupla'),
           ('RAM + MAR', '2x 74S189 (16 x 8)\nMAR 74LS173, chaves DIP', AZUL, 5.1, 'dupla'),
           ('IR', 'Registrador de instrucao\n2x 74LS173 + 74LS245', AZUL, 3.85, 'dupla'),
           ('CONTROLE', '3x EEPROM 28C16 (microcodigo)\n18 sinais de controle', ROXO, 2.35, None),
           ('PASSOS (FETCH)', 'T0..T4: 74LS161 + 74LS138', ROXO, 0.95, None)]
    dir_ = [('REGISTRADOR A', 'Acumulador\n2x 74LS173 + 74LS245', VERDE, 6.35, 'dupla'),
            ('ULA', 'Soma/Sub, AND, OR, XOR, NOT\n74LS283, 86, 08, 32, 153', VERDE, 5.1, 'sai'),
            ('REGISTRADOR B', '2x 74LS173', VERDE, 3.85, 'entra'),
            ('SAIDA (OUT)', '2x 74LS173', LARANJA, 2.6, 'entra'),
            ('DISPLAY', 'EEPROM 28C16 + 4 digitos\n0..255 / -128..127', LARANJA, 1.2, None)]
    for t, s, c, y, _ in esq:
        bloco(ax, 1.6, y, W, H, t, s, c)
    for t, s, c, y, _ in dir_:
        bloco(ax, 8.1, y, W, H, t, s, c)
    bloco(ax, 1.6, 8.85, 3.3, 0.75, 'RESET', 'RST, ~RST, ~STEPCLR', '#c53030')
    bloco(ax, 8.1, 7.75, 3.3, 1.0, 'ALIMENTACAO 5 V', 'jack + PTC + LED (backplane)', '#c53030')
    # ligacoes ao barramento
    for t, s, c, y, k in esq:
        if k:
            seta(ax, 4.9, y + H / 2, 5.9, y + H / 2, c, '', dupla=True)
    for t, s, c, y, k in dir_:
        if k == 'dupla':
            seta(ax, 7.1, y + H / 2, 8.1, y + H / 2, c, '', dupla=True)
        elif k == 'sai':
            seta(ax, 8.1, y + H / 2, 7.1, y + H / 2, c)
        elif k == 'entra':
            seta(ax, 7.1, y + H / 2, 8.1, y + H / 2, c)
    # ligacoes diretas
    seta(ax, 11.4, 6.6, 11.4, 6.15, VERDE, '')
    ax.text(11.55, 6.3, 'A0..A7', fontsize=7, color=VERDE)
    seta(ax, 11.4, 3.85 + H, 11.4, 5.1, VERDE, '')
    ax.text(11.55, 4.95, 'B0..B7', fontsize=7, color=VERDE)
    seta(ax, 9.75, 2.6, 9.75, 1.2 + H, LARANJA, '')
    ax.text(9.85, 2.35, 'O0..O7', fontsize=7, color=LARANJA)
    seta(ax, 1.4, 3.85 + 0.3, 1.4, 2.35 + H - 0.2, ROXO, '')
    ax.text(0.2, 3.6, 'OPCODE\nOP3..OP0', fontsize=7, color=ROXO)
    seta(ax, 1.4, 0.95 + H - 0.2, 1.4, 2.35 + 0.2, ROXO, '')
    ax.text(0.35, 1.9, 'T0..T2', fontsize=7, color=ROXO)
    ax.text(3.25, 0.35, 'Sinais de controle (pelo backplane): HLT PCI ~JMP ~PCO ~MAI RMI ~RMO ~IRI ~IRO ~ACO ~ACI SUB AL1 AL0 ~ALUO NOT ~BRI ~ORI',
            fontsize=8, color=ROXO)
    ax.text(6.5, 10.15, 'Computador 8 Bits v3.0 - Diagrama de blocos', ha='center', fontsize=15, weight='bold')
    ax.text(6.5, 9.82, 'Autor: Marcos Silva dos Santos (MarcosObel) - GPL-3.0', ha='center', fontsize=9, color='#4a5568')
    os.makedirs(OUT, exist_ok=True)
    for ext in ('svg', 'png', 'pdf'):
        fig.savefig(os.path.join(OUT, f'diagrama-blocos.{ext}'), dpi=130, bbox_inches='tight')
    print('ok')


if __name__ == '__main__':
    main()
