#!/usr/bin/env python3
"""Monta o pacote do repositorio (pasta limpa + zip). Uso: python3 empacotar.py <saida.zip> [--parcial]"""
import os, sys, re, shutil, subprocess, glob, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
PAC = '/home/claude/pacote'
sys.path.insert(0, os.path.join(HERE, 'gerador-kicad'))
import designs

saida = sys.argv[1]
parcial = '--parcial' in sys.argv
stage = '/home/claude/staging_pkg'
shutil.rmtree(stage, ignore_errors=True)
dst = os.path.join(stage, '8-bits-computer')
shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.kicad_prl', '*.dsn', '*.ses',
                                                         'fp-info-cache', '*-backups'))


def drc_ok(rpt):
    if not os.path.exists(rpt):
        return False, 'sem PCB roteada'
    t = open(rpt).read()
    blocks = re.findall(r'^\[(\w+)\]:.*?Severity: (\w+)', t, re.M | re.S)
    errs = [k for k, s in blocks if s == 'error' and not k.startswith(('lib_footprint', 'silk_', 'text_'))]
    return (not errs), (f'{len(errs)} erro(s)/ligacao(oes) pendente(s)' if errs else 'ok')


status = []
for b in designs.all_boards():
    fd = os.path.join(dst, 'hardware', 'fabricacao', b.folder)
    ok, msg = drc_ok(os.path.join(fd, 'relatorio-drc.txt'))
    if not ok:
        for z in glob.glob(os.path.join(fd, '*-gerber.zip')):
            os.remove(z)
        if not os.path.exists(os.path.join(dst, 'hardware', 'kicad', b.folder, b.folder + '.kicad_pcb')) or \
                'sem PCB' in msg:
            shutil.rmtree(os.path.join(dst, 'hardware', 'kicad', b.folder), ignore_errors=True)
            shutil.rmtree(fd, ignore_errors=True)
    status.append((b, ok, msg))
    if not ok and not parcial:
        raise SystemExit(f'Placa {b.key} com problema: {msg}')

subprocess.run([sys.executable, os.path.join(dst, 'tools', 'gerar_docs.py'), '--hardware'], check=True)
try:
    subprocess.run([sys.executable, os.path.join(dst, 'tools', 'montar_pdf_completo.py')], check=True,
                   capture_output=True)
except subprocess.CalledProcessError as e:
    print('PDF completo nao gerado (faltam esquematicos):', e.stderr[-300:])

if parcial:
    linhas = ['# Pacote PARCIAL — Computador 8 Bits v3.0', '',
              'Autor: Marcos Silva dos Santos (MarcosObel). Apague este arquivo quando chegar o pacote final.', '',
              '| Placa | Situação |', '|---|---|']
    for b, ok, msg in status:
        linhas.append(f'| {b.title} | {"✅ pronta para fabricar" if ok else "⏳ " + msg + " — Gerber retirado, NÃO fabricar ainda"} |')
    linhas += ['', 'Firmware, documentação e ferramentas: completos.']
    open(os.path.join(dst, 'STATUS-PACOTE-PARCIAL.md'), 'w').write('\n'.join(linhas) + '\n')

for f in ('publicar-no-github.sh', 'LEIA-ME-PRIMEIRO.txt'):
    shutil.copy(os.path.join(PAC, f), stage)
if os.path.exists(saida):
    os.remove(saida)
with zipfile.ZipFile(saida, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(stage):
        for f in files:
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, stage))
for b, ok, msg in status:
    print(f'{b.key:10s} {"OK" if ok else msg}')
print(saida, os.path.getsize(saida) // 1024, 'KB')
