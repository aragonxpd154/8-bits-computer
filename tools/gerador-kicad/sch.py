"""Gera esquematicos KiCad 7 (.kicad_sch) a partir de designs.py.
Ligacoes feitas por rotulos de rede (net labels) em cada pino."""
import uuid, datetime
import symlib
from symlib import _f, G

AUTHOR = 'Marcos Silva dos Santos'
NICK = 'MarcosObel'
COMPANY = 'Zutup All Electronics'
REPO = 'github.com/aragonxpd154/8-bits-computer'
DATE = '2026-11-01'

PAPERS = [('A4', 297, 210), ('A3', 420, 297), ('A2', 594, 420), ('A1', 841, 594)]


def U():
    return str(uuid.uuid4())


def disp_len(name):
    return len(name.replace('~{', '').replace('}', ''))


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


class SchWriter:
    def __init__(self, board, lib, project):
        self.b, self.L, self.project = board, lib, project
        self.root = U()
        self.items = []
        self.sym_uuid = {}
        self.pwr_n = 0
        self.used_syms = set()

    # ------------------------------------------------------------------
    def extents(self, comp):
        s = self.L[comp.sym]
        xmin, ymin, xmax, ymax = s.bbox  # y para cima
        # converte para coordenadas do esquema (y para baixo) relativas a origem
        ex = [xmin, -ymax, xmax, -ymin]
        ex[1] -= 4.5  # referencia
        ex[3] += 4.5  # valor
        for p in s.pins:
            net = comp.pins.get(p.num)
            px, py = p.x, -p.y
            if net in ('+5V', 'GND'):
                ext = G + 4.0
            elif net:
                ext = G + disp_len(net) * 1.27 + 2.0
            else:
                ext = 1.5
            if p.angle == 0:
                ex[0] = min(ex[0], px - ext)
            elif p.angle == 180:
                ex[2] = max(ex[2], px + ext)
            elif p.angle == 90:
                ex[3] = max(ex[3], py + ext)
            else:
                ex[1] = min(ex[1], py - ext)
        return ex

    def layout(self):
        order = {'IC': 0, 'J': 1, 'PWRIN': 2, 'SW': 3, 'R': 4, 'LED': 5, 'C': 6}
        comps = sorted(self.b.comps.values(), key=lambda c: (order.get(c.group, 9), _natkey(c.ref)))
        lines = [self.b.desc, '', 'Revisao 3.0 (KiCad):'] + [' - ' + ch for ch in self.b.changes]
        for paper, W, H in PAPERS:
            nl = sum(len(_wrap(l, int((W - 40) / 1.45)).split('\n')) for l in lines)
            notes_h = 6 + nl * 2.75
            pos = {}
            x0, y0 = 20.0, 20.0 + notes_h
            xmax = W - 15
            ymax = H - 40
            x, y, rowh = x0, y0, 0
            ok = True
            last_group = None
            for c in comps:
                ex = self.extents(c)
                w, h = ex[2] - ex[0], ex[3] - ex[1]
                grp = order.get(c.group, 9)
                if last_group is not None and grp != last_group and grp <= 2 and x > x0:
                    x, y, rowh = x0, y + rowh + 4, 0
                last_group = grp
                if x + w > xmax:
                    x, y, rowh = x0, y + rowh + 4, 0
                ox = x - ex[0]
                oy = y - ex[1]
                ox = round(ox / G) * G
                oy = round(oy / G) * G
                if oy + ex[3] > ymax:
                    ok = False
                    break
                pos[c.ref] = (ox, oy)
                x += w + 3.5
                rowh = max(rowh, h)
            if ok:
                return paper, W, H, pos
        raise RuntimeError(f'{self.b.key}: nao coube nem em A1')

    # ------------------------------------------------------------------
    def place_symbol(self, libsym, ref, value, x, y, angle=0, footprint='', fields=None, hide_ref=False):
        self.used_syms.add(libsym.name)
        uid = U()
        lid = f'{symlib.LIBNAME}:{libsym.name}'
        rx, ry = libsym.ref_pos
        vx, vy = libsym.val_pos
        hr = ' hide' if hide_ref else ''
        o = [f'(symbol (lib_id "{lid}") (at {_f(x)} {_f(y)} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no)',
             f'(uuid {uid})',
             f'(property "Reference" "{ref}" (at {_f(x + rx)} {_f(y - ry)} 0) (effects (font (size 1.27 1.27)){hr}))',
             f'(property "Value" "{esc(value)}" (at {_f(x + vx)} {_f(y - vy)} 0) (effects (font (size 1.27 1.27))))',
             f'(property "Footprint" "{footprint}" (at {_f(x)} {_f(y)} 0) (effects (font (size 1.27 1.27)) hide))',
             f'(property "Datasheet" "" (at {_f(x)} {_f(y)} 0) (effects (font (size 1.27 1.27)) hide))']
        for k, v in (fields or {}).items():
            o.append(f'(property "{k}" "{esc(v)}" (at {_f(x)} {_f(y)} 0) (effects (font (size 1.27 1.27)) hide))')
        for p in libsym.pins:
            o.append(f'(pin "{p.num}" (uuid {U()}))')
        o.append(f'(instances (project "{self.project}" (path "/{self.root}" (reference "{ref}") (unit 1))))')
        o.append(')')
        self.items.append(' '.join(o))
        return uid

    def power(self, name, x, y, angle):
        self.pwr_n += 1
        s = self.L[name]
        ref = f'#PWR{self.pwr_n:03d}' if name != 'PWR_FLAG' else f'#FLG{self.pwr_n:03d}'
        self.place_symbol(s, ref, name, x, y, angle, hide_ref=True)

    def wire(self, x1, y1, x2, y2):
        self.items.append(f'(wire (pts (xy {_f(x1)} {_f(y1)}) (xy {_f(x2)} {_f(y2)})) '
                          f'(stroke (width 0) (type default)) (uuid {U()}))')

    def label(self, name, x, y, angle):
        just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[angle]
        self.items.append(f'(label "{name}" (at {_f(x)} {_f(y)} {angle}) (fields_autoplaced) '
                          f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}))')

    def noconn(self, x, y):
        self.items.append(f'(no_connect (at {_f(x)} {_f(y)}) (uuid {U()}))')

    def text(self, t, x, y, size=1.5, bold=False):
        b = ' bold' if bold else ''
        self.items.append(f'(text "{esc(t)}" (at {_f(x)} {_f(y)} 0) (effects (font (size {size} {size}){b}) '
                          f'(justify left top)) (uuid {U()}))')

    # ------------------------------------------------------------------
    def build(self):
        paper, W, H, pos = self.layout()
        self.paper = paper
        flag_done = set()
        for c in self.b.comps.values():
            s = self.L[c.sym]
            X, Y = pos[c.ref]
            fp = c.fp or s.footprint
            fields = {}
            if c.pinlabels:
                fields['Pinagem'] = ' | '.join(f'{i+1}:{n}' for i, n in enumerate(c.pinlabels))
            self.sym_uuid[c.ref] = self.place_symbol(s, c.ref, c.value, X, Y, 0, fp, fields)
            done_pwr = set()
            for p in s.pins:
                net = c.pins.get(p.num)
                px, py = X + p.x, Y - p.y
                d = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[p.angle]
                if net is None:
                    self.noconn(px, py)
                    continue
                L = G
                ex, ey = px + d[0] * L, py + d[1] * L
                self.wire(px, py, ex, ey)
                if net in ('+5V', 'GND'):
                    if p.num in done_pwr:
                        continue
                    if p.angle in (0, 180):
                        # agrupa pinos vizinhos do mesmo lado com a mesma rede de alimentacao
                        side = sorted([q for q in s.pins if q.angle == p.angle], key=lambda q: -q.y)
                        idx = [q.num for q in side].index(p.num)
                        run = [p]
                        for q in side[idx + 1:]:
                            if abs(run[-1].y - q.y - G) < 0.01 and c.pins.get(q.num) == net:
                                run.append(q)
                            else:
                                break
                        for q in run:
                            done_pwr.add(q.num)
                        if len(run) > 1:
                            ylast = Y - run[-1].y
                            ys = [Y - q.y for q in run]
                            for ya, yb in zip(ys, ys[1:]):
                                self.wire(ex, ya, ex, yb)
                            for yj in ys[1:-1]:
                                self.items.append(f'(junction (at {_f(ex)} {_f(yj)}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
                            if net == 'GND':
                                ey = ylast
                    if net == '+5V':
                        ang = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}[d]
                    else:
                        ang = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}[d]
                    self.power(net, ex, ey, ang)
                else:
                    ang = {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[d]
                    self.label(net, ex, ey, ang)
        # PWR_FLAG (para o ERC do KiCad): +5V e GND
        fx, fy = 22.86, round((H - 24) / G) * G
        self.power('PWR_FLAG', fx, fy, 180); self.power('+5V', fx, fy, 0)
        self.power('PWR_FLAG', fx + 12.7, fy, 0); self.power('GND', fx + 12.7, fy, 0)
        # texto de cabecalho
        t = f'{self.b.title}  -  Computador 8 Bits v{self.b.rev}'
        self.text(t, 20, 12, 3.0, True)
        lines = [self.b.desc, '', 'Revisao 3.0 (KiCad):'] + [' - ' + ch for ch in self.b.changes]
        self.text('\n'.join(_wrap(l, int((W - 40) / 1.45)) for l in lines), 20, 18, 1.6)
        self.text(f'Autor: {AUTHOR} ({NICK})  -  {REPO}  -  Licenca GPL-3.0', 20, H - 14, 1.6)
        return paper

    def write(self, path):
        paper = self.build()
        o = ['(kicad_sch (version 20230121) (generator eeschema)', f'(uuid {self.root})', f'(paper "{paper}")',
             '(title_block', f'(title "{esc(self.b.title)}")', f'(date "{DATE}")', f'(rev "{self.b.rev}")',
             f'(company "{COMPANY}")', f'(comment 1 "Autor: {AUTHOR} ({NICK})")', f'(comment 2 "{REPO}")',
             '(comment 3 "Licenca GPL-3.0 - Computador 8 Bits sem microcontrolador")',
             f'(comment 4 "Placa: {self.b.key}")', ')', '(lib_symbols']
        for name in sorted(self.used_syms | {'PWR_FLAG'}):
            o.append('  ' + self.L[name].sexpr(symlib.LIBNAME))
        o.append(')')
        o += self.items
        o.append('(sheet_instances (path "/" (page "1")))')
        o.append(')')
        with open(path, 'w') as f:
            f.write('\n'.join(o) + '\n')


def _wrap(s, n):
    words, lines, cur = s.split(' '), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = '   ' + w
        else:
            cur = (cur + ' ' + w) if cur else w
    lines.append(cur)
    return '\n'.join(lines)


def _natkey(s):
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]
