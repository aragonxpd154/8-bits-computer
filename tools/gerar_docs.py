#!/usr/bin/env python3
"""Gera tabelas da documentacao (lista de materiais, cabos, sinais) a partir de designs.py."""
import os, sys, re, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'gerador-kicad'))
import designs, symlib

ROOT = os.path.abspath(os.path.join(HERE, '..'))
NOMES = {'CLOCK': 'Clock', 'RESET': 'Reset', 'PC': 'Contador de Programa', 'RAM': 'RAM e MAR', 'IR': 'Reg. Instrucao',
         'CD': 'Decodificador de Controle', 'FETCH': 'Contador de Passos', 'ACC': 'Registrador A', 'B': 'Registrador B',
         'ALU': 'ULA', 'OUT': 'Registrador de Saida', 'DISPLAY': 'Display Decimal', 'BACKPLANE': 'Backplane'}
nat = lambda s: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]
txt = lambda n: (n or 'NC').replace('~{', '/').replace('}', '')


def tipo(c, L):
    fp = c.fp or L[c.sym].footprint
    if c.group == 'IC' and c.sym.startswith('Display'):
        return 'Display 7 segmentos 4 digitos 0,4" catodo comum (12 pinos)'
    if c.group == 'IC':
        pinos = re.search(r'DIP-(\d+)', fp).group(1)
        return f'CI {c.value.split(" (")[0]} (DIP-{pinos})'
    if c.sym == 'R':
        return f'Resistor {c.value} 1/4 W'
    if c.sym in ('C', 'C_Pol'):
        return f'Capacitor {c.value}' + (' eletrolitico' if c.sym == 'C_Pol' and 'tantalo' not in c.value and 'uF' in c.value else '')
    if c.sym == 'LED':
        return c.value
    if c.sym == 'Conn_01x04':
        return 'Barra de pinos macho 1x4 2,54 mm (90 graus ou reta)'
    if c.sym.startswith('R_Network'):
        n = int(c.sym[-2:])
        return f'Rede resistiva SIP-{n+1} {c.value.split("x")[1]} comum no pino 1 ({n} resistores)'
    if c.sym.startswith('SW_DIP'):
        return f'Chave DIP {int(c.sym[-2:])} vias'
    if c.sym == 'SW_Push':
        return 'Botao tactil 6x6 mm (4 terminais)'
    if c.sym == 'SW_SPDT':
        return 'Chave deslizante SPDT 3 terminais passo 2,54 mm'
    if c.sym == 'POT':
        return 'Potenciometro 100k linear 9 mm (Alps RK09K)'
    return c.value


def bom_total():
    L = symlib.build_library()
    tot = {}
    por_placa = {}
    for b in designs.all_boards():
        for c in b.comps.values():
            t = tipo(c, L)
            tot[t] = tot.get(t, 0) + 1
            por_placa.setdefault(b.key, {}).setdefault(t, []).append(c.ref)
    ics = sum(1 for b in designs.all_boards() for c in b.comps.values() if c.group == 'IC' and not c.sym.startswith('Disp'))
    sockets = {}
    for b in designs.all_boards():
        for c in b.comps.values():
            if c.group == 'IC' and not c.sym.startswith('Disp'):
                fp = c.fp or L[c.sym].footprint
                n = re.search(r'DIP-(\d+)', fp).group(1)
                k = f'Soquete DIP-{n}' + (' largo (600 mil) - ou ZIF 24 pinos' if n == '24' else ' (300 mil)')
                sockets[k] = sockets.get(k, 0) + 1
    return tot, por_placa, sockets, ics


