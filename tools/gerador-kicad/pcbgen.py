"""Gera as PCBs (KiCad 7) do Computador 8 Bits: posicionamento, autorroteamento (Freerouting),
importacao das trilhas, DRC.  Executar com o python do sistema que tem o modulo pcbnew:
    /usr/bin/python3 pcbgen.py <PLACA> <pasta_saida>
Autor do projeto: Marcos Silva dos Santos (MarcosObel)."""
import os, re, sys, json, subprocess, math
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designs, symlib, layouts

FPDIR = os.environ.get('KICAD7_FOOTPRINT_DIR', '/usr/share/kicad/footprints')
FREEROUTING = os.environ.get('FREEROUTING_JAR', os.path.join(HERE, 'freerouting-2.0.1.jar'))
MM = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(MM(x), MM(y))

TRACK, POWER_TRACK, CLEAR, VIA_D, VIA_DRILL = 0.5, 0.9, 0.4, 1.6, 0.8
POWER_NETS = {'+5V', 'GND', 'VIN', 'VSW'}


# ---------------------------------------------------------------------------
def make_seg4(board):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID('computador8bits', 'Display_7seg_4dig_0.4in'))
    pitch, row = 2.54, 12.70
    for i in range(6):
        for num, y in ((i + 1, row / 2), (12 - i, -row / 2)):
            p = pcbnew.PAD(fp)
            p.SetNumber(str(num))
            p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            p.SetShape(pcbnew.PAD_SHAPE_RECT if num == 1 else pcbnew.PAD_SHAPE_CIRCLE)
            p.SetSize(V(1.8, 1.8))
            p.SetDrillSize(V(0.9, 0.9))
            p.SetPos0(V(-6.35 + i * pitch, y))
            p.SetPosition(V(-6.35 + i * pitch, y))
            ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
            ls.AddLayer(pcbnew.F_Mask); ls.AddLayer(pcbnew.B_Mask)
            p.SetLayerSet(ls)
            fp.Add(p)
    for p in fp.Pads():
        pass
    for layer, (w, h) in ((pcbnew.F_SilkS, (40.4, 16.0)), (pcbnew.F_CrtYd, (40.9, 16.5))):
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        for k in range(4):
            r = pcbnew.FP_SHAPE(fp, pcbnew.SHAPE_T_SEGMENT)
            r.SetStart0(V(*pts[k])); r.SetEnd0(V(*pts[(k + 1) % 4]))
            r.SetLayer(layer); r.SetWidth(MM(0.12))
            fp.Add(r)
    fp.SetPosition(V(0, 0))
    fp.Reference().SetText('DS**'); fp.Value().SetText('Display_7seg_4dig_0.4in')
    lib = os.environ.get('FP_LIB_OUT')
    if lib:
        if not os.path.isdir(lib):
            pcbnew.FootprintLibCreate(lib)
        pcbnew.FootprintSave(lib, fp)
    return fp


def load_fp(board, libname):
    lib, name = libname.split(':')
    if lib == 'computador8bits':
        return make_seg4(board)
    fp = pcbnew.FootprintLoad(f'{FPDIR}/{lib}.pretty', name)
    if fp is None:
        raise RuntimeError('footprint nao encontrado: ' + libname)
    return fp


def home_fab_pads(fp, libname, dual=False):
    """Pads THT somente na face de baixo (B.Cu): toda ligacao com a face de cima passa por via
    -> placa dupla face caseira sem furo metalizado e sem soldar componente por cima."""
    big = any(k in libname for k in ('R_Axial', 'C_Disc', 'CP_Radial', 'C_Rect'))
    pads = list(fp.Pads())
    mind = min([math.hypot(pcbnew.ToMM(a.GetPosition().x - b.GetPosition().x),
                           pcbnew.ToMM(a.GetPosition().y - b.GetPosition().y))
                for i, a in enumerate(pads) for b in pads[i + 1:]] + [99])
    newsize = min(2.0, mind - 0.6)
    for pad in fp.Pads():
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
            continue
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.B_Mask)
        if dual == 'full':
            ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.F_Mask)
        elif dual and any(k in libname for k in ('R_Axial', 'C_Disc', 'CP_Radial', 'LED_THT')):
            ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.F_Mask)
        pad.SetLayerSet(ls)
        if big and newsize > pcbnew.ToMM(pad.GetSize().x):
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(V(newsize, newsize))


