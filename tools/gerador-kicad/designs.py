"""Descricao (design-as-code) de todas as placas do Computador 8 Bits v3.0.
Autor do projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
Nomes de rede com ~{...} sao ativos em nivel baixo (barra em cima).
"""
from collections import OrderedDict

PWR = ['+5V', '+5V', 'GND', 'GND']
PWR_NAMES = ['+5V', '+5V', 'GND', 'GND']
BUSL = ['D0', 'D1', 'D2', 'D3']
BUSH = ['D4', 'D5', 'D6', 'D7']


class Comp:
    def __init__(self, ref, sym, value, pins, fp=None, pinlabels=None, group=None):
        self.ref, self.sym, self.value, self.pins, self.fp = ref, sym, value, {str(k): v for k, v in pins.items()}, fp
        self.pinlabels = pinlabels  # nomes impressos na serigrafia (conectores)
        self.group = group


class Board:
    def __init__(self, key, title, rev, folder, desc, changes=()):
        self.key, self.title, self.rev, self.folder, self.desc = key, title, rev, folder, desc
        self.changes = list(changes)
        self.comps = OrderedDict()
        self.layout = None
        self._c = 0

    def add(self, ref, sym, value, pins, fp=None, pinlabels=None, group=None):
        assert ref not in self.comps, ref
        self.comps[ref] = Comp(ref, sym, value, pins, fp, pinlabels, group)
        return self.comps[ref]

    def hdr(self, ref, value, nets, labels=None):
        labels = labels or [n.replace('~{', '/').replace('}', '') if n else 'NC' for n in nets]
        return self.add(ref, 'Conn_01x04', value, {i + 1: n for i, n in enumerate(nets)}, pinlabels=labels, group='J')

    def r(self, ref, val, a, b):
        return self.add(ref, 'R', val, {1: a, 2: b}, group='R')

    def c(self, ref, val, a, b='GND', sym='C', fp=None):
        return self.add(ref, sym, val, {1: a, 2: b}, fp=fp, group='C')

    def led(self, ref, anode, cathode, color='verde'):
        return self.add(ref, 'LED', f'LED {color} 3mm', {2: anode, 1: cathode}, group='LED')

    def decoupling(self, n, start=1):
        for i in range(n):
            self.c(f'C{start + i}', '100nF', '+5V', 'GND')

    def nets(self):
        s = set()
        for c in self.comps.values():
            for n in c.pins.values():
                if n:
                    s.add(n)
        return s


def ic173(b, ref, D, Q, load, clr='RST', clk='CLK'):
    """D=[D1..D4], Q=[Q1..Q4]"""
    b.add(ref, '74LS173', '74LS173', {1: 'GND', 2: 'GND', 3: Q[0], 4: Q[1], 5: Q[2], 6: Q[3], 7: clk, 8: 'GND',
                                      9: load, 10: load, 11: D[3], 12: D[2], 13: D[1], 14: D[0], 15: clr, 16: '+5V'},
          group='IC')


def ic245(b, ref, A, B, oe, dir_net='+5V'):
    p = {1: dir_net, 10: 'GND', 19: oe, 20: '+5V'}
    for i in range(8):
        p[2 + i] = A[i]
        p[18 - i] = B[i]
    b.add(ref, '74LS245', '74LS245', p, group='IC')


def register8(key, title, folder, prefix, load, oe, oe_label, extra_out=True, out_names=('ALU_L', 'ALU_H'),
              with_245=True, desc='', changes=(), led_r='470'):
    """Registrador de 8 bits (A, B, IR e OUT compartilham a mesma topologia)."""
    b = Board(key, title, '3.0', folder, desc, changes)
    q = [f'{prefix}{i}' for i in range(8)]
    # U1 = nibble alto (bits 4..7), U2 = nibble baixo (bits 0..3) -- igual ao projeto original
    ic173(b, 'U1', D=['D7', 'D6', 'D5', 'D4'], Q=[q[7], q[6], q[5], q[4]], load=load)
    ic173(b, 'U2', D=['D3', 'D2', 'D1', 'D0'], Q=[q[3], q[2], q[1], q[0]], load=load)
    n_ic = 2
    if with_245:
        if key == 'IR':
            A = ['GND', 'GND', 'GND', 'GND', q[3], q[2], q[1], q[0]]
        else:
            A = [q[7], q[6], q[5], q[4], q[3], q[2], q[1], q[0]]
        ic245(b, 'U3', A, ['D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'], oe)
        n_ic = 3
    for i in range(8):
        bit = 7 - i
        b.led(f'LED{i+1}', q[bit], f'LK{i+1}')
        b.r(f'R{i+1}', led_r, f'LK{i+1}', 'GND')
    b.decoupling(n_ic)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'CONTROLE', ['CLK', load, 'RST', oe if with_245 else None],
          ['CLK', '/' + load[2:-1], 'RST', oe_label])
    b.hdr('J3', 'BUS_L', BUSL)
    b.hdr('J4', 'BUS_H', BUSH)
    if key == 'IR':
        b.hdr('J5', 'OPCODE', [q[7], q[6], q[5], q[4]], ['OP3', 'OP2', 'OP1', 'OP0'])
    elif extra_out:
        b.hdr('J5', out_names[0], q[0:4], [f'{prefix}{i}' for i in range(4)])
        b.hdr('J6', out_names[1], q[4:8], [f'{prefix}{i}' for i in range(4, 8)])
    return b


# ---------------------------------------------------------------------------
def board_acc():
    return register8('ACC', 'Registrador A (Acumulador)', 'acc-registrador-a', 'A', '~{ACI}', '~{ACO}', '/ACO',
                     desc='Registrador A de 8 bits (2x 74LS173) com saida para o barramento (74LS245) e saida '
                          'permanente para a ULA.',
                     changes=['Redesenho em KiCad; mesma logica do ACC Register 2.0V.'])


def board_b():
    return register8('B', 'Registrador B', 'b-registrador-b', 'B', '~{BRI}', '~{BRO}', '/BRO',
                     desc='Registrador B de 8 bits; alimenta a entrada B da ULA.',
                     changes=['Redesenho em KiCad; mesma logica do B Register 2.0V.',
                              '~{BRO} fica em +5V no backplane (B nunca escreve no barramento).'])