def md_bom():
    tot, por_placa, sockets, ics = bom_total()
    o = ['# Lista de materiais completa - Computador 8 Bits v3.0', '',
         '> Autor do projeto: **Marcos Silva dos Santos** (MarcosObel). Gerada automaticamente a partir de '
         '`tools/gerador-kicad/designs.py`.', '',
         'Compre **10 % a mais** de resistores, capacitores, LEDs e barras de pinos, e **1 CI reserva** de cada '
         'tipo mais usado (74LS173, 74LS245, 74LS157).', '',
         '## Totais (todas as 13 placas)', '', '| Quantidade | Componente |', '|---:|---|']
    for k, v in sorted(tot.items(), key=lambda x: (not x[0].startswith('CI'), x[0])):
        o.append(f'| {v} | {k} |')
    o += ['', '### Soquetes (recomendados para todos os CIs)', '', '| Quantidade | Item |', '|---:|---|']
    for k, v in sorted(sockets.items()):
        o.append(f'| {v} | {k} |')
    o += ['', f'Total de circuitos integrados: **{ics}** (+ 1 display).', '',
          '### Itens gerais', '',
          '| Quantidade | Item |', '|---:|---|',
          '| 1 | Fonte 5 V regulada, 2 A ou mais, plugue P4 5,5 x 2,1 mm (centro positivo) |',
          f'| {len(designs.CABOS)} | Cabo jumper femea-femea de 4 vias, 20 cm (ou "cabo flat 4 vias" com conectores Dupont) |',
          '| 1 | Base de MDF/acrilico ~ 60 x 45 cm |', '| 60 | Espacador M3 x 10 mm + parafuso + porca (4 por placa) |',
          '| 1 | Gravador de EEPROM (TL866II Plus / XGecu T48) - para as 4 EEPROMs 28C16 |',
          '| - | Placa de fenolite/fibra de vidro cobreada dupla face (ver tamanhos em hardware/README.md) |',
          '| - | Percloreto de ferro, papel couche/glossy, fio rigido 0,6 mm (vias), estanho, fluxo |', '',
          '## Por placa', '']
    for k, d in por_placa.items():
        o += [f'### {NOMES[k]} (`{k}`)', '', '| Qtd | Componente | Referencias |', '|---:|---|---|']
        for t, refs in sorted(d.items(), key=lambda x: nat(sorted(x[1], key=nat)[0])):
            o.append(f'| {len(refs)} | {t} | {" ".join(sorted(refs, key=nat))} |')
        o.append('')
    return '\n'.join(o)


def md_cabos():
    bs = {b.key: b for b in designs.all_boards()}
    bp = bs['BACKPLANE']
    o = ['| # | Placa | Conector | Sinais (pino 1 -> 4) | Liga em |', '|---:|---|---|---|---|']
    for i, (placa, j, dest) in enumerate(designs.CABOS, 1):
        c = bs[placa].comps[j]
        sinais = ' '.join(c.pinlabels)
        if isinstance(dest, tuple):
            dc = bs[dest[0]].comps[dest[1]]
            alvo = f'**cabo direto** -> {NOMES[dest[0]]} {dest[1]} ({dc.value})'
        else:
            alvo = f'Backplane **{bp.header_map[dest]}** ({dest})'
        o.append(f'| {i} | {NOMES[placa]} | {j} {c.value} | `{sinais}` | {alvo} |')
    return '\n'.join(o)