def fp_bbox(fp):
    bb = fp.GetBoundingBox(False, False)
    return (pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def pad_of(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == str(num):
            return p
    return None


def fix_dsn(txt):
    """Coloca as redes de alimentacao na classe Power (trilha larga) do arquivo Specctra."""
    i = txt.index('(class kicad_default ""')
    j = txt.index('(circuit', i)
    head = txt[i + len('(class kicad_default ""'):j]
    toks = re.findall(r'"[^"]*"|[^\s]+', head)
    keep = [t for t in toks if t.strip('"') not in POWER_NETS]
    pw = [t for t in toks if t.strip('"') in POWER_NETS]
    txt = txt[:i] + '(class kicad_default "" ' + ' '.join(keep) + '\n      ' + txt[j:]
    if '(class Power' in txt:
        txt = txt.replace('(class Power', '(class Power ' + ' '.join(pw), 1)
    return txt


def add_hole_keepouts(txt, board):
    """Na face de cima nao existe pad: impede trilhas F.Cu sobre os furos (keepout circular por pad)."""
    ko = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                continue
            sz = max(pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y), pcbnew.ToMM(p.GetDrillSize().x) + 0.6)
            x, y = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
            ko.append(f'    (wire_keepout "" (circle F.Cu {sz*1000:.0f} {x*1000:.1f} {-y*1000:.1f}))')
    i = txt.index('(boundary')
    return txt[:i] + '\n'.join(ko) + '\n    ' + txt[i:]


def shrink_boundary(txt, d=1.5):
    """Afasta as trilhas da borda da placa (d mm) encolhendo o contorno do Specctra."""
    m = re.search(r'\(boundary\s*\(path pcb 0\s+([-\d.\s]+)\)', txt)
    v = [float(x) for x in m.group(1).split()]
    xs, ys = v[0::2], v[1::2]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    du = d * 1000
    nv = []
    for x, y in zip(xs, ys):
        nv += [x + (du if x < cx else -du), y + (du if y < cy else -du)]
    new = ' '.join(f'{c:.1f}' for c in nv)
    return txt[:m.start(1)] + new + txt[m.end(1):]


def set_rules(board):
    ds = board.GetDesignSettings()
    ns = ds.m_NetSettings
    d = ns.m_DefaultNetClass
    for nc, tw in ((d, TRACK),):
        nc.SetClearance(MM(CLEAR)); nc.SetTrackWidth(MM(tw)); nc.SetViaDiameter(MM(VIA_D)); nc.SetViaDrill(MM(VIA_DRILL))
    pnc = pcbnew.NETCLASS('Power')
    pnc.SetClearance(MM(CLEAR)); pnc.SetTrackWidth(MM(POWER_TRACK)); pnc.SetViaDiameter(MM(VIA_D))
    pnc.SetViaDrill(MM(VIA_DRILL))
    ns.m_NetClasses['Power'] = pnc
    for name, net in board.GetNetsByName().items():
        if str(name) in POWER_NETS:
            net.SetNetClass(pnc)
    ds.m_MinClearance = MM(0.3)
    ds.m_TrackMinWidth = MM(0.4)
    ds.m_ViasMinSize = MM(1.2)
    ds.m_MinThroughDrill = MM(0.6)
    ds.m_CopperEdgeClearance = MM(0.5)
    ds.m_HoleClearance = MM(0.25)
    ds.m_HoleToHoleMin = MM(0.5)
    ds.m_ViasMinAnnularWidth = MM(0.25)


def patch_pro(path):
    """Acrescenta ao .kicad_pro as regras que a API do KiCad 7 nao expoe (padroes de classe de rede)."""
    pro = json.load(open(path))
    nset = pro.setdefault('net_settings', {})
    classes = nset.setdefault('classes', [])
    if not any(c.get('name') == 'Power' for c in classes):
        base = dict(classes[0]) if classes else {}
        base.update({'name': 'Power', 'track_width': POWER_TRACK, 'clearance': CLEAR, 'via_diameter': VIA_D,
                     'via_drill': VIA_DRILL})
        classes.append(base)
    for c in classes:
        if c.get('name') == 'Default':
            c.update({'track_width': TRACK, 'clearance': CLEAR, 'via_diameter': VIA_D, 'via_drill': VIA_DRILL})
    nset['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in sorted(POWER_NETS)]
    dsg = pro.setdefault('board', {}).setdefault('design_settings', {})
    sev = dsg.setdefault('rule_severities', {})
    for k in ('silk_overlap', 'silk_over_copper', 'silk_edge_clearance', 'lib_footprint_issues',
              'lib_footprint_mismatch', 'text_height', 'text_thickness'):
        sev[k] = 'ignore'
    dsg['track_widths'] = [0.0, TRACK, POWER_TRACK, 1.5]
    dsg['via_dimensions'] = [{'diameter': 0.0, 'drill': 0.0}, {'diameter': VIA_D, 'drill': VIA_DRILL}]
    pro.setdefault('text_variables', {})['AUTOR'] = 'Marcos Silva dos Santos'
    json.dump(pro, open(path, 'w'), indent=2)


# ---------------------------------------------------------------------------
class PCBBuilder:
    def __init__(self, board_def, outdir, sym_uuids=None):
        self.d = board_def
        self.out = outdir
        self.name = board_def.folder
        self.board = pcbnew.BOARD()
        self.fps = {}
        self.sym_uuids = sym_uuids or {}
        self.L = symlib.build_library()

    def nets(self):
        self.netinfo = {}
        for n in sorted(self.d.nets()):
            ni = pcbnew.NETINFO_ITEM(self.board, n)
            self.board.Add(ni)
            self.netinfo[n] = ni

    def create_fps(self):
        for c in self.d.comps.values():
            libname = c.fp or self.L[c.sym].footprint
            fp = load_fp(self.board, libname)
            home_fab_pads(fp, libname, layouts.PARAMS.get(self.d.key, {}).get('dual', 'full'))
            fp.SetReference(c.ref)
            fp.SetValue(c.value.split(' (')[0])
            v = fp.Value()
            if c.group in ('IC', 'R', 'C') or c.sym in ('SW_Push', 'SW_SPDT', 'POT', 'Polyfuse', 'D'):
                v.SetLayer(pcbnew.F_SilkS)
                v.SetVisible(True)
                sz = 1.0 if c.group == 'IC' else 0.75
                v.SetTextSize(V(sz, sz)); v.SetTextThickness(MM(sz * 0.15))
            else:
                v.SetVisible(False)
            fp.Reference().SetTextSize(V(1.0, 1.0))
            fp.Reference().SetTextThickness(MM(0.15))
            if c.ref in self.sym_uuids:
                fp.SetPath(pcbnew.KIID_PATH('/' + self.sym_uuids[c.ref]))
            self.board.Add(fp)
            for pad in fp.Pads():
                net = c.pins.get(pad.GetNumber())
                if net:
                    pad.SetNet(self.netinfo[net])
            self.fps[c.ref] = fp

    # -------------------- posicionamento -------------------------------
    def place_at(self, ref, x, y, rot):
        fp = self.fps[ref]
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(V(0, 0))
        bb = fp_bbox(fp)
        fp.SetPosition(V(x - bb[0], y - bb[1]))
        return fp_bbox(fp)

    def unit_size(self, refs_rots):
        """mede largura/altura de um conjunto (posicionado temporariamente)"""
        pass

    def default_rot(self, c):
        lib = c.fp or self.L[c.sym].footprint
        if 'Package_DIP' in lib or 'PinHeader' in lib:
            return 90
        return 0

    def ic_caps(self, ics):
        caps = [c.ref for c in self.d.comps.values() if c.group == 'C' and c.value == '100nF'
                and set(c.pins.values()) == {'+5V', 'GND'}]
        caps.sort(key=lambda r: int(r[1:]))
        return dict(zip(ics, caps))

    def led_pairs(self):
        pairs = []
        for c in self.d.comps.values():
            if c.group != 'LED':
                continue
            nets = {n for n in c.pins.values() if n not in POWER_NETS}
            r = None
            for rc in self.d.comps.values():
                if rc.group == 'R' and rc.sym == 'R' and nets & set(rc.pins.values()):
                    shared = (nets & set(rc.pins.values())).pop()
                    if shared.startswith('L'):
                        r = (rc.ref, shared)
            pairs.append((c.ref, r))
        return pairs

    def layout(self):
        rows = layouts.LAYOUTS[self.d.key]
        if rows is None:
            return self.layout_backplane()
        all_ics = [r for row in rows if isinstance(row, list) for r in row
                   if r.startswith('U') and self.d.comps[r].group == 'IC']
        capmap = self.ic_caps(all_ics)
        used = set(capmap.values())
        prm = layouts.PARAMS.get(self.d.key, {})
        margin_x, top, gap_row = 6.0, 10.0, prm.get('gap_row', 7.0)
        placed_rows = []
        y = top
        self.rowrot = {}
        for row in rows:
            items = []
            if isinstance(row, dict):
                for r in row['refs']:
                    rot = row['rot']
                    if isinstance(rot, dict):
                        if r in rot:
                            self.rowrot[r] = rot[r]
                    else:
                        self.rowrot[r] = rot
                row = row['refs']
            if row == 'LEDS':
                pairs = [p for p in self.led_pairs() if p[0] not in used and (p[1] is None or p[1][0] not in used)]
                for led, r in pairs:
                    used.add(led)
                    if r:
                        used.add(r[0])
                    items.append(('ledpair', led, r))
            else:
                for ref in row:
                    used.add(ref)
                    items.append(('ic', ref, capmap.get(ref)) if ref in capmap else ('one', ref, None))
            placed_rows.append(items)
        rest = [c.ref for c in self.d.comps.values() if c.ref not in used]
        if rest:
            placed_rows.append([('one', r, None) for r in rest])
        # posiciona em x=0 cada linha e mede
        widths, heights, geo = [], [], []
        for items in placed_rows:
            x, h, g = 0.0, 0.0, []
            is_hdr = all(self.d.comps[it[1]].group == 'J' for it in items)
            gap = 6.0 if is_hdr else (prm.get('ic_gap', 4.5) if items and items[0][0] == 'ic' else 2.5)
            if items and items[0][0] == 'ledpair':
                gap = 2.4
            for kind, ref, extra in items:
                c = self.d.comps[ref]
                if kind == 'ic':
                    cb = self.place_at(extra, x, 0, 270)
                    ib = self.place_at(ref, cb[2] + 1.2, 0, self.default_rot(c))
                    # centraliza o capacitor verticalmente no CI
                    cy = (ib[1] + ib[3]) / 2 - (cb[3] - cb[1]) / 2
                    cb = self.place_at(extra, x, cy, 270)
                    w = ib[2] - x
                    h = max(h, ib[3] - min(ib[1], cb[1]))
                    g.append((kind, ref, extra, x, w))
                elif kind == 'ledpair':
                    lb = self.place_at(ref, x, 0, 0)
                    if extra:
                        rref, shared = extra
                        rc = self.d.comps[rref]
                        rot = 270 if rc.pins['1'] == shared else 90
                        lp = pad_of(self.fps[ref], [k for k, v in c.pins.items() if v == shared][0])
                        lx = pcbnew.ToMM(lp.GetPosition().x)
                        rb = self.place_at(rref, 0, lb[3] + 1.5, rot)
                        rp = pad_of(self.fps[rref], [k for k, v in rc.pins.items() if v == shared][0])
                        dx = lx - pcbnew.ToMM(rp.GetPosition().x)
                        self.fps[rref].Move(V(dx, 0))
                        rb = fp_bbox(self.fps[rref])
                        w = max(lb[2], rb[2]) - x
                        h = max(h, rb[3])
                    else:
                        w = lb[2] - x
                        h = max(h, lb[3])
                    g.append((kind, ref, extra, x, w))
                else:
                    b = self.place_at(ref, x, 0, self.rowrot.get(ref, self.default_rot(c)))
                    w = b[2] - x
                    h = max(h, b[3] - b[1])
                    g.append((kind, ref, extra, x, w))
                x += w + gap
            widths.append(x - gap)
            heights.append(h)
            geo.append(g)
        W = max(widths) + 2 * margin_x
        W = max(W, 60)
        # desloca linhas para a posicao final (centralizadas)
        y = top
        for i, g in enumerate(geo):
            off = (W - widths[i]) / 2
            is_hdr = all(self.d.comps[it[1]].group == 'J' for it in g)
            for kind, ref, extra, x, w in g:
                refs = [ref]
                if kind == 'ic' and extra:
                    refs.append(extra)
                if kind == 'ledpair' and extra:
                    refs.append(extra[0])
                for r in refs:
                    self.fps[r].Move(V(off, y))
            if is_hdr:
                self.header_labels(g)
            y += heights[i] + (gap_row + 3.0 if is_hdr else gap_row)
        H = y - gap_row + 9.0
        self.W, self.H = W, H
        self.led_labels()
        for ref, texto in layouts.NOTAS.get(self.d.key, []):
            bb = fp_bbox(self.fps[ref])
            self.silk(texto, (bb[0] + bb[2]) / 2, bb[1] - 1.4, 0.9)

    def led_labels(self):
        """Escreve na serigrafia qual sinal cada LED mostra (didatico)."""
        for c in self.d.comps.values():
            if c.group != 'LED':
                continue
            a, k = c.pins.get('2'), c.pins.get('1')
            lab = a if a and not a.startswith('L') and a not in POWER_NETS else k
            if not lab or lab in POWER_NETS or lab.startswith('L'):
                continue
            lab = lab.replace('~{S', 'T').replace('~{', '/').replace('}', '').replace('/SW_PROG', 'PROG').replace('/SW_RUN', 'RUN')
            bb = fp_bbox(self.fps[c.ref])
            self.silk(lab, (bb[0] + bb[2]) / 2, bb[1] - 1.0, 0.8, bold=True)
            self.fps[c.ref].Reference().SetVisible(False)

    def header_labels(self, g):
        for kind, ref, extra, x, w in g:
            c = self.d.comps[ref]
            fp = self.fps[ref]
            bb = fp_bbox(fp)
            self.silk(c.value, (bb[0] + bb[2]) / 2, bb[1] - 1.3, 0.9)
            for k, lab in enumerate(c.pinlabels or []):
                p = pad_of(fp, k + 1)
                px, py = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
                self.silk(lab, px, bb[3] + 0.6 + len(lab) * 0.36, 0.7, angle=90)
            fp.Reference().SetVisible(False)

    def layout_backplane(self):
        """Backplane: conectores agrupados por modulo, em duas colunas (como os modulos ficam na base)."""
        d = self.d
        heads = {c.value: c for c in d.comps.values() if c.group == 'J' and c.sym == 'Conn_01x04'}

        def mod(v):
            if v.startswith('CD_'):
                return 'CD'
            if v == 'EXPANSAO':
                return 'EXPANSAO'
            m = v.split('_', 1)[1]
            return m.rstrip('12') if m.startswith(('PC', 'RAM', 'ALU')) else m
        grupos = {}
        for v in [x[0] for x in designs.BACKPLANE_HEADERS]:
            grupos.setdefault(mod(v), []).append(heads[v])
        nomes = {'CLOCK': 'CLOCK', 'RESET': 'RESET', 'PC': 'PC', 'RAM': 'RAM/MAR', 'IR': 'IR', 'CD': 'CONTROLE',
                 'FETCH': 'PASSOS', 'ACC': 'REG. A', 'ALU': 'ULA', 'B': 'REG. B', 'OUT': 'SAIDA',
                 'DISPLAY': 'DISPLAY', 'EXPANSAO': 'EXPANSAO'}
        colunas = [['CLOCK', 'RESET', 'PC', 'RAM', 'IR', 'CD', 'FETCH'],
                   ['ACC', 'ALU', 'B', 'OUT', 'DISPLAY', 'EXPANSAO']]
        # energia + LEDs do barramento no topo
        x0, y0 = 8.0, 12.0
        x = x0
        for ref in ['J1', 'J2', 'SW1', 'F1', 'D1', 'C1', 'C2', 'LED1', 'R1']:
            b = self.place_at(ref, x, y0, 0)
            x = b[2] + 3.5
        self.silk('ENTRADA 5 V (fonte regulada 5 V / 2 A ou mais)', x0 + 30, y0 - 2.4, 1.0)
        ledx = x + 3
        for i in range(8):
            led, r = f'LED{2+i}', f'R{2+i}'
            lb = self.place_at(led, ledx + i * 5.08, y0, 0)
            self.place_at(r, 0, lb[3] + 1.5, 270)
            lp = pad_of(self.fps[led], 1)
            rp = pad_of(self.fps[r], 1)
            self.fps[r].Move(V(pcbnew.ToMM(lp.GetPosition().x - rp.GetPosition().x), 0))
            self.silk(f'D{7-i}', ledx + i * 5.08 + 1.27, y0 - 1.4, 0.8)
            self.fps[led].Reference().SetVisible(False)
        self.silk('BARRAMENTO', ledx + 19, y0 - 3.2, 1.0)
        top = y0 + 25.0
        pitch_h, pitch_v, lab_w = 13.5, 16.0, 17.0
        colx = x0
        maxy = top
        g = []
        for col in colunas:
            largura = max(len(grupos[m]) for m in col) * pitch_h + lab_w
            for ri, m in enumerate(col):
                y = top + ri * pitch_v
                self.silk(nomes[m], colx + lab_w / 2 - 1, y + 1.3, 1.3, bold=True)
                for hi, h in enumerate(grupos[m]):
                    self.place_at(h.ref, colx + lab_w + hi * pitch_h, y, 90)
                    g.append(('one', h.ref, None, 0, 0))
                maxy = max(maxy, y + pitch_v)
            colx += largura + 6
        self.header_labels(g)
        self.W = max(colx + 2, ledx + 48)
        self.H = maxy + 4

    # -------------------- graficos -------------------------------------
    def silk(self, txt, x, y, size, angle=0, layer=pcbnew.F_SilkS, mirror=False, bold=False):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(txt)
        t.SetPosition(V(x, y))
        t.SetLayer(layer)
        t.SetTextSize(V(size, size))
        t.SetTextThickness(MM(size * (0.2 if bold else 0.15)))
        t.SetTextAngleDegrees(angle)
        if mirror:
            t.SetMirrored(True)
        self.board.Add(t)
        return t

    def outline(self):
        W, H = self.W, self.H
        pts = [(0, 0), (W, 0), (W, H), (0, H)]
        for i in range(4):
            s = pcbnew.PCB_SHAPE(self.board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(V(*pts[i])); s.SetEnd(V(*pts[(i + 1) % 4]))
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.15))
            self.board.Add(s)
        for i, (x, y) in enumerate(((3.5, 3.5), (W - 3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5))):
            fp = pcbnew.FootprintLoad(f'{FPDIR}/MountingHole.pretty', 'MountingHole_3.2mm_M3')
            fp.SetReference(f'H{i+1}'); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
            fp.SetPosition(V(x, y))
            self.board.Add(fp)
        self.silk(f'{self.d.title} - v{self.d.rev}', W / 2, 4.2, 1.5, bold=True)
        self.silk('Computador 8 Bits - Marcos Silva dos Santos - GPL-3.0', W / 2, H - 2.2, 1.0)
        # texto no cobre (lado de baixo, espelhado) - fica gravado na placa caseira
        self.copper_txt = (f'8BITS {self.d.key} v{self.d.rev} - M.S.SANTOS', W / 2, H - 4.6)
        self.keepout(6, H - 6.2, W - 6, H - 3.0)
        tw = len(f'{self.d.title} - v{self.d.rev}') * 1.25 / 2 + 2
        self.keepout(W / 2 - tw, 2.6, W / 2 + tw, 5.8)
        # textos auxiliares de impressao (camada Cmts.User): titulo e regua de 50 mm
        self.silk(f'{self.d.title} v{self.d.rev} - Marcos Silva dos Santos - IMPRIMIR EM 100% (tamanho real)',
                  0, -6, 1.6, layer=pcbnew.Cmts_User).SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        y = H + 6
        for x1, x2, yy in ((0, 50, y), (0, 0, y - 1.5), (50, 50, y - 1.5), (10, 10, y - 0.8), (20, 20, y - 0.8),
                           (30, 30, y - 0.8), (40, 40, y - 0.8)):
            seg = pcbnew.PCB_SHAPE(self.board)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(V(x1, y)); seg.SetEnd(V(x2, yy if x1 != x2 else yy))
            if x1 == x2:
                seg.SetStart(V(x1, y)); seg.SetEnd(V(x1, yy))
            seg.SetLayer(pcbnew.Cmts_User); seg.SetWidth(MM(0.25))
            self.board.Add(seg)
        self.silk('REGUA DE CONFERENCIA: 50 mm', 25, y + 2.5, 1.4, layer=pcbnew.Cmts_User)

    def shift_all(self, dx, dy):
        for fp in self.board.GetFootprints():
            fp.Move(V(dx, dy))
        for d in self.board.GetDrawings():
            d.Move(V(dx, dy))
        for z in self.board.Zones():
            z.Move(V(dx, dy))
        txt, x, y = self.copper_txt
        self.copper_txt = (txt, x + dx, y + dy)
        self.paper = 'A4' if (self.W < 250 and self.H < 165) else ('A3' if self.W < 375 and self.H < 250 else 'A2')

    def keepout(self, x1, y1, x2, y2):
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowCopperPour(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.F_Cu)
        z.SetLayerSet(ls)
        o = z.Outline(); o.NewOutline()
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            o.Append(MM(x), MM(y))
        self.board.Add(z)

    # -------------------- regras / projeto -------------------------------
    def write_project(self, path):
        cls = lambda name, tw: {"name": name, "clearance": CLEAR, "track_width": tw, "via_diameter": VIA_D,
                                "via_drill": VIA_DRILL, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                                "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
                                "line_style": 0, "wire_width": 6, "bus_width": 12,
                                "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}
        pro = {
            "board": {"design_settings": {
                "defaults": {"board_outline_line_width": 0.15, "copper_line_width": 0.2, "copper_text_size_h": 1.5,
                             "copper_text_size_v": 1.5, "copper_text_thickness": 0.3, "silk_line_width": 0.15,
                             "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {"min_clearance": 0.3, "min_track_width": 0.4, "min_via_diameter": 1.2,
                          "min_through_hole_diameter": 0.6, "min_hole_to_hole": 0.5, "min_copper_edge_clearance": 0.5,
                          "min_hole_clearance": 0.3, "min_via_annular_width": 0.3, "min_silk_clearance": 0.0},
                "track_widths": [0.0, TRACK, POWER_TRACK, 1.5],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": VIA_D, "drill": VIA_DRILL}],
                "rule_severities": {"silk_overlap": "ignore", "silk_over_copper": "ignore", "silk_edge_clearance": "ignore",
                                    "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore",
                                    "text_height": "ignore", "text_thickness": "ignore"},
            }},
            "meta": {"filename": os.path.basename(path), "version": 1},
            "net_settings": {"classes": [cls("Default", TRACK), cls("Power", POWER_TRACK)],
                             "meta": {"version": 3}, "net_colors": None, "netclass_assignments": None,
                             "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in sorted(POWER_NETS)]},
            "pcbnew": {"page_layout_descr_file": ""},
            "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
            "sheets": [], "text_variables": {"AUTOR": "Marcos Silva dos Santos"},
            "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        }
        with open(path, 'w') as f:
            json.dump(pro, f, indent=2)

    # -------------------- roteamento -------------------------------------
    def route(self, pcb_path):
        base = os.path.splitext(pcb_path)[0]
        dsn, ses = base + '.dsn', base + '.ses'
        board = pcbnew.LoadBoard(pcb_path)
        set_rules(board)
        ok = pcbnew.ExportSpecctraDSN(board, dsn)
        assert ok, 'falha exportando DSN'
        txt = shrink_boundary(add_hole_keepouts(fix_dsn(open(dsn).read()), board))
        open(dsn, 'w').write(txt)
        passes = os.environ.get('FR_PASSES', str(layouts.PARAMS.get(self.d.key, {}).get('passes', 100)))
        cmd = ['java', '-jar', FREEROUTING, '-de', dsn, '-do', ses, f'--router.max_passes={passes}', '-da',
               '--gui.enabled=false']
        for attempt in range(4):
            if os.path.exists(ses):
                os.remove(ses)
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=int(os.environ.get('FR_TIMEOUT', '1500')))
            except subprocess.TimeoutExpired:
                print('freerouting: tempo esgotado', file=sys.stderr)
                break
            if os.path.exists(ses) and os.path.getsize(ses) > 100:
                break
        if not os.path.exists(ses) or os.path.getsize(ses) < 100:
            print('freerouting sem resultado (tempo esgotado?)', file=sys.stderr)
            return board, 0
        n = self.import_ses(board, ses)
        pcbnew.SaveBoard(pcb_path, board)
        patch_pro(base + '.kicad_pro')
        set_paper(pcb_path, self.paper)
        return board, n

    def import_ses(self, board, ses):
        t = open(ses).read()
        m = re.search(r'\(resolution\s+(\w+)\s+(\d+)\)', t)
        unit, res = m.group(1), int(m.group(2))
        scale = {'um': 1e-3, 'mm': 1.0, 'mil': 0.0254, 'inch': 25.4}[unit] / res
        nets = {n.GetNetname(): n for n in board.GetNetsByName().values()} if False else None
        nb = board.GetNetsByName()
        layer = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
        count = 0
        net_out = t[t.index('(network_out'):]
        for nm in re.finditer(r'\(net\s+("(?:[^"\\]|\\.)*"|[^\s()]+)(.*?)(?=\(net\s|\Z)', net_out, re.S):
            name = nm.group(1).strip('"')
            body = nm.group(2)
            net = nb[name] if nb.has_key(name) else None
            if net is None:
                print('rede SES desconhecida', name)
                continue
            for w in re.finditer(r'\(path\s+(\S+)\s+([\d.]+)\s+([-\d.\s]+)\)', body):
                ly = layer[w.group(1)]
                width = float(w.group(2)) * scale
                c = [float(v) * scale for v in w.group(3).split()]
                pts = list(zip(c[0::2], c[1::2]))
                for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                    tr = pcbnew.PCB_TRACK(board)
                    tr.SetStart(V(x1, -y1)); tr.SetEnd(V(x2, -y2))
                    tr.SetWidth(MM(width)); tr.SetLayer(ly); tr.SetNet(net)
                    board.Add(tr)
                    count += 1
            for v in re.finditer(r'\(via\s+"?[^"\s]+"?\s+([-\d.]+)\s+([-\d.]+)', body):
                x, y = float(v.group(1)) * scale, float(v.group(2)) * scale
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(V(x, -y))
                via.SetDrill(MM(VIA_DRILL)); via.SetWidth(MM(VIA_D))
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                via.SetNet(net)
                board.Add(via)
        return count

    # -------------------- pipeline ---------------------------------------
    def build(self, route=True):
        os.makedirs(self.out, exist_ok=True)
        self.nets()
        self.create_fps()
        self.layout()
        self.outline()
        self.shift_all(20, 25)
        set_rules(self.board)
        pcb = os.path.join(self.out, self.name + '.kicad_pcb')
        pro = os.path.join(self.out, self.name + '.kicad_pro')
        tb = self.board.GetTitleBlock()
        tb.SetTitle(self.d.title); tb.SetRevision(self.d.rev); tb.SetDate('2026-11-01')
        tb.SetCompany('Zutup All Electronics')
        tb.SetComment(0, 'Autor: Marcos Silva dos Santos (MarcosObel)')
        tb.SetComment(1, 'github.com/aragonxpd154/8-bits-computer - GPL-3.0')
        tb.SetComment(2, 'Placa dupla face caseira: pads so na face inferior, vias = fio passante')
        pcbnew.SaveBoard(pcb, self.board)
        patch_pro(pro)
        set_paper(pcb, self.paper)
        stats = {'W': round(self.W, 1), 'H': round(self.H, 1)}
        if route:
            board, n = self.route(pcb)
            txt, x, y = self.copper_txt
            t = pcbnew.PCB_TEXT(board)
            t.SetText(txt); t.SetPosition(V(x, y)); t.SetLayer(pcbnew.B_Cu)
            t.SetTextSize(V(1.4, 1.4)); t.SetTextThickness(MM(0.3)); t.SetMirrored(True)
            board.Add(t)
            pcbnew.SaveBoard(pcb, board)
            patch_pro(pro)
            set_paper(pcb, self.paper)
            stats['segments'] = n
        return pcb, stats


def set_paper(path, paper):
    t = open(path).read()
    t = re.sub(r'\(paper "[^"]+"\)', f'(paper "{paper}")', t, count=1)
    open(path, 'w').write(t)


def drc(pcb_path):
    board = pcbnew.LoadBoard(pcb_path)
    set_rules(board)
    rpt = os.path.splitext(pcb_path)[0] + '-drc.rpt'
    pcbnew.WriteDRCReport(board, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    t = open(rpt).read()
    ignore = ('lib_footprint', 'silk_', 'text_height', 'text_thickness')
    blocks = re.findall(r'^\[(\w+)\]:.*?Severity: (\w+)', t, re.M | re.S)
    errs = [k for k, sev in blocks if sev == 'error' and not k.startswith(ignore)]
    nunc = re.search(r'\*\* Found (\d+) unconnected pads', t)
    return (len(errs), int(nunc.group(1)) if nunc else -1, rpt)


if __name__ == '__main__':
    key, out = sys.argv[1], sys.argv[2]
    extra = [a for a in sys.argv[3:] if not a.startswith('--')]
    uu = json.load(open(extra[0])) if extra else {}
    b = {x.key: x for x in designs.all_boards()}[key]
    import shutil, tempfile
    rotear = '--noroute' not in sys.argv
    tentativas = int(os.environ.get('ROUTE_TRIES', '4')) if rotear else 1
    melhor, guarda = None, tempfile.mkdtemp()
    for tent in range(tentativas):
        pb = PCBBuilder(b, out, uu)
        pcb, st = pb.build(route=rotear)
        if not rotear:
            break
        st['drc'], st['unrouted'], rpt = drc(pcb)
        st['tentativa'] = tent + 1
        nota = st['unrouted'] * 100 + st['drc']
        if melhor is None or nota < melhor[0]:
            melhor = (nota, dict(st))
            for f in (pcb, os.path.splitext(pcb)[0] + '.kicad_pro', rpt):
                shutil.copy(f, guarda)
        if nota == 0:
            break
    if rotear and melhor[0] != 0:
        for f in os.listdir(guarda):
            shutil.copy(os.path.join(guarda, f), out)
        st = melhor[1]
    print(json.dumps({'board': key, 'pcb': pcb, **st}))
