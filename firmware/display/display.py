#!/usr/bin/env python3
"""Gera o conteudo da EEPROM 28C16 do Display Decimal - Marcos Silva dos Santos (GPL-3.0).

Endereco: A10 = modo (0 = sem sinal 0..255, 1 = com sinal -128..127)
          A9..A8 = digito (0 = unidades/DIG4 ... 3 = DIG1 a esquerda)
          A7..A0 = valor do registrador OUT
Dados:    IO6=a IO5=b IO4=c IO3=d IO2=e IO1=f IO0=g IO7=ponto  (display catodo comum)
Zeros a esquerda ficam apagados.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'microcodigo'))
from microcodigo import intel_hex

DIGITOS = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B]
MENOS = 0x01      # segmento g
APAGADO = 0x00


def digitos_de(v):
    s = str(v)
    return [int(c) for c in s[::-1]]


def imagem():
    rom = bytearray(2048)
    for modo in (0, 1):
        for valor in range(256):
            v = valor if modo == 0 else (valor - 256 if valor > 127 else valor)
            d = digitos_de(abs(v))
            for pos in range(4):
                if pos < len(d):
                    seg = DIGITOS[d[pos]]
                elif v < 0 and pos == 3:
                    seg = MENOS
                else:
                    seg = APAGADO
                rom[(modo << 10) | (pos << 8) | valor] = seg
    return rom


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    rom = imagem()
    open(os.path.join(out, 'DISPLAY.bin'), 'wb').write(rom)
    open(os.path.join(out, 'DISPLAY.hex'), 'w').write(intel_hex(rom))
    print('DISPLAY.bin gerado (grave no U1 da placa Display Decimal)')
