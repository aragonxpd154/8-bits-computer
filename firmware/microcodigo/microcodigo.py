#!/usr/bin/env python3
"""Gerador do microcodigo do Computador 8 Bits v3.0 - Marcos Silva dos Santos (GPL-3.0).

Gera as imagens das 3 EEPROMs 28C16 (2 KB cada) do Decodificador de Controle:
    EEPROM2.bin -> U1   (HLT PCI JMP PCO MAI RMI RMO IRI)
    EEPROM1.bin -> U2   (IRO ACO ACI SUB AL1 AL0 ALU NOT)
    EEPROM0.bin -> U3   (BRI ORI + 6 saidas livres)

Endereco da EEPROM:  A8=ZF  A7=CF  A6..A3=OPCODE  A2..A0=PASSO  (A9/A10 no GND)

IMPORTANTE (correcao da v3.0): varios sinais sao ATIVOS EM NIVEL BAIXO no hardware
(~OE do 74LS245, ~G do 74LS173, ~LOAD do 74LS161). O microcodigo antigo deixava esses
bits em 0 nos passos vazios, o que ligava TODAS as saidas no barramento ao mesmo tempo.
Aqui o microcodigo e escrito em logica positiva e os bits ativos-baixos sao invertidos
na hora de gravar (mascara ATIVO_BAIXO).
"""
import os, sys

# ---- bits de controle: (eeprom, mascara) ------------------------------------
HLT = (2, 0x80); PCI = (2, 0x40); JMP = (2, 0x20); PCO = (2, 0x10)
MAI = (2, 0x08); RMI = (2, 0x04); RMO = (2, 0x02); IRI = (2, 0x01)
IRO = (1, 0x80); ACO = (1, 0x40); ACI = (1, 0x20); SUB = (1, 0x10)
AL1 = (1, 0x08); AL0 = (1, 0x04); ALU = (1, 0x02); NOT = (1, 0x01)
BRI = (0, 0x80); ORI = (0, 0x40)

ATIVO_BAIXO = {2: 0x20 | 0x10 | 0x08 | 0x02 | 0x01,   # JMP PCO MAI RMO IRI
               1: 0x80 | 0x40 | 0x20 | 0x02,          # IRO ACO ACI ALU(~ALUO)
               0: 0x80 | 0x40}                        # BRI ORI

NOMES = {HLT: 'HLT', PCI: 'PCI', JMP: 'JMP', PCO: 'PCO', MAI: 'MAI', RMI: 'RMI', RMO: 'RMO', IRI: 'IRI',
         IRO: 'IRO', ACO: 'ACO', ACI: 'ACI', SUB: 'SUB', AL1: 'AL1', AL0: 'AL0', ALU: 'ALU', NOT: 'NOT',
         BRI: 'BRI', ORI: 'ORI'}

BUSCA = [[PCO, MAI], [RMO, IRI, PCI]]          # T0, T1 (iguais para todas as instrucoes)

