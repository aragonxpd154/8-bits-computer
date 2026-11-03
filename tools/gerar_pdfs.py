#!/usr/bin/env python3
"""Gera os PDFs da documentacao (guia visual e manual completo) a partir dos .md.
Requer: pandoc e playwright (Chromium).  Autor do projeto: Marcos Silva dos Santos."""
import os, subprocess, re
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS = os.path.join(ROOT, 'docs')
OUT = os.path.join(DOCS, 'pdf')

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
html, body { max-width: none !important; margin: 0 !important; padding: 0 !important; }
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 10.5pt; color: #1a202c; line-height: 1.45; }
h1 { color: #1a365d; border-bottom: 3px solid #2b6cb0; padding-bottom: 4px; font-size: 20pt; }
h2 { color: #2b6cb0; border-bottom: 1px solid #cbd5e0; padding-bottom: 3px; margin-top: 18px; page-break-before: always; }
h3, h4 { color: #2c5282; page-break-after: avoid; }
img { max-width: 100%; display: block; margin: 8px auto; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 8.8pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #2b6cb0; color: white; padding: 4px 6px; text-align: left; }
td { border: 1px solid #cbd5e0; padding: 3px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f7fafc; }
code { background: #edf2f7; padding: 1px 4px; border-radius: 3px; font-size: 8.8pt; }
pre { background: #f7fafc; color: #1a202c; border: 1px solid #cbd5e0; padding: 8px 10px; border-radius: 6px; font-size: 8.3pt; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; color: inherit; }
blockquote { border-left: 4px solid #2b6cb0; margin: 6px 0; padding: 4px 10px; background: #ebf8ff; }
hr { border: none; border-top: 1px dashed #cbd5e0; }
.capa { page-break-after: always; text-align: center; padding-top: 30mm; }
.capa h1 { border: none; font-size: 30pt; }
.capa .sub { font-size: 14pt; color: #4a5568; }
.capa .autor { font-size: 15pt; margin-top: 25mm; font-weight: bold; }
.capa img { max-width: 75%; max-height: 105mm; width: auto; margin: 12mm auto 0 auto; }
nav#TOC { page-break-after: always; }
nav#TOC ul { list-style: none; padding-left: 14px; }
nav#TOC > ul > li { margin-top: 4px; font-weight: bold; }
"""


def capa(titulo, sub, imagem):
    return (f'<div class="capa"><h1>{titulo}</h1><div class="sub">{sub}</div>'
            f'<img src="{imagem}"/><div class="autor">Marcos Silva dos Santos (MarcosObel)</div>'
            f'<div class="sub">github.com/aragonxpd154/8-bits-computer · GPL-3.0 · v3.0 · 2026</div></div>')


def md_para_html(arquivos, titulo, capa_html, toc=False, primeiro_h2_sem_quebra=False, base=DOCS, css_extra=''):
    md = '\n\n'.join(open(os.path.join(base, a), encoding='utf-8').read() for a in arquivos)
    # o botao do 3D Viewer (imagem do shields.io) vira um link de texto no PDF
    md = re.sub(r'<a href="([^"]+)"><img alt="Abrir o 3D Viewer"[^>]*></a>',
                lambda m: f'<b>🧊 3D Viewer online: <a href="{m.group(1)}">{m.group(1)}</a></b>', md)
    md = re.sub(r'^← .*$|^.*\[todas as placas\]\(README\.md\).*$|^Voltar para a .*$', '', md, flags=re.M)
    # nos PDFs, cada capitulo (titulo nivel 1) comeca em pagina nova
    md = re.sub(r'^---\s*\nAnterior:.*$', '', md, flags=re.M)
    md = re.sub(r'^(Anterior|Próximo):.*$', '', md, flags=re.M)
    args = ['pandoc', '-f', 'gfm', '-t', 'html5', '--standalone', '--no-highlight', '--metadata', f'title={titulo}']
    if toc:
        args += ['--toc', '--toc-depth=2']
    html = subprocess.run(args, input=md, capture_output=True, text=True, check=True).stdout
    html = re.sub(r'<header id="title-block-header">.*?</header>', '', html, flags=re.S)
    html = html.replace('</head>', f'<style>{CSS}{css_extra}</style></head>', 1)
    html = html.replace('<body>', '<body>' + capa_html, 1)
    html = html.replace('<h1 ', '<h1 style="page-break-before: always" ')
    return html


def para_pdf(html, nome, base=DOCS):
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(base, f'_tmp_{nome}.html')
    open(tmp, 'w', encoding='utf-8').write(html)
    pdf = os.path.join(OUT, nome + '.pdf')
    rodape = ('<div style="font-size:7pt;color:#718096;width:100%;text-align:center;">'
              'Computador 8 Bits v3.0 — Marcos Silva dos Santos — pág. <span class="pageNumber"></span>/'
              '<span class="totalPages"></span></div>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto('file://' + tmp)
        pg.wait_for_load_state('networkidle')
        pg.pdf(path=pdf, format='A4', print_background=True, display_header_footer=True,
               header_template='<div></div>', footer_template=rodape,
               margin={'top': '14mm', 'bottom': '16mm', 'left': '12mm', 'right': '12mm'})
        b.close()
    os.remove(tmp)
    return pdf


if __name__ == '__main__':
    g = md_para_html(['GUIA-VISUAL-PASSO-A-PASSO.md'], 'Guia visual passo a passo',
                     capa('Computador 8 Bits', 'Guia visual passo a passo — do arquivo ao computador funcionando',
                          'imagens/guia/01-roteiro.png'))
    print(para_pdf(g, 'guia-visual-passo-a-passo'))
    caps = ['01-arquitetura.md', '02-revisao-e-correcoes.md', '03-fabricacao-das-placas.md', '04-montagem-das-placas.md',
            '05-interligacao-e-backplane.md', '06-gravacao-das-eeproms.md', '07-programacao-e-uso.md',
            '08-testes-e-diagnostico.md', 'lista-de-materiais-completa.md']
    m = md_para_html(caps, 'Manual completo', capa('Computador 8 Bits', 'Manual completo — arquitetura, fabricação, '
                                                   'montagem, gravação, uso e testes', 'imagens/diagrama-blocos.png'),
                     toc=True)
    print(para_pdf(m, 'manual-completo'))
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from placas_info import PLACAS, PASTAS
    PL = os.path.join(DOCS, 'placas')
    ordem = sorted(PLACAS, key=lambda k: PLACAS[k]['ordem'])
    css_placas = ('h2 { page-break-before: auto !important; } '
                  'table img { max-height: 70mm; width: auto; } '
                  'td[width] img { max-height: 48mm; }')
    gp = md_para_html(['README.md'] + [PASTAS[k] + '.md' for k in ordem], 'Guia das placas',
                      capa('Computador 8 Bits', 'Guia das 13 placas — função, funcionamento, esquema, 3D e conectores',
                           '../imagens/3d/alu-unidade-logica-aritmetica.png'),
                      toc=False, base=PL, css_extra=css_placas)
    print(para_pdf(gp, 'guia-das-placas', base=PL))
