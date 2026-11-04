#!/usr/bin/env python3
"""Testa o microcodigo com os programas de exemplo, usando os binarios REAIS das EEPROMs.

- programas/testes/*.asm: 14 programas, um para cada instrucao. Confere o resultado esperado no display.
- programas/*.asm: os exemplos deste projeto (confere que rodam sem conflito no barramento).

Uso:  python3 testar.py        (sai com codigo 1 se algum teste falhar)
Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os, sys, json, glob
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import montador
from emulador import Computador

PROG = os.path.join(AQUI, '..', 'programas')
falhas = 0
print('Testes das instrucoes')
for t in json.load(open(os.path.join(PROG, 'testes', 'esperado.json'))):
    mem = montador.montar(open(os.path.join(PROG, 'testes', t['nome'] + '.asm')).read())[0]
    c = Computador(mem)
    saida = c.rodar(3000, max_saidas=len(t['saida']))[:len(t['saida'])]
    ok = saida == t['saida']
    falhas += not ok
    print(f'  {"OK " if ok else "ERRO"}  {t["nome"]:20s} esperado {t["saida"]}  obtido {saida}')
print('Exemplos do projeto')
for f in sorted(glob.glob(os.path.join(PROG, '*.asm'))):
    mem = montador.montar(open(f).read())[0]
    c = Computador(mem)
    try:
        saida = c.rodar(3000, max_saidas=12)
        print(f'  OK    {os.path.basename(f):28s} saida {saida}{" (HLT)" if c.parado else " ..."}')
    except RuntimeError as e:
        falhas += 1
        print(f'  ERRO  {os.path.basename(f):28s} {e}')
print('TODOS OS TESTES OK' if not falhas else f'{falhas} TESTE(S) FALHARAM')
sys.exit(1 if falhas else 0)
