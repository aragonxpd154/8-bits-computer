"""Biblioteca de simbolos do Computador 8 Bits (Marcos Silva dos Santos).
Gera simbolos KiCad 7 (formato .kicad_sym) a partir de descricoes simples.
"""
G = 2.54  # grade padrao (100 mil)

def _f(v):
    s = f"{v:.4f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

class Pin:
    def __init__(self, num, name, x, y, angle, etype='input', length=G, hide_name=False):
        self.num, self.name, self.x, self.y, self.angle = str(num), name, x, y, angle
        self.etype, self.length, self.hide_name = etype, length, hide_name

class Symbol:
    def __init__(self, name, ref='U', footprint='', desc='', power=False):
        self.name, self.ref, self.footprint, self.desc, self.power = name, ref, footprint, desc, power
        self.pins, self.graphics = [], []
        self.hide_pin_names = False
        self.hide_pin_numbers = False
        self.ref_pos = (0, 0); self.val_pos = (0, -2.54)
        self.bbox = (-5, -5, 5, 5)  # xmin, ymin, xmax, ymax (coordenadas do simbolo, y para cima)

    def pin(self, num):
        for p in self.pins:
            if p.num == str(num):
                return p
        raise KeyError(f"{self.name}: pino {num} inexistente")

    def sexpr(self, libname=None):
        full = f"{libname}:{self.name}" if libname else self.name
        o = [f'(symbol "{full}"']
        if self.power:
            o.append('(power)')
        if self.hide_pin_numbers:
            o.append('(pin_numbers hide)')
        if self.hide_pin_names:
            o.append('(pin_names (offset 0) hide)')
        else:
            o.append('(pin_names (offset 0.762))')
        o.append('(in_bom yes) (on_board yes)')
        rx, ry = self.ref_pos; vx, vy = self.val_pos
        hide_ref = ' hide' if self.power else ''
        o.append(f'(property "Reference" "{self.ref}" (at {_f(rx)} {_f(ry)} 0) (effects (font (size 1.27 1.27)){hide_ref}))')
        o.append(f'(property "Value" "{self.name}" (at {_f(vx)} {_f(vy)} 0) (effects (font (size 1.27 1.27))))')
        o.append(f'(property "Footprint" "{self.footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        o.append('(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        if self.desc:
            o.append(f'(property "ki_description" "{self.desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        o.append(f'(symbol "{self.name}_0_1" ' + ' '.join(self.graphics) + ')')
        ps = []
        for p in self.pins:
            hide = ' hide' if p.hide_name else ''
            ps.append(f'(pin {p.etype} line (at {_f(p.x)} {_f(p.y)} {p.angle}) (length {_f(p.length)})'
                      f' (name "{p.name}" (effects (font (size 1.27 1.27)){hide}))'
                      f' (number "{p.num}" (effects (font (size 1.27 1.27)))))')
        o.append(f'(symbol "{self.name}_1_1" ' + ' '.join(ps) + ')')
        o.append(')')
        return ' '.join(o)


def rect(x1, y1, x2, y2, fill='background', w=0.254):
    return f'(rectangle (start {_f(x1)} {_f(y1)}) (end {_f(x2)} {_f(y2)}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def poly(pts, fill='none', w=0.254):
    p = ' '.join(f'(xy {_f(x)} {_f(y)})' for x, y in pts)
    return f'(polyline (pts {p}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def circle(x, y, r, fill='none', w=0.254):
    return f'(circle (center {_f(x)} {_f(y)}) (radius {_f(r)}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def text(t, x, y, size=1.27):
    return f'(text "{t}" (at {_f(x)} {_f(y)} 0) (effects (font (size {size} {size}))))'


def ic(name, left, right, vcc=None, gnd=None, footprint='', desc='', label=None, ref='U'):
    """CI retangular. left/right: listas de (num, nome, tipo) ou None (espaco)."""
    s = Symbol(name, ref, footprint, desc)
    n = max(len(left), len(right))
    def tlen(lst):
        return max([len(e[1].replace('~{', '').replace('}', '')) for e in lst if e] + [1])
    w = (tlen(left) + tlen(right)) * 1.27 + 3.0
    half = max(5.08, (int((w / 2) / G) + 1) * G)
    top = (n + 1) * G / 2.0
    top = int(top / G + 0.999) * G
    bottom = top - (n + 1) * G
    for i, e in enumerate(left):
        if e:
            s.pins.append(Pin(e[0], e[1], -half - G, top - (i + 1) * G, 0, e[2] if len(e) > 2 else 'input'))
    for i, e in enumerate(right):
        if e:
            s.pins.append(Pin(e[0], e[1], half + G, top - (i + 1) * G, 180, e[2] if len(e) > 2 else 'output'))
    yt, yb = top, bottom
    if vcc:
        s.pins.append(Pin(vcc, 'VCC', 0, top + G, 270, 'power_in'))
    if gnd:
        s.pins.append(Pin(gnd, 'GND', 0, bottom - G, 90, 'power_in'))
    s.graphics.append(rect(-half, top, half, bottom))
    if label:
        s.graphics.append(text(label, half / 2 + 1.5, top + 1.6, 1.0))
    s.ref_pos = (-half / 2 - 1.5, top + 1.6)
    s.val_pos = (half / 2 + 1.5, bottom - 1.9)
    s.bbox = (-half - G, bottom - G, half + G, top + G)
    return s


def two_pin(name, ref, kind, footprint=''):
    """Componente de 2 pinos horizontal: pino esquerdo / direito."""
    s = Symbol(name, ref, footprint)
    s.hide_pin_names = True
    s.hide_pin_numbers = True
    L = 2 * G
    if kind == 'R':
        lp, rp = '1', '2'
        s.graphics.append(rect(-2.54, 1.016, 2.54, -1.016, fill='none'))
    elif kind == 'C':
        lp, rp = '1', '2'
        s.graphics += [poly([(-0.635, 2.032), (-0.635, -2.032)], w=0.4), poly([(0.635, 2.032), (0.635, -2.032)], w=0.4),
                       poly([(-2.54, 0), (-0.635, 0)]), poly([(0.635, 0), (2.54, 0)])]
    elif kind == 'CP':
        lp, rp = '1', '2'
        s.graphics += [rect(-1.016, 2.032, -0.508, -2.032, fill='none'), rect(0.508, 2.032, 1.016, -2.032, fill='outline'),
                       poly([(-2.54, 0), (-1.016, 0)]), poly([(1.016, 0), (2.54, 0)]), text('+', -2.0, 1.6, 1.27)]
    elif kind in ('LED', 'D'):
        lp, rp = '2', '1'  # anodo a esquerda, catodo a direita
        s.graphics += [poly([(-1.27, 1.27), (-1.27, -1.27), (1.27, 0), (-1.27, 1.27)], fill='none'),
                       poly([(1.27, 1.27), (1.27, -1.27)]), poly([(-2.54, 0), (2.54, 0)])]
        if kind == 'LED':
            s.graphics += [poly([(-0.254, 1.778), (0.762, 2.794)]), poly([(0.762, 1.778), (1.778, 2.794)])]
    elif kind == 'F':
        lp, rp = '1', '2'
        s.graphics += [rect(-2.54, 0.762, 2.54, -0.762, fill='none'), poly([(-2.54, 0), (2.54, 0)])]
    elif kind == 'SW':
        lp, rp = '1', '2'
        s.graphics += [circle(-2.032, 0, 0.508), circle(2.032, 0, 0.508), poly([(-2.54, 1.27), (2.54, 1.27)]),
                       poly([(0, 1.27), (0, 3.048)])]
    s.pins.append(Pin(lp, 'A' if kind in ('LED', 'D') else '~', -G - 2.54, 0, 0, 'passive'))
    s.pins.append(Pin(rp, 'K' if kind in ('LED', 'D') else '~', G + 2.54, 0, 180, 'passive'))
    s.ref_pos = (0, 3.3); s.val_pos = (0, -3.3)
    s.bbox = (-2 * G, -2.54, 2 * G, 2.54)
    return s


def conn(name, n, footprint=''):
    s = Symbol(name, 'J', footprint)
    top = (n - 1) * G / 2.0
    top = round(top / 1.27) * 1.27
    for i in range(n):
        y = top - i * G
        s.pins.append(Pin(i + 1, f'P{i+1}', -2 * G, y, 0, 'passive'))
        s.graphics.append(poly([(-G, y), (-0.508, y)]))
    s.hide_pin_names = True
    s.graphics.insert(0, rect(-1.27, top + 1.27, 1.27, top - (n - 1) * G - 1.27, fill='background'))
    s.ref_pos = (0, top + 2.8); s.val_pos = (0, top - (n - 1) * G - 2.8)
    s.bbox = (-2 * G, top - (n - 1) * G - 1.27, 1.27, top + 1.27)
    return s


def spdt(footprint=''):
    s = Symbol('SW_SPDT', 'SW', footprint)
    s.hide_pin_names = True
    s.pins += [Pin(1, 'COM', -2 * G, 0, 0, 'passive'), Pin(2, 'A', 2 * G, 2.54, 180, 'passive'),
               Pin(3, 'B', 2 * G, -2.54, 180, 'passive')]
    s.graphics += [circle(-2.032, 0, 0.508), circle(2.032, 2.54, 0.508), circle(2.032, -2.54, 0.508),
                   poly([(-1.6, 0.3), (1.8, 2.0)])]
    s.ref_pos = (0, 4.3); s.val_pos = (0, -4.3)
    s.bbox = (-2 * G, -3.81, 2 * G, 3.81)
    return s


def pot(footprint=''):
    s = Symbol('POT', 'RV', footprint)
    s.hide_pin_names = True
    s.pins += [Pin(1, '1', -2 * G, 0, 0, 'passive'), Pin(3, '3', 2 * G, 0, 180, 'passive'),
               Pin(2, 'W', 0, 2 * G, 270, 'passive')]
    s.graphics += [rect(-2.54, 1.016, 2.54, -1.016, fill='none'), poly([(0, 2.54), (0, 1.2)]),
                   poly([(-0.6, 1.9), (0, 1.2), (0.6, 1.9)])]
    s.ref_pos = (3.5, 3.0); s.val_pos = (0, -3.3)
    s.bbox = (-2 * G, -2.54, 2 * G, 2 * G)
    return s


def dipsw(n, footprint=''):
    s = Symbol(f'SW_DIP_x{n:02d}', 'SW', footprint)
    top = (n - 1) * G / 2.0
    top = round(top / 1.27) * 1.27
    for i in range(n):
        y = top - i * G
        s.pins.append(Pin(i + 1, str(i + 1), -3 * G, y, 0, 'passive'))
        s.pins.append(Pin(2 * n - i, str(2 * n - i), 3 * G, y, 180, 'passive'))
        s.graphics += [circle(-1.524, y, 0.4), circle(1.524, y, 0.4), poly([(-1.2, y + 0.2), (1.4, y + 1.0)])]
    s.hide_pin_names = True
    s.graphics.insert(0, rect(-2 * G, top + 1.27, 2 * G, top - (n - 1) * G - 1.27, fill='background'))
    s.ref_pos = (0, top + 2.8); s.val_pos = (0, top - (n - 1) * G - 2.8)
    s.bbox = (-3 * G, top - (n - 1) * G - 1.27, 3 * G, top + 1.27)
    return s


def rarray(n, footprint=''):
    """Rede resistiva SIP com comum no pino 1 (n resistores, n+1 pinos)."""
    s = Symbol(f'R_Network{n:02d}', 'RN', footprint)
    s.hide_pin_names = True
    top = (n - 1) * G / 2.0
    top = round(top / 1.27) * 1.27
    s.pins.append(Pin(1, 'COM', -3 * G, 0, 0, 'passive'))
    for i in range(n):
        y = top - i * G
        s.pins.append(Pin(i + 2, f'R{i+1}', 3 * G, y, 180, 'passive'))
        s.graphics.append(rect(-0.4, y + 0.5, 1.6, y - 0.5, fill='none'))
        s.graphics.append(poly([(1.6, y), (G, y)]))
        s.graphics.append(poly([(-0.4, y), (-1.27, y)]))
    s.graphics.append(poly([(-1.27, top), (-1.27, top - (n - 1) * G)]))
    s.graphics.append(poly([(-G, 0), (-1.27, 0)]))
    s.graphics.insert(0, rect(-G, top + 1.27, G, top - (n - 1) * G - 1.27, fill='background'))
    s.ref_pos = (0, top + 2.8); s.val_pos = (0, top - (n - 1) * G - 2.8)
    s.bbox = (-3 * G, top - (n - 1) * G - 1.27, 3 * G, top + 1.27)
    return s


def barrel(footprint=''):
    s = Symbol('Barrel_Jack', 'J', footprint)
    s.hide_pin_names = True
    s.pins += [Pin(1, '+', 2 * G, 2.54, 180, 'passive'), Pin(2, '-', 2 * G, 0, 180, 'passive'),
               Pin(3, 'SW', 2 * G, -2.54, 180, 'passive')]
    s.graphics += [rect(-3.81, 3.81, 2.54, -3.81), circle(-1.27, 2.54, 0.8), poly([(-0.47, 2.54), (2.54, 2.54)])]
    s.ref_pos = (0, 5.3); s.val_pos = (0, -5.3)
    s.bbox = (-3.81, -3.81, 2 * G, 3.81)
    return s


def power_sym(name):
    s = Symbol(name, '#PWR', '', power=True)
    s.hide_pin_numbers = True
    s.hide_pin_names = True
    if name == 'GND':
        s.pins.append(Pin(1, 'GND', 0, 0, 270, 'power_in', length=0, hide_name=True))
        s.graphics.append(poly([(0, 0), (0, -1.27), (1.27, -1.27), (0, -2.54), (-1.27, -1.27), (0, -1.27)]))
        s.val_pos = (0, -3.81)
        s.bbox = (-1.27, -2.54, 1.27, 0)
    elif name == 'PWR_FLAG':
        s.ref = '#FLG'
        s.pins.append(Pin(1, 'pwr', 0, 0, 90, 'power_out', length=0, hide_name=True))
        s.graphics.append(poly([(0, 0), (0, 1.27), (-1.016, 1.905), (0, 2.54), (1.016, 1.905), (0, 1.27)]))
        s.val_pos = (0, 3.81)
        s.bbox = (-1.016, 0, 1.016, 2.54)
    else:
        s.pins.append(Pin(1, name, 0, 0, 90, 'power_in', length=0, hide_name=True))
        s.graphics.append(poly([(-0.762, 1.27), (0, 2.54), (0.762, 1.27)]))
        s.graphics.append(poly([(0, 0), (0, 2.54)]))
        s.val_pos = (0, 3.556)
        s.bbox = (-0.762, 0, 0.762, 2.54)
    return s


def seg7x4(footprint=''):
    s = ic('Display_7seg_4dig_CC',
           [(11, 'a'), (7, 'b'), (4, 'c'), (2, 'd'), (1, 'e'), (10, 'f'), (5, 'g'), (3, 'dp')],
           [(12, 'DIG1', 'input'), (9, 'DIG2', 'input'), (8, 'DIG3', 'input'), (6, 'DIG4', 'input')],
           footprint=footprint, label='4 digitos catodo comum', ref='DS')
    return s


# ---------------------------------------------------------------------------
FP = {
    'DIP8': 'Package_DIP:DIP-8_W7.62mm_LongPads', 'DIP14': 'Package_DIP:DIP-14_W7.62mm_LongPads',
    'DIP16': 'Package_DIP:DIP-16_W7.62mm_LongPads', 'DIP20': 'Package_DIP:DIP-20_W7.62mm_LongPads',
    'DIP24': 'Package_DIP:DIP-24_W15.24mm_LongPads',
    'R': 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal',
    'C': 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',
    'CP': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm',
    'CPBIG': 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
    'CT': 'Capacitor_THT:CP_Radial_Tantal_D4.5mm_P2.50mm',
    'LED': 'LED_THT:LED_D3.0mm', 'HDR4': 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
    'SWPUSH': 'Button_Switch_THT:SW_PUSH_6mm', 'SPDT': 'Button_Switch_THT:SW_Slide-03_Wuerth-WS-SLTV_10x2.5x6.4_P2.54mm',
    'DIPSW4': 'Button_Switch_THT:SW_DIP_SPSTx04_Slide_9.78x12.34mm_W7.62mm_P2.54mm',
    'DIPSW8': 'Button_Switch_THT:SW_DIP_SPSTx08_Slide_9.78x22.5mm_W7.62mm_P2.54mm',
    'SIP5': 'Resistor_THT:R_Array_SIP5', 'SIP9': 'Resistor_THT:R_Array_SIP9',
    'POT': 'Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical',
    'JACK': 'Connector_BarrelJack:BarrelJack_Horizontal', 'TB2': 'TerminalBlock:TerminalBlock_bornier-2_P5.08mm',
    'PTC': 'Fuse:Fuse_Bourns_MF-RG300', 'D201': 'Diode_THT:D_DO-201AD_P15.24mm_Horizontal',
    'SEG4': 'computador8bits:Display_7seg_4dig_0.4in',
}

def build_library():
    L = {}
    def add(s):
        L[s.name] = s
    add(ic('74LS173', [(14, 'D1'), (13, 'D2'), (12, 'D3'), (11, 'D4'), None, (9, '~{G1}'), (10, '~{G2}'), (7, 'CLK'),
                       (15, 'CLR'), (1, '~{M}'), (2, '~{N}')],
           [(3, 'Q1', 'tri_state'), (4, 'Q2', 'tri_state'), (5, 'Q3', 'tri_state'), (6, 'Q4', 'tri_state')],
           16, 8, FP['DIP16'], 'Registrador 4 bits 3-state', '74LS173'))
    add(ic('74LS245', [(2, 'A1', 'bidirectional'), (3, 'A2', 'bidirectional'), (4, 'A3', 'bidirectional'),
                       (5, 'A4', 'bidirectional'), (6, 'A5', 'bidirectional'), (7, 'A6', 'bidirectional'),
                       (8, 'A7', 'bidirectional'), (9, 'A8', 'bidirectional'), None, (1, 'DIR'), (19, '~{OE}')],
           [(18, 'B1', 'bidirectional'), (17, 'B2', 'bidirectional'), (16, 'B3', 'bidirectional'),
            (15, 'B4', 'bidirectional'), (14, 'B5', 'bidirectional'), (13, 'B6', 'bidirectional'),
            (12, 'B7', 'bidirectional'), (11, 'B8', 'bidirectional')],
           20, 10, FP['DIP20'], 'Transceptor octal 3-state', '74LS245'))
    add(ic('74LS283', [(5, 'A1'), (3, 'A2'), (14, 'A3'), (12, 'A4'), None, (6, 'B1'), (2, 'B2'), (15, 'B3'), (11, 'B4'),
                       None, (7, 'C0')],
           [(4, 'S1'), (1, 'S2'), (13, 'S3'), (10, 'S4'), None, None, None, None, None, None, (9, 'C4')],
           16, 8, FP['DIP16'], 'Somador completo 4 bits', '74LS283'))
    for nm, lab in (('74LS00', '4x NAND'), ('74LS08', '4x AND'), ('74LS32', '4x OR'), ('74LS86', '4x XOR'),
                    ('74LS132', '4x NAND Schmitt')):
        add(ic(nm, [(1, '1A'), (2, '1B'), (4, '2A'), (5, '2B'), (9, '3A'), (10, '3B'), (12, '4A'), (13, '4B')],
               [(3, '1Y'), None, (6, '2Y'), None, (8, '3Y'), None, (11, '4Y')], 14, 7, FP['DIP14'], lab, lab))
    add(ic('74LS04', [(1, '1A'), (3, '2A'), (5, '3A'), (9, '4A'), (11, '5A'), (13, '6A')],
           [(2, '1Y'), (4, '2Y'), (6, '3Y'), (8, '4Y'), (10, '5Y'), (12, '6Y')], 14, 7, FP['DIP14'], '6x NOT', '6x NOT'))
    add(ic('74LS153', [(6, '1C0'), (5, '1C1'), (4, '1C2'), (3, '1C3'), (1, '~{1G}'), None, (10, '2C0'), (11, '2C1'),
                       (12, '2C2'), (13, '2C3'), (15, '~{2G}'), None, (14, 'A'), (2, 'B')],
           [None, None, (7, '1Y'), None, None, None, None, None, (9, '2Y')], 16, 8, FP['DIP16'],
           'Duplo multiplexador 4:1', '2x MUX 4:1'))
    add(ic('74LS161', [(3, 'A'), (4, 'B'), (5, 'C'), (6, 'D'), None, (7, 'ENP'), (10, 'ENT'), (9, '~{LOAD}'),
                       (1, '~{CLR}'), (2, 'CLK')],
           [(14, 'QA'), (13, 'QB'), (12, 'QC'), (11, 'QD'), None, (15, 'RCO')], 16, 8, FP['DIP16'],
           'Contador binario sincrono 4 bits', 'Contador 4 bits'))
    add(ic('74LS138', [(1, 'A'), (2, 'B'), (3, 'C'), None, (6, 'G1'), (4, '~{G2A}'), (5, '~{G2B}')],
           [(15, '~{Y0}'), (14, '~{Y1}'), (13, '~{Y2}'), (12, '~{Y3}'), (11, '~{Y4}'), (10, '~{Y5}'), (9, '~{Y6}'),
            (7, '~{Y7}')], 16, 8, FP['DIP16'], 'Decodificador 3:8', 'DEC 3:8'))
    add(ic('74LS139', [(2, '1A'), (3, '1B'), (1, '~{1G}'), None, None, (14, '2A'), (13, '2B'), (15, '~{2G}')],
           [(4, '~{1Y0}'), (5, '~{1Y1}'), (6, '~{1Y2}'), (7, '~{1Y3}'), None, (12, '~{2Y0}'), (11, '~{2Y1}'),
            (10, '~{2Y2}'), (9, '~{2Y3}')], 16, 8, FP['DIP16'], 'Duplo decodificador 2:4', '2x DEC 2:4'))
    add(ic('74LS157', [(2, '1A'), (3, '1B'), (5, '2A'), (6, '2B'), (14, '3A'), (13, '3B'), (11, '4A'), (10, '4B'), None,
                       (1, 'S'), (15, '~{G}')],
           [None, (4, '1Y'), None, (7, '2Y'), None, (12, '3Y'), None, (9, '4Y')], 16, 8, FP['DIP16'],
           'Quadruplo multiplexador 2:1', '4x MUX 2:1'))
    add(ic('74S189', [(1, 'A0'), (15, 'A1'), (14, 'A2'), (13, 'A3'), None, (4, 'D1'), (6, 'D2'), (10, 'D3'), (12, 'D4'),
                      None, (2, '~{CS}'), (3, '~{WE}')],
           [None, None, None, None, None, (5, '~{Q1}', 'tri_state'), (7, '~{Q2}', 'tri_state'),
            (9, '~{Q3}', 'tri_state'), (11, '~{Q4}', 'tri_state')], 16, 8, FP['DIP16'],
           'RAM 16x4 saidas invertidas', 'RAM 16x4'))
    add(ic('28C16', [(8, 'A0'), (7, 'A1'), (6, 'A2'), (5, 'A3'), (4, 'A4'), (3, 'A5'), (2, 'A6'), (1, 'A7'), (23, 'A8'),
                     (22, 'A9'), (19, 'A10'), None, (18, '~{CE}'), (20, '~{OE}'), (21, '~{WE}')],
           [(9, 'IO0', 'tri_state'), (10, 'IO1', 'tri_state'), (11, 'IO2', 'tri_state'), (13, 'IO3', 'tri_state'),
            (14, 'IO4', 'tri_state'), (15, 'IO5', 'tri_state'), (16, 'IO6', 'tri_state'), (17, 'IO7', 'tri_state')],
           24, 12, FP['DIP24'], 'EEPROM paralela 2K x 8', 'EEPROM 2Kx8'))
    add(ic('NE556', [(6, 'TR1'), (2, 'THR1'), (3, 'CV1'), (4, '~{R1}'), None, (8, 'TR2'), (12, 'THR2'), (11, 'CV2'),
                     (10, '~{R2}')],
           [(5, 'Q1'), (1, 'DIS1', 'open_collector'), None, None, None, (9, 'Q2'), (13, 'DIS2', 'open_collector')],
           14, 7, FP['DIP14'], 'Duplo temporizador 555', 'Duplo 555'))
    add(ic('NE555', [(2, 'TR'), (6, 'THR'), (5, 'CV'), (4, '~{R}')], [(3, 'Q'), (7, 'DIS', 'open_collector')],
           8, 1, FP['DIP8'], 'Temporizador 555', '555'))
    add(seg7x4(FP['SEG4']))
    add(two_pin('R', 'R', 'R', FP['R']))
    add(two_pin('C', 'C', 'C', FP['C']))
    add(two_pin('C_Pol', 'C', 'CP', FP['CP']))
    add(two_pin('LED', 'LED', 'LED', FP['LED']))
    add(two_pin('D', 'D', 'D', FP['D201']))
    add(two_pin('Polyfuse', 'F', 'F', FP['PTC']))
    add(two_pin('SW_Push', 'SW', 'SW', FP['SWPUSH']))
    add(conn('Conn_01x04', 4, FP['HDR4']))
    add(conn('Conn_01x02', 2, FP['TB2']))
    add(spdt(FP['SPDT']))
    add(pot(FP['POT']))
    add(dipsw(4, FP['DIPSW4']))
    add(dipsw(8, FP['DIPSW8']))
    add(rarray(4, FP['SIP5']))
    add(rarray(8, FP['SIP9']))
    add(barrel(FP['JACK']))
    for p in ('+5V', 'GND', 'PWR_FLAG'):
        add(power_sym(p))
    return L

LIBNAME = 'computador8bits'

def write_library(path):
    L = build_library()
    with open(path, 'w') as f:
        f.write('(kicad_symbol_lib (version 20220914) (generator gerador_computador8bits)\n')
        for s in L.values():
            f.write('  ' + s.sexpr() + '\n')
        f.write(')\n')
    return L
