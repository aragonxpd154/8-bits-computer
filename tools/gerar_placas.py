#!/usr/bin/env python3
"""Gera uma pagina detalhada por placa em docs/placas/<placa>.md (+ indice docs/placas/README.md).

Fontes: tools/placas_info.py (explicacoes), tools/gerador-kicad/designs.py (componentes, conectores, cabos),
docs/3d/placas3d.json (medidas, gerado por tools/render3d.py). Tambem rasteriza o esquematico de cada placa
em docs/imagens/esquemas/<placa>.png (precisa do pdftoppm).

Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import re
import sys
import json
import subprocess
from collections import OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, 'gerador-kicad'))
sys.path.insert(0, AQUI)
import designs  # noqa: E402
from placas_info import PLACAS, PASTAS  # noqa: E402
from gerar_visualizador import destinos, nome_sinal  # noqa: E402

SAIDA = os.path.join(RAIZ, 'docs', 'placas')
ESQ = os.path.join(RAIZ, 'docs', 'imagens', 'esquemas')

VIEWER = 'https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html'
BOTAO = '<a href="https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html"><img alt="Abrir o 3D Viewer" src="https://img.shields.io/badge/%E2%96%B6%20Abrir%20o%203D%20Viewer-as%2013%20placas%20em%203D-1d5c34?style=for-the-badge&logo=threedotjs&logoColor=white&labelColor=0f3a20" height="36"></a>'

GRUPOS = OrderedDict([('IC', 'Circuitos integrados'), ('R', 'Resistores'), ('C', 'Capacitores'), ('LED', 'LEDs'),
                      ('SW', 'Chaves e botões'), ('J', 'Conectores'), ('PWRIN', 'Entrada de energia')])


def br(v):
    return f'{v:g}'.replace('.', ',') if isinstance(v, (int, float)) else v


def esquema_png(pasta):
    os.makedirs(ESQ, exist_ok=True)
    pdf = os.path.join(RAIZ, 'hardware', 'fabricacao', pasta, '0-esquematico.pdf')
    png = os.path.join(ESQ, pasta + '.png')
    base = png[:-4]
    subprocess.run(['pdftoppm', '-png', '-singlefile', '-scale-to', '1800', pdf, base], check=True)
    from PIL import Image
    Image.open(png).convert('RGB').save(png, optimize=True)


def bom(b):
    por = OrderedDict((g, OrderedDict()) for g in GRUPOS)
    for c in b.comps.values():
        g = c.group if c.group in GRUPOS else 'IC'
        v = 'Barra de pinos 1×4, 2,54 mm (macho, 90° ou reta)' if c.sym == 'Conn_01x04' else c.value
        por[g].setdefault(v, []).append(c.ref)
    linhas = ['| Tipo | Valor / peça | Qtd. | Referências |', '|---|---|---:|---|']
    for g, vals in por.items():
        for v, refs in vals.items():
            refs = sorted(refs, key=lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0)))
            linhas.append(f'| {GRUPOS[g]} | {v} | {len(refs)} | {", ".join(refs)} |')
    return '\n'.join(linhas)


def tabela(pares, cab=('Item', 'Função')):
    if not pares:
        return ''
    return '\n'.join([f'| {cab[0]} | {cab[1]} |', '|---|---|'] + [f'| **{a}** | {t} |' for a, t in pares])


def conectores_md(b, dest):
    linhas = ['| Conector | Nome | Pino 1 | Pino 2 | Pino 3 | Pino 4 | Liga em |', '|---|---|---|---|---|---|---|']
    for c in sorted([c for c in b.comps.values() if c.ref.startswith('J')],
                    key=lambda c: int(re.sub(r'\D', '', c.ref))):
        n = len(c.pins)
        lab = c.pinlabels or [nome_sinal(c.pins.get(str(i + 1))) for i in range(n)]
        lab = (list(lab) + [''] * 4)[:4]
        if c.sym == 'Barrel_Jack':
            lab = ['+5V (centro)', 'GND', 'GND', '']
        linhas.append(f'| **{c.ref}** | {c.value} | ' + ' | '.join(f'`{x}`' if x else '—' for x in lab)
                      + f' | {dest.get((b.key, c.ref), "—")} |')
    return '\n'.join(linhas)


def vizinhos(b):
    """com quais placas esta se comunica (pelos cabos)"""
    s = []
    for placa, j, d in designs.CABOS:
        if isinstance(d, tuple):
            if placa == b.key:
                s.append(d[0])
            elif d[0] == b.key:
                s.append(placa)
    return sorted(set(s), key=lambda k: PLACAS[k]['ordem'])


def pagina(b, meta, dest, ordem):
    info = PLACAS[b.key]
    p = PASTAS[b.key]
    m = meta.get(p, {})
    i = ordem.index(b.key)
    ant = ordem[i - 1] if i > 0 else None
    prox = ordem[i + 1] if i + 1 < len(ordem) else None
    nci = sum(1 for c in b.comps.values() if c.group == 'IC')
    fab = f'../../hardware/fabricacao/{p}'
    viz = vizinhos(b)
    o = [f'# {info["ordem"]:02d} · {info["nome"]}', '',
         f'> Placa do **Computador 8 Bits v3.0** — projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.', '',
         f'**{info["resumo"]}**', '',
         f'<p align="center"><img alt="{info["nome"]} em 3D" src="../imagens/3d/{p}.png" width="760"></p>', '',
         f'<p align="center">' + BOTAO.replace(VIEWER, VIEWER + '#' + p) + '</p>', '',
         '| | |', '|---|---|',
         f'| Tamanho | **{br(m.get("largura_mm"))} × {br(m.get("altura_mm"))} mm**, 2 camadas, furo metalizado |',
         f'| Componentes | {len(b.comps)} ({nci} {"CI" if nci == 1 else "CIs"}) |',
         f'| Furos / vias | {m.get("furos")} / {m.get("vias")} |',
         f'| Projeto KiCad | [`hardware/kicad/{p}/`](../../hardware/kicad/{p}/) |',
         f'| Para a fábrica | [`{p}-gerber.zip`]({fab}/{p}-gerber.zip) · [lista de materiais (CSV)]({fab}/lista-de-materiais.csv) · [relatório DRC]({fab}/relatorio-drc.txt) |',
         f'| Esquemático | [PDF]({fab}/0-esquematico.pdf) · [imagem](../imagens/esquemas/{p}.png) |',
         f'| Modelo 3D | [**3D Viewer** (abre no navegador)]({VIEWER}#{p}) · [STL (abre em 3D no GitHub)](../3d/stl/{p}.stl) · [GLB](../3d/modelos/{p}.glb) · [STEP (FreeCAD/Fusion)]({fab}/{p}.step) |',
         '', '## Função', '', info['funcao'], '']
    if viz:
        o += [f'Liga-se diretamente (cabo próprio) a: ' + ', '.join(f'[{PLACAS[k]["nome"]}]({PASTAS[k]}.md)' for k in viz)
              + '. Todo o resto passa pelo [backplane](backplane-barramento.md).', '']
    o += ['## Diagrama de funcionamento', '',
          f'![Diagrama de funcionamento — {info["nome"]}](../imagens/placas-funcionamento/{p}.png)', '',
          '<sub>Laranja = barramento/dados · roxo = sinais de controle do microcódigo · verde = clock e reset · '
          'cinza = sinais internos da placa.</sub>', '',
          '## Como funciona', '']
    for t in info['funcionamento']:
        o += [t, '']
    o += ['## O que cada parte faz', '', tabela(info['blocos'], ('Componente', 'Papel no circuito')), '']
    if info['leds']:
        o += ['## O que os LEDs mostram', '', tabela(info['leds'], ('LED', 'Significado')), '']
    if info['controles']:
        o += ['## Chaves e ajustes', '', tabela(info['controles'], ('Controle', 'O que faz')), '']
    o += ['## Esquemático', '',
          f'[![Esquemático — {info["nome"]}](../imagens/esquemas/{p}.png)]({fab}/0-esquematico.pdf)', '',
          '<sub>Clique para abrir o PDF em alta resolução. Sinais com barra (ex.: /RST) são ativos em nível baixo.</sub>', '',
          '## A placa como sai da fábrica', '',
          '| Face de cima (componentes) | Face de baixo (solda) |', '|---|---|',
          f'| ![topo](../3d/texturas/{p}-topo.png) | ![fundo](../3d/texturas/{p}-fundo.png) |', '',
          '<sub>Imagens geradas das camadas reais (cobre, máscara verde, serigrafia branca e furos). '
          'A face de baixo aparece como você a vê com a placa virada.</sub>', '',
          f'<p align="center"><img alt="Placa sem componentes" src="../imagens/3d/{p}-nua.png" width="560"></p>', '',
          '## Conectores', '',
          'Todos os conectores são barras de pinos de 2,54 mm. Os nomes dos sinais estão impressos na serigrafia, '
          'embaixo de cada pino. Cabos de 4 vias **retos** (pino 1 com pino 1).', '',
          conectores_md(b, dest), '',
          '## Lista de componentes', '', bom(b), '',
          '## Como testar', '']
    o += [f'{k + 1}. {t}' for k, t in enumerate(info['teste'])] + ['']
    if info['atencao']:
        o += ['## Atenção', ''] + [f'- {t}' for t in info['atencao']] + ['']
    if b.changes:
        o += ['## O que mudou na v3.0', ''] + [f'- {t}' for t in b.changes] + ['']
    nav = []
    if ant:
        nav.append(f'← [{PLACAS[ant]["nome"]}]({PASTAS[ant]}.md)')
    nav.append('[todas as placas](README.md)')
    if prox:
        nav.append(f'[{PLACAS[prox]["nome"]}]({PASTAS[prox]}.md) →')
    o += ['---', ' · '.join(nav), '']
    return '\n'.join(o)


def indice(bs, meta, ordem):
    o = ['# As 13 placas — guia detalhado', '',
         '> **Computador 8 Bits v3.0** — projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.', '',
         'Cada placa tem uma página com: a função dela no computador, como o circuito funciona, o papel de cada CI, '
         'o significado dos LEDs, o esquemático, a placa em 3D, a pinagem dos conectores, a lista de componentes e '
         'como testar.', '',
         f'<p align="center">{BOTAO}</p>', '',
         f'🧊 **[3D Viewer]({VIEWER})** — gire, aproxime e veja a placa por cima e por baixo '
         '(instruções em [docs/3d](../3d/README.md)). Os arquivos `.stl` também abrem em 3D direto no GitHub.', '',
         '| # | Placa | Função | Tamanho | 3D |', '|---:|---|---|---|---|']
    for k in ordem:
        b = bs[k]
        p, info, m = PASTAS[k], PLACAS[k], meta.get(PASTAS[k], {})
        o.append(f'| {info["ordem"]} | **[{info["nome"]}]({p}.md)** | {info["resumo"]} | '
                 f'{round(m.get("largura_mm", 0))} × {round(m.get("altura_mm", 0))} mm | [STL](../3d/stl/{p}.stl) |')
    o += ['', '## Galeria', '', '<table>']
    for i in range(0, len(ordem), 3):
        o.append('<tr>')
        for k in ordem[i:i + 3]:
            p = PASTAS[k]
            o.append(f'<td align="center" width="33%"><a href="{p}.md"><img src="../imagens/3d/{p}.png" '
                     f'alt="{PLACAS[k]["nome"]}"><br><b>{PLACAS[k]["nome"]}</b></a></td>')
        o.append('</tr>')
    o += ['</table>', '', '---', 'Voltar para a [documentação](../README.md)', '']
    return '\n'.join(o)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    meta = json.load(open(os.path.join(RAIZ, 'docs', '3d', 'placas3d.json')))
    dest = destinos()
    bs = {b.key: b for b in designs.all_boards()}
    ordem = sorted(bs, key=lambda k: PLACAS[k]['ordem'])
    for k in ordem:
        esquema_png(PASTAS[k])
        open(os.path.join(SAIDA, PASTAS[k] + '.md'), 'w').write(pagina(bs[k], meta, dest, ordem))
        print('docs/placas/' + PASTAS[k] + '.md')
    open(os.path.join(SAIDA, 'README.md'), 'w').write(indice(bs, meta, ordem))


if __name__ == '__main__':
    main()