def md_sinais():
    bs = {b.key: b for b in designs.all_boards()}
    # quem gera / quem usa (pelo tipo de pino dos CIs)
    L = symlib.build_library()
    info = {}
    sinais = ['CLK', '~{CLK}', 'HLT', 'RST', '~{RST}', '~{Y5}', '~{STEPCLR}', 'PCI', '~{JMP}', '~{PCO}', '~{MAI}', 'RMI',
              '~{RMO}', '~{IRI}', '~{IRO}', '~{ACI}', '~{ACO}', 'SUB', 'AL0', 'AL1', '~{ALUO}', 'NOT', '~{BRI}', '~{ORI}']
    desc = {'CLK': 'clock do sistema', '~{CLK}': 'clock invertido (contador de passos)', 'HLT': 'para o clock',
            'RST': 'reset (ativo alto, 74LS173)', '~{RST}': 'reset (ativo baixo, 74LS161 do PC)',
            '~{Y5}': 'passo T5 alcancado', '~{STEPCLR}': 'zera o contador de passos',
            'PCI': 'incrementa o PC', '~{JMP}': 'carrega o PC (salto)', '~{PCO}': 'PC -> barramento',
            '~{MAI}': 'barramento -> MAR', 'RMI': 'barramento -> RAM (escrita)', '~{RMO}': 'RAM -> barramento',
            '~{IRI}': 'barramento -> IR', '~{IRO}': 'operando do IR -> barramento', '~{ACI}': 'barramento -> A',
            '~{ACO}': 'A -> barramento', 'SUB': 'subtracao na ULA', 'AL0': 'selecao da ULA (bit 0)',
            'AL1': 'selecao da ULA (bit 1)', '~{ALUO}': 'resultado da ULA -> barramento', 'NOT': 'inverte A (com AL=11)',
            '~{BRI}': 'barramento -> B', '~{ORI}': 'barramento -> OUT'}
    eeprom = {}
    cd = bs['CD']
    for u, e in (('U1', 'EEPROM2'), ('U2', 'EEPROM1'), ('U3', 'EEPROM0')):
        for p, n in cd.comps[u].pins.items():
            if p in ('9', '10', '11', '13', '14', '15', '16', '17') and n and n not in ('GND', '+5V'):
                bit = ['9', '10', '11', '13', '14', '15', '16', '17'].index(p)
                eeprom[n] = f'{e} IO{bit} ({u} pino {p})'
    o = ['| Sinal | Nivel ativo | Funcao | Origem | Destinos (placa: CI pino) |', '|---|---|---|---|---|']
    for s in sinais:
        orig, dest = [], []
        for b in bs.values():
            if b.key == 'BACKPLANE':
                continue
            for c in b.comps.values():
                if c.group != 'IC':
                    continue
                sym = L[c.sym]
                for p, n in c.pins.items():
                    if n == s:
                        et = sym.pin(p).etype
                        lab = f'{b.key}: {c.ref}.{p} ({sym.pin(p).name.replace("~{", "/").replace("}", "")})'
                        (orig if et in ('output', 'tri_state', 'open_collector') else dest).append(lab)
        if s in eeprom:
            orig = [f'CD: {eeprom[s]}']
        nivel = 'baixo' if s.startswith('~{') else 'alto'
        o.append(f'| `{txt(s)}` | {nivel} | {desc[s]} | {"<br>".join(orig)} | {"<br>".join(dest)} |')
    return '\n'.join(o)


if __name__ == '__main__':
    e = designs.verificar_cabos()
    if e:
        raise SystemExit('\n'.join(e))
    open(os.path.join(ROOT, 'docs', 'lista-de-materiais-completa.md'), 'w').write(md_bom() + '\n')
    open(os.path.join(ROOT, 'docs', '_tabela_cabos.md'), 'w').write(md_cabos() + '\n')
    open(os.path.join(ROOT, 'docs', '_tabela_sinais.md'), 'w').write(md_sinais() + '\n')
    print('ok')


# ---------------------------------------------------------------------------
def info_pcb(path):
    t = open(path).read()
    vias = len(re.findall(r'\(via \(at', t))
    xs, ys = [], []
    for m in re.finditer(r'\(gr_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)\s*\(stroke[^\n]*?\(layer "Edge.Cuts"\)', t):
        xs += [float(m.group(1)), float(m.group(3))]; ys += [float(m.group(2)), float(m.group(4))]
    segs_f = len(re.findall(r'\(segment .*?\(layer "F.Cu"\)', t))
    segs_b = len(re.findall(r'\(segment .*?\(layer "B.Cu"\)', t))
    return (max(xs) - min(xs), max(ys) - min(ys), vias, segs_f, segs_b)


