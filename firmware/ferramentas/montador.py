#!/usr/bin/env python3
"""Montador (assembler) do Computador 8 Bits - Marcos Silva dos Santos (GPL-3.0).

Uso:  python3 montador.py programa.asm [-o programa.bin]

Sintaxe:
    ; comentario
    rotulo: MNEMONICO operando      operando = numero (0..15), rotulo, 0x0F, 0b1010
    rotulo: DB valor                 byte de dado (0..255)
Saida: tabela endereco -> byte, com a posicao das chaves DIP da placa RAM (1 = chave LIGADA).
"""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'microcodigo'))
from microcodigo import INSTRUCOES

OPC = {v[0]: (k, v[1]) for k, v in INSTRUCOES.items() if not (v[0] == 'NOP' and k != 0)}


def num(tok, rot):
    tok = tok.strip()
    if tok in rot:
        return rot[tok]
    return int(tok, 0)


def montar(texto):
    linhas = []
    rot = {}
    end = 0
    for nl, l in enumerate(texto.splitlines(), 1):
        l = l.split(';')[0].strip()
        if not l:
            continue
        m = re.match(r'^(\w+):\s*(.*)$', l)
        if m:
            rot[m.group(1)] = end
            l = m.group(2).strip()
            if not l:
                continue
        linhas.append((nl, end, l))
        end += 1
    if end > 16:
        raise SystemExit(f'programa tem {end} bytes; a RAM tem so 16')
    mem = [0] * 16
    lista = []
    for nl, a, l in linhas:
        p = l.split(None, 1)
        mn = p[0].upper()
        if mn == 'DB':
            v = num(p[1], rot) & 0xFF
        else:
            if mn not in OPC:
                raise SystemExit(f'linha {nl}: instrucao desconhecida {mn}')
            op, tem = OPC[mn]
            arg = num(p[1], rot) if len(p) > 1 else 0
            if tem and len(p) < 2:
                raise SystemExit(f'linha {nl}: {mn} precisa de operando')
            if not 0 <= arg <= 15:
                raise SystemExit(f'linha {nl}: operando {arg} fora de 0..15')
            v = (op << 4) | arg
        mem[a] = v
        lista.append((a, v, l))
    return mem, lista, rot


def chaves(v, n=8):
    return ''.join('█' if (v >> (n - 1 - i)) & 1 else '·' for i in range(n))


def listagem(lista):
    out = ['End  Chaves-END  Chaves-DADO   Hex  Binario    Instrucao',
           '     (4 3 2 1)   (8 7 6 5 4 3 2 1)']
    for a, v, l in lista:
        out.append(f'{a:2d}   {chaves(a, 4)}        {chaves(v)}     {v:02X}   {v:08b}   {l}')
    out.append('█ = chave LIGADA (1)   · = chave DESLIGADA (0).  Chave 1 = bit 0 (direita).')
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = sys.argv[1]
    mem, lista, rot = montar(open(src, encoding='utf-8').read())
    print(listagem(lista))
    dst = sys.argv[sys.argv.index('-o') + 1] if '-o' in sys.argv else os.path.splitext(src)[0] + '.bin'
    open(dst, 'wb').write(bytes(mem))
    print(f'\n{dst} gravado (16 bytes)')
