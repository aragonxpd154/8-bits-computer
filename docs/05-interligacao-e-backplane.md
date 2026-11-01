# 5. Interligação: backplane, cabos e montagem na base

> Projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

## 5.1 Ideia geral

Cada módulo tem conectores de 4 pinos (barra de pinos 2,54 mm). O **backplane** (pasta
`backplane-barramento`, antiga "ASSEMBLY LAYOUT") é a placa-mãe: recebe os 5 V, distribui a
alimentação, contém o **barramento D0…D7** (com 8 LEDs) e roteia **todos** os sinais de controle.

Regras simples:
1. **Todos os cabos são de 4 vias e RETOS** — pino 1 de uma ponta no pino 1 da outra (fio da mesma cor sempre no pino 1).
2. No backplane, os conectores estão **agrupados por módulo**, com o nome do módulo ao lado
   (CLOCK, RESET, PC, RAM/MAR, IR, CONTROLE, PASSOS, REG. A, ULA, REG. B, SAÍDA, DISPLAY).
3. Cada conector tem o mesmo nome e a mesma ordem de sinais do conector correspondente no módulo
   (impressos na serigrafia, embaixo de cada pino).
4. São **52 cabos**: 44 vão do módulo ao backplane e 8 são **diretos** entre módulos vizinhos.

## 5.2 Arranjo físico sugerido

Monte os módulos numa base de MDF/acrílico (~60 × 45 cm) com espaçadores M3 de 10 mm, no mesmo
arranjo do diagrama de blocos — assim todos os cabos de 20 cm alcançam:

```
            +--------------------- BASE ~60 x 45 cm ---------------------+
            |  [RESET]                                [ENTRADA 5 V]      |
            |  [CLOCK]                                                  |
            |  [PC]                                   [REG. A]          |
            |  [RAM/MAR]          [ BACKPLANE ]       [ULA]             |
            |  [IR]               [ D0..D7    ]       [REG. B]          |
            |  [CONTROLE]                             [SAIDA]           |
            |  [PASSOS]                               [DISPLAY]         |
            +------------------------------------------------------------+
```

- O **Controle** fica logo abaixo do **IR** (cabo direto do opcode) e acima de **Passos** (cabo direto T0…T2).
- A **ULA** fica entre **A** e **B** (dois cabos diretos de cada lado); o **Display** abaixo da **Saída**.

## 5.3 Alimentação

- Use uma **fonte regulada de 5 V, 2 A ou mais** (3 A recomendado), plugue P4 5,5 × 2,1 mm,
  **centro positivo** — ou ligue os fios no borne J2.
- Consumo típico do computador completo: **1,0 a 1,4 A** (depende de quantos LEDs estão acesos).
- **Não use fonte de 9 V/12 V**: não há regulador. O diodo D1 + PTC F1 protegem apenas contra
  inversão de polaridade e curto.
- Cada cabo de alimentação leva +5 V em 2 fios e GND em 2 fios, então a queda de tensão é desprezível.

## 5.4 Tabela de cabos