def renderizar(pcb, png):
    import subprocess, tempfile
    from PIL import Image, ImageChops
    with tempfile.TemporaryDirectory() as td:
        pdf = os.path.join(td, 'p.pdf')
        subprocess.run(['kicad-cli', 'pcb', 'export', 'pdf', '--layers', 'F.Cu,B.Cu,F.SilkS,Edge.Cuts', '-o', pdf, pcb],
                       check=True, capture_output=True)
        subprocess.run(['pdftoppm', '-r', '110', '-png', '-singlefile', pdf, os.path.join(td, 'p')], check=True)
        im = Image.open(os.path.join(td, 'p.png')).convert('RGB')
        bb = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
        # remove a regua e o titulo de impressao (Cmts.User nao foi plotado) -> recorta no conteudo
        im.crop((max(bb[0] - 6, 0), max(bb[1] - 6, 0), bb[2] + 6, bb[3] + 6)).save(png, optimize=True)


def md_hardware(render=True):
    import glob
    o = ['# Hardware — Computador 8 Bits v3.0', '',
         '> Projeto e PCBs de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0. Gerado por `tools/gerar_docs.py`.', '',
         '- `kicad/<placa>/` — projeto KiCad (abra o `.kicad_pro`). Formato KiCad 7 (abre no 7, 8 e 9).',
         '- `fabricacao/<placa>/` — **Gerber para a fábrica**, guia de montagem 1:1, esquemático, BOM, relatório DRC.',
         '- [`esquema-eletrico-completo.pdf`](esquema-eletrico-completo.pdf) — todos os esquemáticos num único PDF.', '',
         'Todas: 2 camadas, furo metalizado, trilha 0,5 mm (alimentação 0,9 mm), isolação 0,4 mm, '
         'vias 1,6/0,8 mm, 4 furos M3 nos cantos, serigrafia didática. Como pedir: '
         '[docs/03-fabricacao-das-placas.md](../docs/03-fabricacao-das-placas.md).', '',
         '| Placa | Tamanho (mm) | Vias | Trilhas na face de cima | Esquema | Fabricação |',
         '|---|---|---:|---:|---|---|']
    imgs = []
    os.makedirs(os.path.join(ROOT, 'docs', 'imagens', 'placas'), exist_ok=True)
    for b in designs.all_boards():
        pcb = os.path.join(ROOT, 'hardware', 'kicad', b.folder, b.folder + '.kicad_pcb')
        if not os.path.exists(pcb):
            continue
        w, h, v, sf, sb = info_pcb(pcb)
        o.append(f'| **{b.title}** | {w:.0f} × {h:.0f} | {v} | {sf} segmentos | '
                 f'[PDF](fabricacao/{b.folder}/0-esquematico.pdf) | [arquivos](fabricacao/{b.folder}/) |')
        png = os.path.join(ROOT, 'docs', 'imagens', 'placas', b.folder + '.png')
        if render:
            renderizar(pcb, png)
        imgs.append((b, png))
    o += ['', 'Vermelho = cobre da face de cima (componentes) · azul = cobre da face de baixo (solda) · '
          'amarelo = serigrafia.', '']
    for b, png in imgs:
        o += [f'## {b.title}', '', b.desc, '', f'![{b.title}](../docs/imagens/placas/{os.path.basename(png)})', '']
    return '\n'.join(o)


def preencher(arquivo, marcador, conteudo):
    p = os.path.join(ROOT, 'docs', arquivo)
    t = open(p).read()
    if marcador in t:
        t = t.replace(marcador, conteudo)
        open(p, 'w').write(t)


if __name__ == '__main__' and '--hardware' in sys.argv:
    open(os.path.join(ROOT, 'hardware', 'README.md'), 'w').write(md_hardware('--sem-imagens' not in sys.argv) + '\n')
    preencher('01-arquitetura.md', 'TABELA_SINAIS', md_sinais())
    preencher('05-interligacao-e-backplane.md', 'TABELA_CABOS', md_cabos())
    for f in ('_tabela_cabos.md', '_tabela_sinais.md'):
        p = os.path.join(ROOT, 'docs', f)
        if os.path.exists(p):
            os.remove(p)
    print('hardware/README.md ok')
