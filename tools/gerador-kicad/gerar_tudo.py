#!/usr/bin/python3
"""Gera TODO o hardware do Computador 8 Bits v3.0 (Marcos Silva dos Santos):
   esquematicos, PCBs roteadas, verificacao de netlist, Gerbers e PDFs de fabricacao caseira.
Uso (no Zorin OS / Ubuntu com KiCad 7+ e Java 21):
   /usr/bin/python3 gerar_tudo.py [PLACA ...] [--sem-rotear]
"""
import os, sys, json, subprocess, csv, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import designs, symlib, sch, verify

KICAD_DIR = os.path.join(ROOT, 'hardware', 'kicad')
FAB_DIR = os.path.join(ROOT, 'hardware', 'fabricacao')
LIB_DIR = os.path.join(ROOT, 'hardware', 'kicad', 'bibliotecas')


def write_lib_tables(d):
    open(os.path.join(d, 'sym-lib-table'), 'w').write(
        '(sym_lib_table\n  (lib (name "computador8bits")(type "KiCad")'
        '(uri "${KIPRJMOD}/../bibliotecas/computador8bits.kicad_sym")(options "")(descr "Computador 8 Bits"))\n)\n')
    open(os.path.join(d, 'fp-lib-table'), 'w').write(
        '(fp_lib_table\n  (lib (name "computador8bits")(type "KiCad")'
        '(uri "${KIPRJMOD}/../bibliotecas/computador8bits.pretty")(options "")(descr "Computador 8 Bits"))\n)\n')


def bom(board, L, path):
    rows = {}
    for c in board.comps.values():
        fp = c.fp or L[c.sym].footprint
        key = (c.value, fp)
        rows.setdefault(key, []).append(c.ref)
    import re
    nat = lambda s: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Quantidade', 'Valor', 'Referencias', 'Footprint'])
        for (val, fp), refs in sorted(rows.items(), key=lambda x: nat(sorted(x[1], key=nat)[0])):
            w.writerow([len(refs), val, ' '.join(sorted(refs, key=nat)), fp.split(':')[-1]])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    route = '--sem-rotear' not in sys.argv
    os.makedirs(LIB_DIR, exist_ok=True)
    L = symlib.write_library(os.path.join(LIB_DIR, 'computador8bits.kicad_sym'))
    boards = designs.all_boards()
    if args:
        boards = [b for b in boards if b.key in args]
    report = []
    for b in boards:
        t0 = time.time()
        kd = os.path.join(KICAD_DIR, b.folder)
        fd = os.path.join(FAB_DIR, b.folder)
        os.makedirs(kd, exist_ok=True); os.makedirs(fd, exist_ok=True)
        write_lib_tables(kd)
        schp = os.path.join(kd, b.folder + '.kicad_sch')
        w = sch.SchWriter(b, L, b.folder)
        w.write(schp)
        net = os.path.join('/tmp', b.folder + '.net')
        subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', net, schp],
                       check=True, capture_output=True)
        errs = verify.compare(b, verify.parse_kicad_net(net))
        subprocess.run(['kicad-cli', 'sch', 'export', 'pdf', '-o', os.path.join(fd, '0-esquematico.pdf'), schp],
                       check=True, capture_output=True)
        bom(b, L, os.path.join(fd, 'lista-de-materiais.csv'))
        uu = os.path.join('/tmp', b.folder + '-uuids.json')
        json.dump(w.sym_uuid, open(uu, 'w'))
        cmd = ['/usr/bin/python3', os.path.join(HERE, 'pcbgen.py'), b.key, kd, uu] + ([] if route else ['--noroute'])
        env = dict(os.environ, FP_LIB_OUT=os.path.join(LIB_DIR, 'computador8bits.pretty'))
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-4000:])
            raise SystemExit(f'falha na PCB {b.key}')
        st = json.loads(r.stdout.strip().splitlines()[-1])
        for ext in ('.dsn', '.ses', '.kicad_prl'):
            p = os.path.join(kd, b.folder + ext)
            if os.path.exists(p):
                os.remove(p)
        if route:
            drc_src = os.path.join(kd, b.folder + '-drc.rpt')
            if os.path.exists(drc_src):
                os.replace(drc_src, os.path.join(fd, 'relatorio-drc.txt'))
            r = subprocess.run(['/usr/bin/python3', '-c',
                                f'import sys; sys.path.insert(0, {HERE!r}); import fabricacao; '
                                f'fabricacao.export_all({os.path.join(kd, b.folder + ".kicad_pcb")!r}, {fd!r}, {b.folder!r})'],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stderr[-3000:])
                raise SystemExit('falha exportando ' + b.key)
        st.update({'netlist_erros': len(errs), 'tempo_s': round(time.time() - t0, 1)})
        if errs:
            print('\n'.join(errs[:20]))
        print(json.dumps(st), flush=True)
        report.append(st)
    json.dump(report, open(os.path.join('/tmp', 'relatorio-geracao.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