def board_ir():
    return register8('IR', 'Registrador de Instrucao (IR)', 'ir-registrador-instrucao', 'I', '~{IRI}', '~{IRO}',
                     '/IRO', desc='Guarda a instrucao: nibble alto = opcode (para o decodificador), nibble baixo = '
                                  'operando (volta ao barramento por ~{IRO}).',
                     changes=['Conector OPCODE com OP3 no pino 1 (cabo reto ate o Control Decoder v3).'])


def board_out():
    return register8('OUT', 'Registrador de Saida (OUT)', 'out-registrador-saida', 'O', '~{ORI}', '~{ORI}', 'NC',
                     with_245=False, out_names=('DISPLAY_L', 'DISPLAY_H'),
                     desc='Registrador de saida: guarda o valor exibido pelo display decimal.',
                     changes=['Resistores de LED padronizados em 470 R (antes 150 R).'])


def board_alu():
    b = Board('ALU', 'Unidade Logica e Aritmetica (ULA)', '3.0', 'alu-unidade-logica-aritmetica',
              'Soma/subtracao (2x 74LS283 + 74LS86), AND, OR, XOR e NOT, selecionados por AL1:AL0 em 4x 74LS153.',
              changes=['CORRECAO: AL0 e AL1 (selecao dos 74LS153) nao chegavam a nenhum conector - agora em CTRL1 pinos 3/4.',
                       'CORRECAO: saidas 2Y de U5 e U6 (AND dos bits 1 e 5) estavam ligadas ao GND (curto) e as '
                       'entradas 2C1 de U13/U15 tambem - agora AND1/AND5 ligados corretamente.',
                       'NOVO: U18 74LS04 como buffer de SUB e NOT (cada sinal aciona 8-9 entradas TTL, '
                       'mais do que a EEPROM consegue drenar).',
                       'NOVO: CARRY (C4 do somador alto) exposto em CTRL2 pino 2 para futuro registrador de flags.'])
    A = [f'A{i}' for i in range(8)]; B = [f'B{i}' for i in range(8)]
    BX = [f'BX{i}' for i in range(8)]; S = [f'S{i}' for i in range(8)]
    AND = [f'AND{i}' for i in range(8)]; OR = [f'OR{i}' for i in range(8)]
    BN = [f'BN{i}' for i in range(8)]; X = [f'X{i}' for i in range(8)]; R = [f'R{i}' for i in range(8)]

    def adder(ref, a, bb, s, cin, cout):
        b.add(ref, '74LS283', '74LS283', {5: a[0], 3: a[1], 14: a[2], 12: a[3], 6: bb[0], 2: bb[1], 15: bb[2],
                                          11: bb[3], 7: cin, 4: s[0], 1: s[1], 13: s[2], 10: s[3], 9: cout,
                                          16: '+5V', 8: 'GND'}, group='IC')

    def quad(ref, part, a, bb, y):
        b.add(ref, part, part, {1: a[0], 2: bb[0], 3: y[0], 4: a[1], 5: bb[1], 6: y[1], 9: a[2], 10: bb[2], 8: y[2],
                                12: a[3], 13: bb[3], 11: y[3], 14: '+5V', 7: 'GND'}, group='IC')

    adder('U1', A[4:8], BX[4:8], S[4:8], 'CY4', 'CARRY')
    adder('U2', A[0:4], BX[0:4], S[0:4], 'SUB_B', 'CY4')
    quad('U3', '74LS86', B[4:8], ['SUB_B'] * 4, BX[4:8])
    quad('U4', '74LS86', B[0:4], ['SUB_B'] * 4, BX[0:4])
    quad('U5', '74LS08', A[0:4], B[0:4], AND[0:4])
    quad('U6', '74LS08', A[4:8], B[4:8], AND[4:8])
    quad('U7', '74LS32', A[0:4], B[0:4], OR[0:4])
    quad('U8', '74LS32', A[4:8], B[4:8], OR[4:8])
    quad('U9', '74LS32', ['NOT_B'] * 4, B[0:4], BN[0:4])
    quad('U10', '74LS86', A[0:4], BN[0:4], X[0:4])
    quad('U11', '74LS32', ['NOT_B'] * 4, B[4:8], BN[4:8])
    quad('U12', '74LS86', A[4:8], BN[4:8], X[4:8])
    for ref, lo in (('U13', 0), ('U14', 2), ('U15', 4), ('U16', 6)):
        hi = lo + 1
        b.add(ref, '74LS153', '74LS153', {6: S[lo], 5: AND[lo], 4: OR[lo], 3: X[lo], 7: R[lo],
                                          10: S[hi], 11: AND[hi], 12: OR[hi], 13: X[hi], 9: R[hi],
                                          1: 'GND', 15: 'GND', 14: 'AL0', 2: 'AL1', 16: '+5V', 8: 'GND'}, group='IC')
    ic245(b, 'U17', [R[7], R[6], R[5], R[4], R[3], R[2], R[1], R[0]],
          ['D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'], '~{ALUO}')
    b.add('U18', '74LS04', '74LS04', {1: 'SUB', 2: '~{SUB}', 3: '~{SUB}', 4: 'SUB_B', 5: 'NOT', 6: '~{NOT}',
                                      9: '~{NOT}', 8: 'NOT_B', 11: 'GND', 10: None, 13: 'GND', 12: None,
                                      14: '+5V', 7: 'GND'}, group='IC')
    for i in range(8):
        b.led(f'LED{i+1}', R[7 - i], f'LK{i+1}')
        b.r(f'R{i+1}', '470', f'LK{i+1}', 'GND')
    b.decoupling(18)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'BUS_L', BUSL)
    b.hdr('J3', 'BUS_H', BUSH)
    b.hdr('J4', 'ACC_L', A[0:4]); b.hdr('J5', 'ACC_H', A[4:8])
    b.hdr('J6', 'B_L', B[0:4]); b.hdr('J7', 'B_H', B[4:8])
    b.hdr('J8', 'CTRL1', ['~{ALUO}', 'SUB', 'AL0', 'AL1'], ['/ALUO', 'SUB', 'AL0', 'AL1'])
    b.hdr('J9', 'CTRL2', ['NOT', 'CARRY', None, None], ['NOT', 'CARRY', 'NC', 'NC'])
    return b


