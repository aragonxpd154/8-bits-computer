#!/usr/bin/env python3
"""Monta hardware/esquema-eletrico-completo.pdf: capa, indice, diagrama de blocos, cabos e esquematicos.
Autor do projeto: Marcos Silva dos Santos (MarcosObel)."""
import os, sys, io
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, 'gerador-kicad'))
import designs

ORDEM = ['BACKPLANE', 'CLOCK', 'RESET', 'PC', 'RAM', 'IR', 'CD', 'FETCH', 'ACC', 'B', 'ALU', 'OUT', 'DISPLAY']


def capa(boards):
    buf = io.BytesIO()
    W, H = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(W, H))
    c.setTitle('Computador 8 Bits v3.0 - Esquema eletrico completo')
    c.setAuthor('Marcos Silva dos Santos')
    c.setFillColor(colors.HexColor('#1a365d'))
    c.rect(0, H - 60 * mm, W, 60 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 30)
    c.drawString(20 * mm, H - 30 * mm, 'Computador 8 Bits  -  v3.0')
    c.setFont('Helvetica', 16)
    c.drawString(20 * mm, H - 42 * mm, 'Esquema eletrico completo  |  12 modulos + backplane  |  logica TTL 74LS, sem microcontrolador')
    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(20 * mm, H - 75 * mm, 'Autor: Marcos Silva dos Santos (MarcosObel)')
    c.setFont('Helvetica', 11)
    c.drawString(20 * mm, H - 83 * mm, 'Zutup All Electronics  -  github.com/aragonxpd154/8-bits-computer  -  Licenca GPL-3.0')
    c.drawString(20 * mm, H - 90 * mm, 'Revisao 3.0  -  01/11/2026  -  Projeto em KiCad (esquematicos, PCBs, Gerbers e manual em docs/)')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(20 * mm, H - 105 * mm, 'Indice')
    c.setFont('Helvetica', 10)
    y = H - 113 * mm
    itens = [('1', 'Diagrama de blocos'), ('2', 'Tabela de interligacao (52 cabos)')]
    for i, b in enumerate(boards):
        itens.append((str(3 + i), f'{b.title}  ({b.folder})'))
    for n, t in itens:
        c.drawString(25 * mm, y, f'Folha {n:>2}   {t}')
        y -= 5.6 * mm
    c.setFont('Helvetica-Oblique', 8)
    c.drawString(20 * mm, 12 * mm, 'Nomes de sinal com barra (/X ou ~{X}) sao ativos em nivel baixo. Conexoes por rotulos de rede: '
                 'pinos com o mesmo nome de rede estao ligados.')
    c.showPage()
    c.save()
    return buf.getvalue()


def tabela_cabos():
    bs = {b.key: b for b in designs.all_boards()}
    bp = bs['BACKPLANE']
    linhas = [['#', 'Placa', 'Conector', 'Pino 1', 'Pino 2', 'Pino 3', 'Pino 4', 'Liga em']]
    for i, (placa, j, dest) in enumerate(designs.CABOS, 1):
        cc = bs[placa].comps[j]
        if isinstance(dest, tuple):
            alvo = f'DIRETO: {bs[dest[0]].title} {dest[1]}'
        else:
            alvo = f'Backplane {bp.header_map[dest]} ({dest})'
        linhas.append([str(i), bs[placa].title[:30], f'{j} {cc.value}'] + list(cc.pinlabels) + [alvo])
    buf = io.BytesIO()
    W, H = landscape(A3)
    c = canvas.Canvas(buf, pagesize=(W, H))
    c.setFont('Helvetica-Bold', 16)
    c.drawString(15 * mm, H - 15 * mm, 'Tabela de interligacao - todos os cabos sao de 4 vias e RETOS (pino 1 com pino 1)')
    c.setFont('Helvetica', 9)
    c.drawString(15 * mm, H - 21 * mm, 'Computador 8 Bits v3.0 - Autor: Marcos Silva dos Santos (MarcosObel)')
    t = Table(linhas, colWidths=[9 * mm, 62 * mm, 40 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 120 * mm],
              rowHeights=4.6 * mm)
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, -1), 'Helvetica', 7.5), ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
                           ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cbd5e0')),
                           ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                           ('GRID', (0, 0), (-1, -1), 0.25, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    w, h = t.wrapOn(c, W, H)
    t.drawOn(c, 15 * mm, H - 26 * mm - h)
    c.showPage()
    c.save()
    return buf.getvalue()


def main():
    bs = {b.key: b for b in designs.all_boards()}
    boards = [bs[k] for k in ORDEM]
    w = PdfWriter()
    for data in (capa(boards),):
        for p in PdfReader(io.BytesIO(data)).pages:
            w.add_page(p)
    for p in PdfReader(os.path.join(ROOT, 'docs', 'imagens', 'diagrama-blocos.pdf')).pages:
        w.add_page(p)
    for p in PdfReader(io.BytesIO(tabela_cabos())).pages:
        w.add_page(p)
    for b in boards:
        f = os.path.join(ROOT, 'hardware', 'fabricacao', b.folder, '0-esquematico.pdf')
        for p in PdfReader(f).pages:
            w.add_page(p)
    w.add_metadata({'/Title': 'Computador 8 Bits v3.0 - Esquema eletrico completo',
                    '/Author': 'Marcos Silva dos Santos (MarcosObel)', '/Subject': 'GPL-3.0'})
    out = os.path.join(ROOT, 'hardware', 'esquema-eletrico-completo.pdf')
    with open(out, 'wb') as f:
        w.write(f)
    print(out, len(w.pages), 'paginas')


if __name__ == '__main__':
    main()
