"""Verifica se a netlist exportada pelo KiCad bate exatamente com designs.py."""
import re


def parse_kicad_net(path):
    t = open(path).read()
    nets = {}
    for m in re.finditer(r'\(net \(code "\d+"\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', t, re.S):
        name = m.group(1)
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))
        nets[name] = {(r, p) for r, p in nodes}
    return nets


def norm(name):
    return name[1:] if name.startswith('/') else name


def design_partition(board):
    nets = {}
    for c in board.comps.values():
        for p, n in c.pins.items():
            if n:
                nets.setdefault(n, set()).add((c.ref, p))
    return nets


def compare(board, kicad_nets):
    """Retorna lista de erros (vazia = ok)."""
    errs = []
    want = design_partition(board)
    got = {}
    for n, nodes in kicad_nets.items():
        nodes = {x for x in nodes if not x[0].startswith('#')}
        if not nodes:
            continue
        got[norm(n)] = nodes
    # pinos sem conexao viram redes unconnected-(...) no KiCad
    got = {k: v for k, v in got.items() if not k.startswith('unconnected-') and not k.startswith('Net-(')
           or len(v) > 1}
    for n, nodes in want.items():
        if n not in got:
            errs.append(f'rede {n} ausente no KiCad')
        elif got[n] != nodes:
            errs.append(f'rede {n}: faltando {sorted(nodes - got[n])} sobrando {sorted(got[n] - nodes)}')
    for n in got:
        if n not in want:
            errs.append(f'rede extra no KiCad: {n} {sorted(got[n])}')
    return errs