def board_pc():
    b = Board('PC', 'Contador de Programa (PC)', '3.0', 'pc-contador-programa',
              'Contador de 4 bits (74LS161) com carga (JMP) e saida para o barramento (74LS245).',
              changes=['Alimentacao em conector proprio (antes misturada com ~{PCO}).',
                       'Novo conector BUS_H: o 74LS245 coloca 0 no nibble alto durante ~{PCO}.'])
    P = ['P0', 'P1', 'P2', 'P3']
    b.add('U1', '74LS161', '74LS161', {1: '~{RST}', 2: 'CLK', 3: 'D0', 4: 'D1', 5: 'D2', 6: 'D3', 7: 'PCI', 10: 'PCI',
                                       9: '~{JMP}', 14: P[0], 13: P[1], 12: P[2], 11: P[3], 15: None,
                                       16: '+5V', 8: 'GND'}, group='IC')
    ic245(b, 'U2', ['GND', 'GND', 'GND', 'GND', P[3], P[2], P[1], P[0]],
          ['D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'], '~{PCO}')
    for i in range(4):
        b.led(f'LED{i+1}', P[3 - i], f'LK{i+1}')
        b.r(f'R{i+1}', '470', f'LK{i+1}', 'GND')
    b.decoupling(2)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'CONTROLE', ['PCI', 'CLK', '~{JMP}', '~{RST}'], ['PCI', 'CLK', '/JMP', '/RST'])
    b.hdr('J3', 'CONTROLE2', ['~{PCO}', None, None, None], ['/PCO', 'NC', 'NC', 'NC'])
    b.hdr('J4', 'BUS_L', BUSL)
    b.hdr('J5', 'BUS_H', BUSH)
    return b


def board_ram():
    b = Board('RAM', 'Memoria RAM e MAR', '3.0', 'ram-mar-memoria',
              'MAR (74LS173), RAM 16x8 (2x 74S189), multiplexadores PROG/RUN (74LS157), '
              'gravacao manual por chaves DIP e pulso de escrita sincronizado ao clock.',
              changes=['CORRECAO: pino 6 (THR) do 555 da chave PROG/RUN estava flutuando - agora no GND; CV com 10nF.',
                       'MELHORIA: chaves DIP agora ligam ao +5V com resistores de pull-down (RN1/RN2 1k): '
                       'chave LIGADA = bit 1 (antes era invertido).',
                       'Entradas nao usadas do U10 (74LS157) aterradas.',
                       'Barramento entra e sai pelos mesmos conectores BUS_L/BUS_H (antes 5 conectores).'])
    M = ['M0', 'M1', 'M2', 'M3']; RA = ['RA0', 'RA1', 'RA2', 'RA3']
    ic173(b, 'U6', D=['D3', 'D2', 'D1', 'D0'], Q=[M[3], M[2], M[1], M[0]], load='~{MAI}')
    b.add('U7', '74LS157', '74LS157', {1: 'RUN', 2: 'SWA3', 3: M[3], 4: RA[3], 5: 'SWA2', 6: M[2], 7: RA[2],
                                       14: 'SWA0', 13: M[0], 12: RA[0], 11: 'SWA1', 10: M[1], 9: RA[1],
                                       15: 'GND', 16: '+5V', 8: 'GND'}, group='IC')
    b.add('U8', '74LS157', '74LS157', {1: 'RUN', 2: 'SWD7', 3: 'D7', 4: 'WD7', 5: 'SWD6', 6: 'D6', 7: 'WD6',
                                       14: 'SWD4', 13: 'D4', 12: 'WD4', 11: 'SWD5', 10: 'D5', 9: 'WD5',
                                       15: 'GND', 16: '+5V', 8: 'GND'}, group='IC')
    b.add('U9', '74LS157', '74LS157', {1: 'RUN', 2: 'SWD3', 3: 'D3', 4: 'WD3', 5: 'SWD2', 6: 'D2', 7: 'WD2',
                                       14: 'SWD0', 13: 'D0', 12: 'WD0', 11: 'SWD1', 10: 'D1', 9: 'WD1',
                                       15: 'GND', 16: '+5V', 8: 'GND'}, group='IC')
    b.add('U10', '74LS157', '74LS157', {1: 'RUN', 14: '~{WE_MAN}', 13: '~{WE_RUN}', 12: '~{WE}',
                                        2: 'GND', 3: 'GND', 4: None, 5: 'GND', 6: 'GND', 7: None,
                                        11: 'GND', 10: 'GND', 9: None, 15: 'GND', 16: '+5V', 8: 'GND'}, group='IC')
    for ref, wd, q in (('U1', 4, 4), ('U2', 0, 0)):
        b.add(ref, '74S189', '74S189', {1: RA[0], 15: RA[1], 14: RA[2], 13: RA[3], 2: 'GND', 3: '~{WE}',
                                        4: f'WD{wd}', 6: f'WD{wd+1}', 10: f'WD{wd+2}', 12: f'WD{wd+3}',
                                        5: f'~{{Q{q}}}', 7: f'~{{Q{q+1}}}', 9: f'~{{Q{q+2}}}', 11: f'~{{Q{q+3}}}',
                                        16: '+5V', 8: 'GND'}, group='IC')
    b.add('U3', '74LS04', '74LS04', {1: '~{Q7}', 2: 'Q7', 3: '~{Q6}', 4: 'Q6', 5: '~{Q5}', 6: 'Q5', 9: '~{Q4}', 8: 'Q4',
                                     11: 'GND', 10: None, 13: 'GND', 12: None, 14: '+5V', 7: 'GND'}, group='IC')
    b.add('U4', '74LS04', '74LS04', {1: '~{Q3}', 2: 'Q3', 3: '~{Q2}', 4: 'Q2', 5: '~{Q1}', 6: 'Q1', 9: '~{Q0}', 8: 'Q0',
                                     11: 'GND', 10: None, 13: 'GND', 12: None, 14: '+5V', 7: 'GND'}, group='IC')
    ic245(b, 'U5', ['Q7', 'Q6', 'Q5', 'Q4', 'Q3', 'Q2', 'Q1', 'Q0'],
          ['D7', 'D6', 'D5', 'D4', 'D3', 'D2', 'D1', 'D0'], '~{RMO}')
    b.add('U11', '74LS00', '74LS00', {1: 'WPULSE', 2: 'RMI', 3: '~{WE_RUN}', 4: 'CLK', 5: 'CLK', 6: '~{CLK_R}',
                                      9: 'CLK', 10: 'CLK', 8: 'CLKN', 12: 'CLKN', 13: 'CLKN', 11: 'CLKD',
                                      14: '+5V', 7: 'GND'}, group='IC')
    b.add('U12', 'NE555', 'NE555', {1: 'GND', 2: '~{SW_RUN}', 3: 'RUN', 4: '~{SW_PROG}', 5: 'CV_RUN', 6: 'GND',
                                    7: None, 8: '+5V'}, group='IC')
    b.c('C13', '1nF', 'CLKD', 'WPULSE')
    b.r('R18', '1k', 'WPULSE', 'GND')
    b.c('C14', '10nF', 'CV_RUN', 'GND')
    b.r('R13', '1k', '+5V', '~{SW_PROG}')
    b.r('R16', '1k', '+5V', '~{SW_RUN}')
    b.add('SW2', 'SW_SPDT', 'PROG/RUN', {1: 'GND', 2: '~{SW_RUN}', 3: '~{SW_PROG}'}, group='SW')
    b.led('LED13', 'LP13', '~{SW_PROG}', 'vermelho'); b.r('R14', '470', '+5V', 'LP13')
    b.led('LED14', 'LP14', '~{SW_RUN}', 'verde'); b.r('R15', '470', '+5V', 'LP14')
    b.add('SW1', 'SW_DIP_x04', 'ENDERECO', {1: '+5V', 2: '+5V', 3: '+5V', 4: '+5V',
                                            8: 'SWA0', 7: 'SWA1', 6: 'SWA2', 5: 'SWA3'}, group='SW')
    b.add('SW3', 'SW_DIP_x08', 'DADO', dict([(i, '+5V') for i in range(1, 9)] +
                                            [(16 - i, f'SWD{i}') for i in range(8)]), group='SW')
    b.add('RN2', 'R_Network04', '4x1k', {1: 'GND', 2: 'SWA0', 3: 'SWA1', 4: 'SWA2', 5: 'SWA3'}, group='R')
    b.add('RN1', 'R_Network08', '8x1k', dict([(1, 'GND')] + [(i + 2, f'SWD{i}') for i in range(8)]), group='R')
    b.add('SW4', 'SW_Push', 'GRAVAR', {1: '~{WE_MAN}', 2: 'GND'}, group='SW')
    b.r('R17', '10k', '+5V', '~{WE_MAN}')
    for i in range(8):
        b.led(f'LED{i+1}', f'Q{7-i}', f'LK{i+1}')
        b.r(f'R{i+1}', '470', f'LK{i+1}', 'GND')
    for i in range(4):
        b.led(f'LED{9+i}', RA[3 - i], f'LK{9+i}', 'amarelo')
        b.r(f'R{9+i}', '470', f'LK{9+i}', 'GND')
    b.decoupling(12)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'CONTROLE1', ['CLK', '~{MAI}', 'RST', 'RMI'], ['CLK', '/MAI', 'RST', 'RMI'])
    b.hdr('J3', 'CONTROLE2', ['~{WE}', '~{CLK_R}', '~{RMO}', 'RUN'], ['/WE', '/CLK', '/RMO', 'RUN'])
    b.hdr('J4', 'BUS_L', BUSL)
    b.hdr('J5', 'BUS_H', BUSH)
    return b


