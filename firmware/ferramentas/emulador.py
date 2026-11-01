#!/usr/bin/env python3
"""Emulador em nivel de sinais do Computador 8 Bits - Marcos Silva dos Santos (GPL-3.0).

Executa um programa usando os ARQUIVOS BINARIOS REAIS das EEPROMs (EEPROM0/1/2.bin), decodificando
cada sinal de controle com a polaridade do hardware. Detecta conflito no barramento.

Uso:  python3 emulador.py programa.asm|programa.bin [--passos] [--max N]
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'microcodigo'))
sys.path.insert(0, HERE)
import microcodigo as mc

ROMDIR = os.path.join(HERE, '..', 'microcodigo')


class Computador:
    def __init__(self, ram, romdir=ROMDIR, cf=0, zf=0):
        self.rom = {e: open(os.path.join(romdir, f'EEPROM{e}.bin'), 'rb').read() for e in (0, 1, 2)}
        self.ram = list(ram) + [0] * (16 - len(ram))
        self.pc = self.mar = self.ir = self.a = self.b = self.out = 0
        self.passo = 0
        self.parado = False
        self.saidas = []
        self.cf, self.zf = cf, zf
        self.ciclos = 0

    def sinais(self):
        addr = (self.zf << 8) | (self.cf << 7) | ((self.ir >> 4) << 3) | self.passo
        s = set()
        for sig, nome in mc.NOMES.items():
            e, m = sig
            nivel = 1 if self.rom[e][addr] & m else 0
            ativo_baixo = mc.ATIVO_BAIXO[e] & m
            if (nivel == 0) if ativo_baixo else (nivel == 1):
                s.add(nome)
        return s

    def ula(self, s):
        sel = (2 if 'AL1' in s else 0) | (1 if 'AL0' in s else 0)
        if sel == 0:
            sub = 1 if 'SUB' in s else 0
            return (self.a + ((self.b ^ (0xFF if sub else 0)) & 0xFF) + sub) & 0xFF
        if sel == 1:
            return self.a & self.b
        if sel == 2:
            return self.a | self.b
        return self.a ^ (self.b | (0xFF if 'NOT' in s else 0))

    def ciclo(self, verbose=False):
        s = self.sinais()
        fontes = {'PCO': self.pc & 0x0F, 'RMO': self.ram[self.mar], 'IRO': self.ir & 0x0F, 'ACO': self.a,
                  'ALU': self.ula(s)}
        ativas = [k for k in fontes if k in s]
        if len(ativas) > 1:
            raise RuntimeError(f'CONFLITO no barramento: {ativas} (IR={self.ir:02X} passo T{self.passo})')
        bus = fontes[ativas[0]] if ativas else None
        if verbose:
            print(f'  T{self.passo} PC={self.pc:2d} MAR={self.mar:2d} IR={self.ir:02X} A={self.a:3d} B={self.b:3d} '
                  f'bus={"--" if bus is None else f"{bus:3d}"}  {" ".join(sorted(s))}')
        if 'HLT' in s:
            self.parado = True
            return
        # borda de subida do clock
        need = {'MAI', 'RMI', 'IRI', 'ACI', 'BRI', 'ORI', 'JMP'} & s
        if need and bus is None:
            raise RuntimeError(f'leitura com barramento flutuando: {need}')
        mar, ram, ir, a, b, pc = self.mar, list(self.ram), self.ir, self.a, self.b, self.pc
        if 'MAI' in s: mar = bus & 0x0F
        if 'RMI' in s: ram[self.mar] = bus
        if 'IRI' in s: ir = bus
        if 'ACI' in s: a = bus
        if 'BRI' in s: b = bus
        if 'ORI' in s:
            self.out = bus
            self.saidas.append(bus)
        if 'JMP' in s: pc = bus & 0x0F
        elif 'PCI' in s: pc = (self.pc + 1) & 0x0F
        self.mar, self.ram, self.ir, self.a, self.b, self.pc = mar, ram, ir, a, b, pc
        # borda de descida: contador de passos (reinicia em T5)
        self.passo = (self.passo + 1) % mc.PASSOS_POR_INSTRUCAO
        self.ciclos += 1

    def rodar(self, max_ciclos=5000, verbose=False, max_saidas=None):
        while not self.parado and self.ciclos < max_ciclos:
            self.ciclo(verbose)
            if max_saidas and len(self.saidas) >= max_saidas:
                break
        return self.saidas


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    f = sys.argv[1]
    if f.endswith('.asm'):
        import montador
        ram = montador.montar(open(f, encoding='utf-8').read())[0]
    else:
        ram = list(open(f, 'rb').read())
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 2000
    c = Computador(ram)
    c.rodar(mx, verbose='--passos' in sys.argv, max_saidas=None)
    print('Saidas no display:', c.saidas[:40], '...' if len(c.saidas) > 40 else '')
    print('Parou (HLT)' if c.parado else f'Nao parou em {mx} ciclos (laco infinito?)', f'- ciclos: {c.ciclos}')