# ---- conjunto de instrucoes ---------------------------------------------------
# opcode: (mnemonico, tem_operando, passos T2.., descricao)
INSTRUCOES = {
    0x0: ('NOP', False, [], 'nao faz nada'),
    0x1: ('LDA', True, [[IRO, MAI], [RMO, ACI]], 'A <- RAM[end]'),
    0x2: ('SUB', True, [[IRO, MAI], [RMO, BRI], [ALU, SUB, ACI]], 'A <- A - RAM[end]'),
    0x3: ('STA', True, [[IRO, MAI], [ACO, RMI]], 'RAM[end] <- A'),
    0x4: ('ADD', True, [[IRO, MAI], [RMO, BRI], [ALU, ACI]], 'A <- A + RAM[end]'),
    0x5: ('LDI', True, [[IRO, ACI]], 'A <- valor imediato (0..15)'),
    0x6: ('JMP', True, [[IRO, JMP]], 'PC <- end'),
    0x7: ('AND', True, [[IRO, MAI], [RMO, BRI], [ALU, AL0, ACI]], 'A <- A AND RAM[end]'),
    0x8: ('OR', True, [[IRO, MAI], [RMO, BRI], [ALU, AL1, ACI]], 'A <- A OR RAM[end]'),
    0x9: ('XOR', True, [[IRO, MAI], [RMO, BRI], [ALU, AL1, AL0, ACI]], 'A <- A XOR RAM[end]'),
    0xA: ('NOT', False, [[ALU, AL1, AL0, NOT, ACI]], 'A <- NOT A'),
    0xB: ('JC', True, 'CF', 'se CF=1: PC <- end (precisa da placa de flags)'),
    0xC: ('JZ', True, 'ZF', 'se ZF=1: PC <- end (precisa da placa de flags)'),
    0xD: ('NOP', False, [], 'reservado'),
    0xE: ('OUT', False, [[ACO, ORI]], 'OUT <- A (mostra no display)'),
    0xF: ('HLT', False, [[HLT]], 'para o clock'),
}

PASSOS_POR_INSTRUCAO = 5   # o 74LS138 reinicia o contador em T5 (~Y5)


def palavra(sinais):
    w = {0: 0, 1: 0, 2: 0}
    for e, m in sinais:
        w[e] |= m
    return w


def microcodigo():
    """Retorna dict eeprom -> bytearray(2048) ja com a inversao dos sinais ativos-baixos."""
    rom = {e: bytearray(2048) for e in (0, 1, 2)}
    for addr in range(2048):
        passo = addr & 0x7
        opcode = (addr >> 3) & 0xF
        cf = (addr >> 7) & 1
        zf = (addr >> 8) & 1
        nome, _, passos, _ = INSTRUCOES[opcode]
        if passos == 'CF':
            passos = [[IRO, JMP]] if cf else []
        elif passos == 'ZF':
            passos = [[IRO, JMP]] if zf else []
        seq = BUSCA + passos
        assert len(seq) <= PASSOS_POR_INSTRUCAO, nome
        sinais = seq[passo] if passo < len(seq) else []
        w = palavra(sinais)
        for e in (0, 1, 2):
            rom[e][addr] = w[e] ^ ATIVO_BAIXO[e]
    return rom


def intel_hex(data):
    out = []
    for off in range(0, len(data), 16):
        chunk = data[off:off + 16]
        rec = [len(chunk), (off >> 8) & 0xFF, off & 0xFF, 0] + list(chunk)
        cks = (-sum(rec)) & 0xFF
        out.append(':' + ''.join(f'{b:02X}' for b in rec) + f'{cks:02X}')
    out.append(':00000001FF')
    return '\n'.join(out) + '\n'


def tabela_markdown():
    linhas = ['| Opcode | Binario | Mnemonico | Operando | Operacao | Passos T2..T4 |', '|---|---|---|---|---|---|']
    for op, (nome, opnd, passos, desc) in INSTRUCOES.items():
        if passos in ('CF', 'ZF'):
            p = f'se {passos}: IRO JMP'
        else:
            p = ' / '.join(' '.join(NOMES[s] for s in st) for st in passos) or '-'
        linhas.append(f'| {op:X} | {op:04b} | {nome} | {"sim" if opnd else "-"} | {desc} | {p} |')
    return '\n'.join(linhas)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    rom = microcodigo()
    for e, chip in ((2, 'U1'), (1, 'U2'), (0, 'U3')):
        with open(os.path.join(out, f'EEPROM{e}.bin'), 'wb') as f:
            f.write(rom[e])
        with open(os.path.join(out, f'EEPROM{e}.hex'), 'w') as f:
            f.write(intel_hex(rom[e]))
        print(f'EEPROM{e}.bin  -> grave no chip {chip} do Decodificador de Controle')
    print()
    print(tabela_markdown())