def board_cd():
    b = Board('CD', 'Decodificador de Controle (microcodigo)', '3.0', 'cd-decodificador-controle',
              '3 EEPROMs 28C16 com o microcodigo: endereco = FLAGS(A8:A7) OPCODE(A6:A3) PASSO(A2:A0).',
              changes=['CORRECAO CRITICA: ~{WE} (pino 21) das EEPROMs estava no GND - agora em +5V.',
                       'Ordem do opcode corrigida no proprio conector (OP3 no pino 1, igual ao IR).',
                       'NOVO: conector FLAGS (A7/A8) com pull-down para futuro registrador de flags (JC/JZ).',
                       'Sinais ativos em nivel baixo agora sao invertidos no microcodigo (ver firmware).'])
    base = {8: 'T0', 7: 'T1', 6: 'T2', 5: 'OP0', 4: 'OP1', 3: 'OP2', 2: 'OP3', 1: 'FLG_C', 23: 'FLG_Z',
            22: 'GND', 19: 'GND', 18: 'GND', 20: 'GND', 21: '+5V', 24: '+5V', 12: 'GND'}
    io = [9, 10, 11, 13, 14, 15, 16, 17]
    e2 = ['~{IRI}', '~{RMO}', 'RMI', '~{MAI}', '~{PCO}', '~{JMP}', 'PCI', 'HLT']
    e1 = ['NOT', '~{ALUO}', 'AL0', 'AL1', 'SUB', '~{ACI}', '~{ACO}', '~{IRO}']
    e0 = [None, None, None, None, 'E0_4', 'E0_5', '~{ORI}', '~{BRI}']
    for ref, outs in (('U1', e2), ('U2', e1), ('U3', e0)):
        p = dict(base)
        for k, n in zip(io, outs):
            p[k] = n
        b.add(ref, '28C16', {'U1': 'AT28C16 (EEPROM2)', 'U2': 'AT28C16 (EEPROM1)', 'U3': 'AT28C16 (EEPROM0)'}[ref], p,
              group='IC')
    b.r('R1', '10k', 'FLG_C', 'GND')
    b.r('R2', '10k', 'FLG_Z', 'GND')
    b.decoupling(3)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'PASSO', ['T0', 'T1', 'T2', None], ['T0', 'T1', 'T2', 'NC'])
    b.hdr('J3', 'OPCODE', ['OP3', 'OP2', 'OP1', 'OP0'])
    b.hdr('J4', 'FLAGS', ['FLG_C', 'FLG_Z', None, None], ['CF', 'ZF', 'NC', 'NC'])
    b.hdr('J5', 'CTRL_A', e2[0:4]); b.hdr('J6', 'CTRL_B', e2[4:8])
    b.hdr('J7', 'CTRL_C', e1[0:4]); b.hdr('J8', 'CTRL_D', e1[4:8])
    b.hdr('J9', 'CTRL_E', ['~{BRI}', '~{ORI}', 'E0_5', 'E0_4'], ['/BRI', '/ORI', 'E0_5', 'E0_4'])
    return b


