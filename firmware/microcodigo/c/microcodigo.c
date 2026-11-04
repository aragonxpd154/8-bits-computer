/*
 * Gerador do microcodigo - Computador 8 Bits v3.0
 * Autor: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
 *
 * Versao em C para Linux (Zorin OS / Ubuntu) do gerador original de 2021.
 * Compilar:  gcc -O2 -o microcodigo microcodigo.c
 * Executar:  ./microcodigo        (gera EEPROM0.bin, EEPROM1.bin, EEPROM2.bin com 2048 bytes)
 *
 * Endereco: A8=ZF A7=CF A6..A3=opcode A2..A0=passo.
 * Sinais ativos em nivel baixo sao invertidos pela mascara ATIVO_BAIXO_n.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* sinal = (eeprom << 8) | mascara */
#define HLT ((2 << 8) | 0x80)
#define PCI ((2 << 8) | 0x40)
#define JMP ((2 << 8) | 0x20)
#define PCO ((2 << 8) | 0x10)
#define MAI ((2 << 8) | 0x08)
#define RMI ((2 << 8) | 0x04)
#define RMO ((2 << 8) | 0x02)
#define IRI ((2 << 8) | 0x01)
#define IRO ((1 << 8) | 0x80)
#define ACO ((1 << 8) | 0x40)
#define ACI ((1 << 8) | 0x20)
#define SUB ((1 << 8) | 0x10)
#define AL1 ((1 << 8) | 0x08)
#define AL0 ((1 << 8) | 0x04)
#define ALU ((1 << 8) | 0x02)
#define NOT ((1 << 8) | 0x01)
#define BRI ((0 << 8) | 0x80)
#define ORI ((0 << 8) | 0x40)

static const uint8_t ATIVO_BAIXO[3] = { 0xC0, 0xE2, 0x3B }; /* EEPROM0, EEPROM1, EEPROM2 */

#define MAXS 6
typedef struct { int n; int s[MAXS]; } passo_t;
#define P(...) { sizeof((int[]){__VA_ARGS__}) / sizeof(int), { __VA_ARGS__ } }
#define VAZIO { 0, { 0 } }

/* passos T2..T4 de cada opcode (T0/T1 = busca, iguais para todos). */
static const passo_t prog[16][3] = {
    /* 0 NOP */ { VAZIO, VAZIO, VAZIO },
    /* 1 LDA */ { P(IRO, MAI), P(RMO, ACI), VAZIO },
    /* 2 LDI */ { P(IRO, ACI), VAZIO, VAZIO },
    /* 3 STA */ { P(IRO, MAI), P(ACO, RMI), VAZIO },
    /* 4 ADD */ { P(IRO, MAI), P(RMO, BRI), P(ALU, ACI) },
    /* 5 SUB */ { P(IRO, MAI), P(RMO, BRI), P(ALU, SUB, ACI) },
    /* 6 AND */ { P(IRO, MAI), P(RMO, BRI), P(ALU, AL0, ACI) },
    /* 7 OR  */ { P(IRO, MAI), P(RMO, BRI), P(ALU, AL1, ACI) },
    /* 8 XOR */ { P(IRO, MAI), P(RMO, BRI), P(ALU, AL1, AL0, ACI) },
    /* 9 NOT */ { P(ALU, AL1, AL0, NOT, ACI), VAZIO, VAZIO },
    /* A JMP */ { P(IRO, JMP), VAZIO, VAZIO },
    /* B JC  */ { VAZIO, VAZIO, VAZIO },   /* tratado abaixo (depende de CF) */
    /* C JZ  */ { VAZIO, VAZIO, VAZIO },   /* tratado abaixo (depende de ZF) */
    /* D --  */ { VAZIO, VAZIO, VAZIO },
    /* E OUT */ { P(ACO, ORI), VAZIO, VAZIO },
    /* F HLT */ { P(HLT), VAZIO, VAZIO },
};
static const passo_t busca[2] = { P(PCO, MAI), P(RMO, IRI, PCI) };
static const passo_t salto = P(IRO, JMP);

static uint8_t rom[3][2048];

static void aplica(int addr, const passo_t *p)
{
    for (int i = 0; i < p->n; i++)
        rom[p->s[i] >> 8][addr] |= (uint8_t)(p->s[i] & 0xFF);
}

int main(void)
{
    memset(rom, 0, sizeof rom);
    for (int addr = 0; addr < 2048; addr++) {
        int passo = addr & 7, op = (addr >> 3) & 15, cf = (addr >> 7) & 1, zf = (addr >> 8) & 1;
        if (passo < 2)
            aplica(addr, &busca[passo]);
        else if (passo < 5) {
            if (op == 0xB) { if (cf && passo == 2) aplica(addr, &salto); }
            else if (op == 0xC) { if (zf && passo == 2) aplica(addr, &salto); }
            else aplica(addr, &prog[op][passo - 2]);
        }
        for (int e = 0; e < 3; e++)
            rom[e][addr] ^= ATIVO_BAIXO[e];
    }
    for (int e = 0; e < 3; e++) {
        char nome[32];
        snprintf(nome, sizeof nome, "EEPROM%d.bin", e);
        FILE *f = fopen(nome, "wb");
        if (!f) { perror(nome); return 1; }
        fwrite(rom[e], 1, sizeof rom[e], f);
        fclose(f);
    }
    printf("Arquivos binarios gerados com sucesso! (EEPROM2 -> U1, EEPROM1 -> U2, EEPROM0 -> U3)\n");
    return 0;
}
