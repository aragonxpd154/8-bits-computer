#!/usr/bin/env python3
"""Monta o computador completo em 3D: as 14 placas numa base de madeira, com espacadores, tampa de acrilico
e os 58 cabos de 4 vias. Gera docs/3d/montagem.json, lido pela pagina docs/3d/montagem.html.

O JSON traz: posicao de cada placa na base, os pinos de cada conector, os furos de fixacao, cada LED
(posicao, cor e qual sinal ele mostra), a posicao do display e o microcodigo/programas para a simulacao.

Uso:  python3 tools/montagem3d.py        (precisa do modulo pcbnew do KiCad)
Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import sys
import json

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, 'gerador-kicad'))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'firmware', 'microcodigo'))
sys.path.insert(0, os.path.join(RAIZ, 'firmware', 'ferramentas'))
import designs  # noqa: E402
from placas_info import PLACAS, PASTAS  # noqa: E402
import microcodigo as mc  # noqa: E402
import montador  # noqa: E402

# posicao (canto superior esquerdo, mm) de cada placa na base - mesmo arranjo do capitulo 5
BASE = (650.0, 560.0, 18.0)          # largura, profundidade, espessura (mm)
POS = {
    'CLOCK': (20, 20), 'RESET': (20, 124), 'PC': (20, 200), 'RAM': (20, 287),
    'BACKPLANE': (185, 20), 'CW': (185, 191), 'CD': (185, 291), 'IR': (185, 370), 'FETCH': (305, 370),
    'ACC': (409, 20), 'ALU': (409, 107), 'B': (409, 253), 'OUT': (409, 340), 'DISPLAY': (409, 427),
}
ESPACADOR = 25.0                      # espacadores M3 de 25 mm: os cabos passam por baixo das placas
TAMPA = 105.0                         # altura da tampa de acrilico acima da base (mm)
CORES_LED = {'verde': '#3dff74', 'vermelho': '#ff2b2b', 'amarelo': '#ffd400', 'azul': '#3d9bff'}
POWER = {'+5V', 'GND', 'VIN', 'VSW'}


def extrair(b):
    import pcbnew
    pasta = PASTAS[b.key]
    pcb = pcbnew.LoadBoard(os.path.join(RAIZ, 'hardware', 'kicad', pasta, pasta + '.kicad_pcb'))
    mm = pcbnew.ToMM
    bb = pcb.GetBoardEdgesBoundingBox()
    lw = max([mm(d.GetWidth()) for d in pcb.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts] or [0])
    x0, y0 = mm(bb.GetX()) + lw / 2, mm(bb.GetY()) + lw / 2
    w, h = mm(bb.GetWidth()) - lw, mm(bb.GetHeight()) - lw
    fps = {fp.GetReference(): fp for fp in pcb.GetFootprints()}

    def pads(fp):
        out = {}
        for p in fp.Pads():
            if p.GetNumber():
                q = p.GetPosition()
                out.setdefault(p.GetNumber(), (round(mm(q.x) - x0, 2), round(mm(q.y) - y0, 2)))
        return out
    conn, furos, leds = {}, [], []
    for ref, fp in fps.items():
        nome = fp.GetFPID().GetLibItemName().wx_str()
        if nome.startswith('MountingHole'):
            q = fp.GetPosition()
            furos.append((round(mm(q.x) - x0, 2), round(mm(q.y) - y0, 2)))
        elif ref.startswith('J') and nome.startswith('PinHeader_1x04'):
            p = pads(fp)
            conn[ref] = [p[str(i)] for i in range(1, 5)]
        elif ref.startswith('J1') and b.key == 'BACKPLANE' and 'BarrelJack' in nome:
            q = fp.GetPosition()
            conn['JACK'] = [(round(mm(q.x) - x0, 2), round(mm(q.y) - y0, 2))]
    for c in b.comps.values():
        if c.group != 'LED':
            continue
        p = list(pads(fps[c.ref]).values())
        cx, cy = sum(v[0] for v in p) / len(p), sum(v[1] for v in p) / len(p)
        a, k = c.pins.get('2'), c.pins.get('1')
        if a and not a.startswith('L') and a not in POWER:
            sinal, nivel = a, 1                       # acende com o sinal em 1
        elif k and k not in POWER:
            sinal, nivel = k, 0                       # acende com o sinal em 0
        else:
            sinal, nivel = '+5V', 1                   # LED de energia
        cor = next((v for kk, v in CORES_LED.items() if kk in c.value), '#ff2b2b')
        leds.append({'ref': c.ref, 'x': round(cx, 2), 'y': round(cy, 2), 'cor': cor, 'sinal': sinal, 'nivel': nivel})
    disp = None
    if b.key == 'DISPLAY':
        r = fps['DS1'].GetBoundingBox(False, False)
        disp = [round(mm(r.GetX()) - x0 + 0.4, 2), round(mm(r.GetY()) - y0 + 0.4, 2),
                round(mm(r.GetRight()) - x0 - 0.4, 2), round(mm(r.GetBottom()) - y0 - 0.4, 2)]
    return {'id': pasta, 'key': b.key, 'nome': PLACAS[b.key]['nome'], 'x': POS[b.key][0], 'y': POS[b.key][1],
            'w': round(w, 2), 'h': round(h, 2), 'conectores': conn, 'furos': furos, 'leds': leds, 'display': disp}


def main():
    boards = {b.key: b for b in designs.all_boards()}
    placas = {k: extrair(b) for k, b in boards.items()}
    # sobreposicao?
    ks = list(placas)
    for i, a in enumerate(ks):
        A = placas[a]
        assert A['x'] + A['w'] <= BASE[0] - 5 and A['y'] + A['h'] <= BASE[1] - 5, f'{a} fora da base'
        for bk in ks[i + 1:]:
            B = placas[bk]
            if not (A['x'] + A['w'] + 4 <= B['x'] or B['x'] + B['w'] + 4 <= A['x'] or
                    A['y'] + A['h'] + 4 <= B['y'] or B['y'] + B['h'] + 4 <= A['y']):
                raise SystemExit(f'placas sobrepostas: {a} x {bk}')
    bp = boards['BACKPLANE']
    cabos = []
    for placa, j, dest in designs.CABOS:
        if isinstance(dest, tuple):
            dk, dj = dest
        else:
            dk, dj = 'BACKPLANE', bp.header_map[dest]
        labels = boards[placa].comps[j].pinlabels
        energia = labels[:2] == ['+5V', '+5V']
        pa = [(placas[placa]['x'] + x, placas[placa]['y'] + y) for x, y in placas[placa]['conectores'][j]]
        pb = [(placas[dk]['x'] + x, placas[dk]['y'] + y) for x, y in placas[dk]['conectores'][dj]]
        dist = ((pa[0][0] - pb[0][0]) ** 2 + (pa[0][1] - pb[0][1]) ** 2) ** 0.5
        cabos.append({'de': [placa, j], 'para': [dk, dj], 'a': pa, 'b': pb, 'energia': energia,
                      'direto': isinstance(dest, tuple), 'dist': round(dist)})
    # comprimento do cabo pelo trajeto real (sobe/desce + borda + "L" pela base), como na pagina 3D
    alt = 1.6 + 2.5 + 14 + 7                       # topo do conector femea + folga
    def borda(p, x, y):
        d = sorted([(x - p['x'], (p['x'] - 7, y)), (p['x'] + p['w'] - x, (p['x'] + p['w'] + 7, y)),
                    (y - p['y'], (x, p['y'] - 7)), (p['y'] + p['h'] - y, (x, p['y'] + p['h'] + 7))])[0]
        return d[0] + 7, d[1]
    for cb in cabos:
        pa, pb = placas[cb['de'][0]], placas[cb['para'][0]]
        ca = ((cb['a'][0][0] + cb['a'][3][0]) / 2, (cb['a'][0][1] + cb['a'][3][1]) / 2)
        cbb = ((cb['b'][0][0] + cb['b'][3][0]) / 2, (cb['b'][0][1] + cb['b'][3][1]) / 2)
        da, A = borda(pa, *ca)
        db, B = borda(pb, *cbb)
        L = 2 * (alt + ESPACADOR) + da + db + abs(A[0] - B[0]) + abs(A[1] - B[1])
        cb['comprimento'] = round(L)
        cb['cabo_cm'] = next(c for c in (20, 30, 40, 50, 60, 80) if c * 10 >= L * 1.1)

    # microcodigo e programas para a simulacao
    nomes = {v: k for k, v in mc.NOMES.items()}
    instr = {}
    for op, (mn, _, passos, _) in mc.INSTRUCOES.items():
        if passos in ('CF', 'ZF'):
            passos = []
        instr[op] = {'mn': mn, 'passos': [[mc.NOMES[s] for s in st] for st in passos]}
    progs = {}
    for nome, arq in (('Fibonacci', '04-fibonacci.asm'), ('Contador', '03-contador.asm'),
                      ('Tabuada do 7', '06-multiplica-por-soma.asm'), ('28 + 14', '01-soma.asm')):
        progs[nome] = montador.montar(open(os.path.join(RAIZ, 'firmware', 'programas', arq)).read())[0]
    out = {'base': BASE, 'espacador': ESPACADOR, 'tampa': TAMPA, 'placas': list(placas.values()), 'cabos': cabos,
           'busca': [['PCO', 'MAI'], ['RMO', 'IRI', 'PCI']], 'instrucoes': instr, 'programas': progs}
    p = os.path.join(RAIZ, 'docs', '3d', 'montagem.json')
    json.dump(out, open(p, 'w'), separators=(',', ':'), ensure_ascii=False)
    from collections import Counter
    print(p, f'{len(cabos)} cabos; tamanhos:', dict(sorted(Counter(c['cabo_cm'] for c in cabos).items())))


if __name__ == '__main__':
    main()