def board_fetch():
    b = Board('FETCH', 'Contador de Passos (Fetch/Execute)', '3.0', 'fetch-contador-passos',
              'Contador de passos T0..T4 (74LS161 + 74LS138). ~{Y5} reinicia o contador via placa de Reset.',
              changes=['LEDs de passo agora acendem no passo ATIVO (antes acendiam os inativos) e ganharam resistores.',
                       'Entradas de carga paralela A..D do 74LS161 aterradas (antes flutuando).'])
    b.add('U1', '74LS161', '74LS161', {1: '~{STEPCLR}', 2: '~{CLK}', 3: 'GND', 4: 'GND', 5: 'GND', 6: 'GND', 7: '+5V',
                                       10: '+5V', 9: '+5V', 14: 'T0', 13: 'T1', 12: 'T2', 11: None, 15: None,
                                       16: '+5V', 8: 'GND'}, group='IC')
    b.add('U2', '74LS138', '74LS138', {1: 'T0', 2: 'T1', 3: 'T2', 6: '+5V', 4: 'GND', 5: 'GND', 15: '~{S0}',
                                       14: '~{S1}', 13: '~{S2}', 12: '~{S3}', 11: '~{S4}', 10: '~{Y5}', 9: None,
                                       7: None, 16: '+5V', 8: 'GND'}, group='IC')
    for i, t in enumerate(['T2', 'T1', 'T0']):
        b.led(f'LED{i+1}', t, f'LK{i+1}', 'amarelo')
        b.r(f'R{i+1}', '330', f'LK{i+1}', 'GND')
    for i in range(5):
        b.led(f'LED{4+i}', f'LA{4+i}', f'~{{S{i}}}')
        b.r(f'R{4+i}', '470', '+5V', f'LA{4+i}')
    b.decoupling(2)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'PASSO', ['T0', 'T1', 'T2', None], ['T0', 'T1', 'T2', 'NC'])
    b.hdr('J3', 'CONTROLE', ['~{Y5}', '~{CLK}', '~{STEPCLR}', None], ['/Y5', '/CLK', '/STCLR', 'NC'])
    return b


def board_clock():
    b = Board('CLOCK', 'Clock Astavel / Monoestavel', '3.0', 'clock-astavel-monoestavel',
              'NE556: metade astavel (clock automatico ajustavel) e metade monoestavel (passo manual sem repique). '
              'Chave AUTO/MANUAL, entrada HLT.',
              changes=['R1 150 R -> 1 k: corrente no pino DIS do 556 cai de ~33 mA para 5 mA; faixa 0,7 a 140 Hz.',
                       'Logica identica ao Clock 2.1V (testado em bancada).'])
    b.add('U1', 'NE556', 'NE556', {1: 'DIS1', 2: 'TC1', 6: 'TC1', 3: 'CV1', 4: '+5V', 5: 'ASTABLE', 7: 'GND',
                                   8: 'TRIG2', 9: 'MONO', 10: '+5V', 11: 'CV2', 12: 'TC2', 13: 'TC2', 14: '+5V'},
          group='IC')
    b.add('U2', '74LS00', '74LS00', {1: '~{ASTABLE}', 2: 'MODE', 3: 'N1', 4: '~{MODE}', 5: 'MONO', 6: 'N2',
                                     12: 'N2', 13: 'N1', 11: 'CLKSEL', 9: '~{HLT}', 10: 'CLKSEL', 8: '~{CLK}',
                                     14: '+5V', 7: 'GND'}, group='IC')
    b.add('U3', '74LS04', '74LS04', {1: 'ASTABLE', 2: '~{ASTABLE}', 3: 'MODE', 4: '~{MODE}', 5: 'HLT', 6: '~{HLT}',
                                     9: '~{CLK}', 8: 'CLK', 11: '~{MODE_SW}', 10: 'MODE', 13: 'MODE_SW',
                                     12: '~{MODE_SW}', 14: '+5V', 7: 'GND'}, group='IC')
    b.r('R1', '1k', '+5V', 'DIS1')
    b.r('R2', '10', 'DIS1', 'RB')
    b.add('RV1', 'POT', '100k lin', {1: 'TC1', 2: 'TC1', 3: 'RB'}, group='R')
    b.c('C1', '10uF tantalo', 'TC1', 'GND', sym='C_Pol', fp='Capacitor_THT:CP_Radial_Tantal_D4.5mm_P2.50mm')
    b.c('C2', '10nF', 'CV1', 'GND')
    b.c('C3', '10nF', 'CV2', 'GND')
    b.r('R4', '10k', '+5V', 'TRIG2')
    b.add('SW1', 'SW_Push', 'PASSO', {1: 'TRIG2', 2: 'GND'}, group='SW')
    b.r('R5', '330k', '+5V', 'TC2')
    b.c('C4', '330nF', 'TC2', 'GND')
    b.add('SW2', 'SW_SPDT', 'AUTO/MANUAL', {1: 'MODE_SW', 2: '+5V', 3: 'GND'}, group='SW')
    b.led('LED1', 'CLK', 'LK1', 'azul')
    b.r('R6', '470', 'LK1', 'GND')
    b.c('C5', '100nF', '+5V', 'GND'); b.c('C6', '100nF', '+5V', 'GND'); b.c('C7', '100nF', '+5V', 'GND')
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'CLOCK', ['CLK', '~{CLK}', 'HLT', None], ['CLK', '/CLK', 'HLT', 'NC'])
    return b