<!-- tabela gerada por tools/gerar_docs.py -->
| # | Placa | Conector | Sinais (pino 1 -> 4) | Liga em |
|---:|---|---|---|---|
| 1 | Clock | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J12** (P_CLOCK) |
| 2 | Clock | J2 CLOCK | `CLK /CLK HLT NC` | Backplane **J45** (C_CLOCK) |
| 3 | Reset | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J13** (P_RESET) |
| 4 | Reset | J2 RESET | `RST /RST /Y5 /STCLR` | Backplane **J46** (C_RESET) |
| 5 | Contador de Programa | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J8** (P_PC) |
| 6 | Contador de Programa | J2 CONTROLE | `PCI CLK /JMP /RST` | Backplane **J33** (C_PC1) |
| 7 | Contador de Programa | J3 CONTROLE2 | `/PCO NC NC NC` | Backplane **J34** (C_PC2) |
| 8 | Contador de Programa | J4 BUS_L | `D0 D1 D2 D3` | Backplane **J20** (BL_PC) |
| 9 | Contador de Programa | J5 BUS_H | `D4 D5 D6 D7` | Backplane **J27** (BH_PC) |
| 10 | RAM e MAR | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J9** (P_RAM) |
| 11 | RAM e MAR | J2 CONTROLE1 | `CLK /MAI RST RMI` | Backplane **J35** (C_RAM1) |
| 12 | RAM e MAR | J3 CONTROLE2 | `/WE /CLK /RMO RUN` | Backplane **J36** (C_RAM2) |
| 13 | RAM e MAR | J4 BUS_L | `D0 D1 D2 D3` | Backplane **J21** (BL_RAM) |
| 14 | RAM e MAR | J5 BUS_H | `D4 D5 D6 D7` | Backplane **J28** (BH_RAM) |
| 15 | Reg. Instrucao | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J6** (P_IR) |
| 16 | Reg. Instrucao | J2 CONTROLE | `CLK /IRI RST /IRO` | Backplane **J31** (C_IR) |
| 17 | Reg. Instrucao | J3 BUS_L | `D0 D1 D2 D3` | Backplane **J18** (BL_IR) |
| 18 | Reg. Instrucao | J4 BUS_H | `D4 D5 D6 D7` | Backplane **J25** (BH_IR) |
| 19 | Reg. Instrucao | J5 OPCODE | `OP3 OP2 OP1 OP0` | **cabo direto** -> Decodificador de Controle J3 (OPCODE) |
| 20 | Decodificador de Controle | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J10** (P_CD) |
| 21 | Decodificador de Controle | J5 CTRL_A | `/IRI /RMO RMI /MAI` | Backplane **J39** (CD_A) |
| 22 | Decodificador de Controle | J6 CTRL_B | `/PCO /JMP PCI HLT` | Backplane **J40** (CD_B) |
| 23 | Decodificador de Controle | J7 CTRL_C | `NOT /ALUO AL0 AL1` | Backplane **J41** (CD_C) |
| 24 | Decodificador de Controle | J8 CTRL_D | `SUB /ACI /ACO /IRO` | Backplane **J42** (CD_D) |
| 25 | Decodificador de Controle | J9 CTRL_E | `/BRI /ORI E0_5 E0_4` | Backplane **J43** (CD_E) |
| 26 | Contador de Passos | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J11** (P_FETCH) |
| 27 | Contador de Passos | J2 PASSO | `T0 T1 T2 NC` | **cabo direto** -> Decodificador de Controle J2 (PASSO) |
| 28 | Contador de Passos | J3 CONTROLE | `/Y5 /CLK /STCLR NC` | Backplane **J44** (C_FETCH) |
| 29 | Registrador A | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J3** (P_ACC) |
| 30 | Registrador A | J2 CONTROLE | `CLK /ACI RST /ACO` | Backplane **J29** (C_ACC) |
| 31 | Registrador A | J3 BUS_L | `D0 D1 D2 D3` | Backplane **J15** (BL_ACC) |
| 32 | Registrador A | J4 BUS_H | `D4 D5 D6 D7` | Backplane **J22** (BH_ACC) |
| 33 | Registrador A | J5 ALU_L | `A0 A1 A2 A3` | **cabo direto** -> ULA J4 (ACC_L) |
| 34 | Registrador A | J6 ALU_H | `A4 A5 A6 A7` | **cabo direto** -> ULA J5 (ACC_H) |
| 35 | Registrador B | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J4** (P_B) |
| 36 | Registrador B | J2 CONTROLE | `CLK /BRI RST /BRO` | Backplane **J30** (C_B) |
| 37 | Registrador B | J3 BUS_L | `D0 D1 D2 D3` | Backplane **J16** (BL_B) |
| 38 | Registrador B | J4 BUS_H | `D4 D5 D6 D7` | Backplane **J23** (BH_B) |
| 39 | Registrador B | J5 ALU_L | `B0 B1 B2 B3` | **cabo direto** -> ULA J6 (B_L) |
| 40 | Registrador B | J6 ALU_H | `B4 B5 B6 B7` | **cabo direto** -> ULA J7 (B_H) |
| 41 | ULA | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J5** (P_ALU) |
| 42 | ULA | J2 BUS_L | `D0 D1 D2 D3` | Backplane **J17** (BL_ALU) |
| 43 | ULA | J3 BUS_H | `D4 D5 D6 D7` | Backplane **J24** (BH_ALU) |
| 44 | ULA | J8 CTRL1 | `/ALUO SUB AL0 AL1` | Backplane **J37** (C_ALU1) |
| 45 | ULA | J9 CTRL2 | `NOT CARRY NC NC` | Backplane **J38** (C_ALU2) |
| 46 | Registrador de Saida | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J7** (P_OUT) |
| 47 | Registrador de Saida | J2 CONTROLE | `CLK /ORI RST NC` | Backplane **J32** (C_OUT) |
| 48 | Registrador de Saida | J3 BUS_L | `D0 D1 D2 D3` | Backplane **J19** (BL_OUT) |
| 49 | Registrador de Saida | J4 BUS_H | `D4 D5 D6 D7` | Backplane **J26** (BH_OUT) |
| 50 | Registrador de Saida | J5 DISPLAY_L | `O0 O1 O2 O3` | **cabo direto** -> Display Decimal J2 (ENTRADA_L) |
| 51 | Registrador de Saida | J6 DISPLAY_H | `O4 O5 O6 O7` | **cabo direto** -> Display Decimal J3 (ENTRADA_H) |
| 52 | Display Decimal | J1 ALIMENTACAO | `+5V +5V GND GND` | Backplane **J14** (P_DISPLAY) |

### Pinos que mudam de nome de propósito
- **Reg. B J2 pino 4 (/BRO):** no backplane vai fixo em +5 V — o registrador B nunca escreve no barramento.
- **RAM J3 pinos 1, 2 e 4 (/WE, /CLK, RUN):** são **saídas de teste** da placa de RAM; no backplane esses pinos não estão ligados.
- **ULA J9 pino 2 (CARRY):** reservado para o futuro registrador de flags (não ligado no backplane).
- **Controle J4 (FLAGS):** fica livre até existir a placa de flags (pull-down interno = flags em 0).
- **Backplane EXPANSAO:** E0_5, E0_4 (saídas livres da EEPROM0), CLK e RST para futuras extensões.

## 5.5 Ordem de ligação recomendada
1. Backplane sozinho → confira os 5 V e o LED de energia.
2. Clock + Reset → observe o LED do clock e o reset.
3. Passos → os LEDs T0…T4 devem andar com o clock (com o Reset ligado, voltam a T0 depois de T4).
4. PC, RAM/MAR, IR, Controle (com as EEPROMs gravadas).
5. A, B, ULA, Saída, Display.
6. Programe a RAM e rode o primeiro programa (veja [7. Programação e uso](07-programacao-e-uso.md)).

---
Anterior: [4. Montagem das placas](04-montagem-das-placas.md) · Próximo: [6. Gravação das EEPROMs](06-gravacao-das-eeproms.md)