def board_reset():
    b = Board('RESET', 'Circuito de Reset', '3.0', 'reset-circuito',
              'Gera RST e ~{RST} (botao + reset automatico ao ligar) e o ~{STEPCLR} do contador de passos '
              '(= ~{RST} AND ~{Y5}).',
              changes=['CORRECAO CRITICA: o botao usava pull-down de 10 k numa entrada TTL - a entrada LS '
                       'fica em nivel ALTO com 10 k ao GND, entao o reset ficaria sempre ativo. Agora o botao vai '
                       'ao GND com pull-up de 10 k (logica invertida no 1o gate).',
                       'NOVO: reset automatico ao ligar (C1 10 uF) e LED indicador.',
                       'Recomendado 74LS132 (NAND Schmitt, mesma pinagem do 74LS00).',
                       'Primeira versao em PCB desta placa.'])
    b.add('U1', '74LS132', '74LS132 (ou 74LS00)', {12: '~{BTN}', 13: '~{BTN}', 11: 'RST', 9: 'RST', 10: 'RST',
                                                   8: '~{RST}', 1: '~{RST}', 2: '~{Y5}', 3: 'SC', 4: 'SC', 5: 'SC',
                                                   6: '~{STEPCLR}', 14: '+5V', 7: 'GND'}, group='IC')
    b.add('SW1', 'SW_Push', 'RESET', {1: '~{BTN}', 2: 'GND'}, group='SW')
    b.r('R1', '10k', '+5V', '~{BTN}')
    b.c('C1', '10uF', '~{BTN}', 'GND', sym='C_Pol')
    b.r('R2', '10k', '+5V', '~{Y5}')
    b.led('LED1', 'LR1', '~{RST}', 'vermelho')
    b.r('R3', '1k', '+5V', 'LR1')
    b.c('C2', '100nF', '+5V', 'GND')
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'RESET', ['RST', '~{RST}', '~{Y5}', '~{STEPCLR}'], ['RST', '/RST', '/Y5', '/STCLR'])
    return b


def board_display():
    b = Board('DISPLAY', 'Display Decimal', '3.0', 'display-decimal',
              'Converte o valor de 8 bits do registrador OUT em decimal (0..255 ou -128..127) por EEPROM 28C16 e '
              'varredura de 4 digitos (555 + 74LS161 + 74LS139).',
              changes=['Display especificado como CATODO COMUM (o 74LS139 ativa digito em nivel baixo).',
                       'NOVO: resistores de 100 R em serie nos segmentos (protecao da EEPROM).',
                       'Metade nao usada do 74LS139 com entradas fixadas.',
                       'Conteudo da EEPROM gerado em firmware/display (antes nao existia).'])
    p = {8: 'O0', 7: 'O1', 6: 'O2', 5: 'O3', 4: 'O4', 3: 'O5', 2: 'O6', 1: 'O7', 23: 'DG0', 22: 'DG1', 19: 'SIGNED',
         18: 'GND', 20: 'GND', 21: '+5V', 24: '+5V', 12: 'GND'}
    segs = ['g', 'f', 'e', 'd', 'c', 'b', 'a', 'dp']
    for k, s in zip([9, 10, 11, 13, 14, 15, 16, 17], segs):
        p[k] = f'IO_{s}'
    b.add('U1', '28C16', 'AT28C16 (DISPLAY)', p, group='IC')
    b.add('U2', 'NE555', 'NE555', {1: 'GND', 2: 'TCD', 6: 'TCD', 7: 'DISD', 3: 'MUXCLK', 4: '+5V', 5: 'CVD', 8: '+5V'},
          group='IC')
    b.add('U3', '74LS161', '74LS161', {1: '+5V', 2: 'MUXCLK', 3: 'GND', 4: 'GND', 5: 'GND', 6: 'GND', 7: '+5V', 10: '+5V',
                                       9: '+5V', 14: 'DG0', 13: 'DG1', 12: None, 11: None, 15: None, 16: '+5V',
                                       8: 'GND'}, group='IC')
    b.add('U4', '74LS139', '74LS139', {2: 'GND', 3: 'GND', 1: '+5V', 4: None, 5: None, 6: None, 7: None,
                                       14: 'DG0', 13: 'DG1', 15: 'GND', 12: '~{DIG4}', 11: '~{DIG3}',
                                       10: '~{DIG2}', 9: '~{DIG1}', 16: '+5V', 8: 'GND'}, group='IC')
    segpin = {'a': 11, 'b': 7, 'c': 4, 'd': 2, 'e': 1, 'f': 10, 'g': 5, 'dp': 3}
    dp = {segpin[s]: f'SEG_{s}' for s in segs}
    dp.update({12: '~{DIG1}', 9: '~{DIG2}', 8: '~{DIG3}', 6: '~{DIG4}'})
    b.add('DS1', 'Display_7seg_4dig_CC', '4 dig. 0,4" catodo comum', dp, group='IC')
    for i, s in enumerate(segs):
        b.r(f'R{2+i}', '100', f'IO_{s}', f'SEG_{s}')
    b.r('R1', '1k', '+5V', 'DISD')
    b.r('R10', '100k', 'DISD', 'TCD')
    b.c('C5', '15nF', 'TCD', 'GND')
    b.c('C6', '10nF', 'CVD', 'GND')
    b.add('SW1', 'SW_SPDT', 'SEM SINAL/COM SINAL', {1: 'SIGNED', 2: '+5V', 3: 'GND'}, group='SW')
    b.decoupling(4)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    b.hdr('J2', 'ENTRADA_L', ['O0', 'O1', 'O2', 'O3'])
    b.hdr('J3', 'ENTRADA_H', ['O4', 'O5', 'O6', 'O7'])
    return b


# Sinais de controle na ordem dos conectores CTRL_A..CTRL_E do Decodificador (= CD_A..CD_E do backplane)
CTRL_GRUPOS = [('A', ['~{IRI}', '~{RMO}', 'RMI', '~{MAI}']), ('B', ['~{PCO}', '~{JMP}', 'PCI', 'HLT']),
               ('C', ['NOT', '~{ALUO}', 'AL0', 'AL1']), ('D', ['SUB', '~{ACI}', '~{ACO}', '~{IRO}']),
               ('E', ['~{BRI}', '~{ORI}', 'E0_5', 'E0_4'])]


def board_cw():
    """Palavra de Controle: repete os 20 sinais do Decodificador e mostra os 18 sinais de controle em LEDs."""
    b = Board('CW', 'Palavra de Controle (18 LEDs)', '3.0', 'cw-palavra-de-controle',
              'Fica entre o Decodificador de Controle e o backplane (que nao muda): recebe os 5 V do conector P_CD e '
              'repassa ao Decodificador por J12. 3x 74HCT541 repetem os 20 sinais das EEPROMs '
              '(reforcam a saida das EEPROMs) e 18 LEDs mostram cada sinal de controle: LED aceso = sinal ATIVO, '
              'inclusive nos sinais com barra (ativos em 0). Opcional: sem ela, os cabos do Decodificador vao direto '
              'ao backplane.',
              changes=['Placa nova na v3.0: os 11 sinais ativos em 0 ja saem invertidos das EEPROMs, entao esta placa '
                       'NAO inverte nada - so repete os sinais e acende os LEDs.'])
    sinais = [n for _, g in CTRL_GRUPOS for n in g]
    canais = [sinais[0:8], sinais[8:16], sinais[16:20] + [None] * 4]
    for k, ch in enumerate(canais):
        p = {1: 'GND', 19: 'GND', 20: '+5V', 10: 'GND'}
        for i, n in enumerate(ch):
            p[2 + i] = f'IN_{n}' if n else 'GND'
            p[18 - i] = n
        b.add(f'U{k + 1}', '74HCT541', '74HCT541', p, group='IC')
    nl = 0
    for n in sinais:
        if n.startswith('E0_'):
            continue
        nl += 1
        if n.startswith('~{'):      # ativo em 0: +5V -> R -> LED -> saida (acende quando a saida vai a 0)
            b.r(f'R{nl}', '1k', '+5V', f'LA{nl}')
            b.led(f'LED{nl}', f'LA{nl}', n, 'azul')
        else:                       # ativo em 1: saida -> LED -> R -> GND
            b.led(f'LED{nl}', n, f'LK{nl}', 'azul')
            b.r(f'R{nl}', '1k', f'LK{nl}', 'GND')
    b.decoupling(3)
    b.hdr('J1', 'ALIMENTACAO', PWR, PWR_NAMES)
    for k, (g, ns) in enumerate(CTRL_GRUPOS):
        lab = [n.replace('~{', '/').replace('}', '') for n in ns]
        b.hdr(f'J{2 + k}', f'ENTRADA_{g}', [f'IN_{n}' for n in ns], lab)
        b.hdr(f'J{7 + k}', f'SAIDA_{g}', ns, lab)
    b.hdr('J12', 'ALIM_DECODIF', PWR, PWR_NAMES)   # repassa os 5 V para o Decodificador (backplane sem mudanca)
    return b


# Conectores do backplane: (ref, rotulo, redes, nomes impressos)
BACKPLANE_HEADERS = [
    # alimentacao
    *[(f'P_{m}', PWR, PWR_NAMES) for m in ['ACC', 'B', 'ALU', 'IR', 'OUT', 'PC', 'RAM', 'CD', 'FETCH', 'CLOCK', 'RESET',
                                          'DISPLAY']],
    *[(f'BL_{m}', BUSL, None) for m in ['ACC', 'B', 'ALU', 'IR', 'OUT', 'PC', 'RAM']],
    *[(f'BH_{m}', BUSH, None) for m in ['ACC', 'B', 'ALU', 'IR', 'OUT', 'PC', 'RAM']],
    ('C_ACC', ['CLK', '~{ACI}', 'RST', '~{ACO}'], None),
    ('C_B', ['CLK', '~{BRI}', 'RST', '+5V'], ['CLK', '/BRI', 'RST', '+5V']),
    ('C_IR', ['CLK', '~{IRI}', 'RST', '~{IRO}'], None),
    ('C_OUT', ['CLK', '~{ORI}', 'RST', None], None),
    ('C_PC1', ['PCI', 'CLK', '~{JMP}', '~{RST}'], None),
    ('C_PC2', ['~{PCO}', None, None, None], None),
    ('C_RAM1', ['CLK', '~{MAI}', 'RST', 'RMI'], None),
    ('C_RAM2', [None, None, '~{RMO}', None], None),
    ('C_ALU1', ['~{ALUO}', 'SUB', 'AL0', 'AL1'], None),
    ('C_ALU2', ['NOT', None, None, None], None),
    ('CD_A', ['~{IRI}', '~{RMO}', 'RMI', '~{MAI}'], None),
    ('CD_B', ['~{PCO}', '~{JMP}', 'PCI', 'HLT'], None),
    ('CD_C', ['NOT', '~{ALUO}', 'AL0', 'AL1'], None),
    ('CD_D', ['SUB', '~{ACI}', '~{ACO}', '~{IRO}'], None),
    ('CD_E', ['~{BRI}', '~{ORI}', 'E0_5', 'E0_4'], None),
    ('C_FETCH', ['~{Y5}', '~{CLK}', '~{STEPCLR}', None], ['/Y5', '/CLK', '/STCLR', 'NC']),
    ('C_CLOCK', ['CLK', '~{CLK}', 'HLT', None], None),
    ('C_RESET', ['RST', '~{RST}', '~{Y5}', '~{STEPCLR}'], ['RST', '/RST', '/Y5', '/STCLR']),
    ('EXPANSAO', ['E0_5', 'E0_4', 'CLK', 'RST'], None),
]


def board_backplane():
    b = Board('BACKPLANE', 'Backplane / Barramento (Assembly Layout)', '3.0', 'backplane-barramento',
              'Placa-mae de interligacao: entrada de 5 V protegida, distribuicao de alimentacao, barramento de dados '
              'D0..D7 com LEDs, e roteamento de todos os sinais de controle entre os modulos. Cada conector tem a '
              'mesma pinagem do conector correspondente no modulo: use cabos de 4 vias RETOS (pino 1 com pino 1).',
              changes=['Placa nova (antes a pasta ASSEMBLY LAYOUT estava vazia).'])
    b.add('J1', 'Barrel_Jack', 'Jack DC 5,5x2,1 (5 V)', {1: 'VIN', 2: 'GND', 3: 'GND'}, group='PWRIN')
    b.add('J2', 'Conn_01x02', 'Borne 5 V', {1: 'VIN', 2: 'GND'}, pinlabels=['+5V', 'GND'], group='PWRIN')
    b.add('SW1', 'SW_SPDT', 'LIGA/DESLIGA', {1: 'VIN', 2: 'VSW', 3: None}, group='PWRIN')
    b.add('F1', 'Polyfuse', 'PTC 3 A (MF-RG300)', {1: 'VSW', 2: '+5V'}, group='PWRIN')
    b.add('D1', 'D', '1N5822', {1: '+5V', 2: 'GND'}, group='PWRIN')
    b.c('C1', '470uF 10V', '+5V', 'GND', sym='C_Pol', fp='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm')
    b.c('C2', '100nF', '+5V', 'GND')
    b.led('LED1', 'LPWR', 'GND', 'verde')
    b.r('R1', '470', '+5V', 'LPWR')
    for i in range(8):
        b.led(f'LED{2+i}', f'D{7-i}', f'LB{2+i}', 'vermelho')
        b.r(f'R{2+i}', '1k', f'LB{2+i}', 'GND')
    j = 3
    b.header_map = {}
    for name, nets, labels in BACKPLANE_HEADERS:
        ref = f'J{j}'
        b.hdr(ref, name, nets, labels)
        b.header_map[name] = ref
        j += 1
    return b


def all_boards():
    return [board_clock(), board_reset(), board_pc(), board_ram(), board_ir(), board_cd(), board_cw(), board_fetch(),
            board_acc(), board_b(), board_alu(), board_out(), board_display(), board_backplane()]


# ---------------------------------------------------------------------------
# Cabos de 4 vias (todos RETOS: pino 1 <-> pino 1).
# (placa, conector, destino) ; destino = nome de conector do backplane  ou  (placa, conector) p/ cabo direto
CABOS = [
    ('CLOCK', 'J1', 'P_CLOCK'), ('CLOCK', 'J2', 'C_CLOCK'),
    ('RESET', 'J1', 'P_RESET'), ('RESET', 'J2', 'C_RESET'),
    ('PC', 'J1', 'P_PC'), ('PC', 'J2', 'C_PC1'), ('PC', 'J3', 'C_PC2'), ('PC', 'J4', 'BL_PC'), ('PC', 'J5', 'BH_PC'),
    ('RAM', 'J1', 'P_RAM'), ('RAM', 'J2', 'C_RAM1'), ('RAM', 'J3', 'C_RAM2'), ('RAM', 'J4', 'BL_RAM'),
    ('RAM', 'J5', 'BH_RAM'),
    ('IR', 'J1', 'P_IR'), ('IR', 'J2', 'C_IR'), ('IR', 'J3', 'BL_IR'), ('IR', 'J4', 'BH_IR'), ('IR', 'J5', ('CD', 'J3')),
    # Decodificador -> Palavra de Controle -> backplane (o backplane NAO muda).
    # Sem a placa CW: CD J1 -> P_CD e CD J5..J9 -> CD_A..CD_E, direto.
    ('CW', 'J1', 'P_CD'), ('CD', 'J1', ('CW', 'J12')),
    ('CD', 'J5', ('CW', 'J2')), ('CD', 'J6', ('CW', 'J3')), ('CD', 'J7', ('CW', 'J4')), ('CD', 'J8', ('CW', 'J5')),
    ('CD', 'J9', ('CW', 'J6')),
    ('CW', 'J7', 'CD_A'), ('CW', 'J8', 'CD_B'), ('CW', 'J9', 'CD_C'), ('CW', 'J10', 'CD_D'),
    ('CW', 'J11', 'CD_E'),
    ('FETCH', 'J1', 'P_FETCH'), ('FETCH', 'J2', ('CD', 'J2')), ('FETCH', 'J3', 'C_FETCH'),
    ('ACC', 'J1', 'P_ACC'), ('ACC', 'J2', 'C_ACC'), ('ACC', 'J3', 'BL_ACC'), ('ACC', 'J4', 'BH_ACC'),
    ('ACC', 'J5', ('ALU', 'J4')), ('ACC', 'J6', ('ALU', 'J5')),
    ('B', 'J1', 'P_B'), ('B', 'J2', 'C_B'), ('B', 'J3', 'BL_B'), ('B', 'J4', 'BH_B'),
    ('B', 'J5', ('ALU', 'J6')), ('B', 'J6', ('ALU', 'J7')),
    ('ALU', 'J1', 'P_ALU'), ('ALU', 'J2', 'BL_ALU'), ('ALU', 'J3', 'BH_ALU'), ('ALU', 'J8', 'C_ALU1'),
    ('ALU', 'J9', 'C_ALU2'),
    ('OUT', 'J1', 'P_OUT'), ('OUT', 'J2', 'C_OUT'), ('OUT', 'J3', 'BL_OUT'), ('OUT', 'J4', 'BH_OUT'),
    ('OUT', 'J5', ('DISPLAY', 'J2')), ('OUT', 'J6', ('DISPLAY', 'J3')),
    ('DISPLAY', 'J1', 'P_DISPLAY'),
]

# pinos onde os nomes podem diferir de proposito: (placa, conector, pino) -> motivo
EXCECOES = {
    ('B', 'J2', 4): '~{BRO} do registrador B fica fixo em +5V no backplane',
    ('RAM', 'J3', 1): 'saida de teste ~{WE} - nao vai ao backplane',
    ('RAM', 'J3', 2): 'saida de teste ~{CLK} - nao vai ao backplane',
    ('RAM', 'J3', 4): 'saida de teste RUN - nao vai ao backplane',
    ('ALU', 'J9', 2): 'CARRY reservado para o futuro registrador de flags',
}


# mesmo sinal com nomes diferentes em placas diferentes
ALIAS = {'I7': 'OP3', 'I6': 'OP2', 'I5': 'OP1', 'I4': 'OP0'}
ALIAS.update({f'IN_{n}': n for _, g in CTRL_GRUPOS for n in g})   # entradas da Palavra de Controle


def verificar_cabos():
    """Confere pino a pino que cada cabo reto liga redes de mesmo nome. Retorna lista de erros."""
    bs = {b.key: b for b in all_boards()}
    bp = bs['BACKPLANE']
    erros, usados = [], set()
    for placa, j, dest in CABOS:
        a = bs[placa].comps[j]
        if isinstance(dest, tuple):
            b = bs[dest[0]].comps[dest[1]]
            usados.add(dest)
        else:
            b = bp.comps[bp.header_map[dest]]
            usados.add(('BACKPLANE', dest))
        for p in range(1, 5):
            na, nb = a.pins.get(str(p)), b.pins.get(str(p))
            na, nb = ALIAS.get(na, na), ALIAS.get(nb, nb)
            if na != nb and (placa, j, p) not in EXCECOES:
                erros.append(f'{placa}.{j} pino {p} = {na}  x  {dest} pino {p} = {nb}')
    for name, *_ in BACKPLANE_HEADERS:
        if ('BACKPLANE', name) not in usados and name != 'EXPANSAO':
            erros.append(f'conector do backplane sem cabo: {name}')
    return erros
