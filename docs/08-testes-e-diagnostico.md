# 8. Testes e diagnóstico

> Projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

## 8.1 Ferramentas
- Multímetro (tensão e continuidade).
- **Ponta de prova lógica** simples: um LED + resistor de 1 kΩ num jumper (acende = nível alto).
- Jumpers macho-fêmea para forçar níveis (+5 V / GND) nas barras de pinos.
- Clock em **MANUAL**: o computador pode ser executado um passo por vez, indefinidamente devagar.
- O **emulador** (`firmware/ferramentas/emulador.py --passos`) mostra, passo a passo, o que cada LED deveria mostrar — compare com a placa real.

## 8.2 Subida do sistema (bring-up) em etapas

| Etapa | Ligue | O que deve acontecer |
|---|---|---|
| 1 | Backplane | LED de energia aceso; 5,0 V (4,75–5,25 V) em todos os `P_xxx` |
| 2 | + Clock (HLT ligado ao backplane) | LED do clock pisca em AUTO; com o Controle ainda sem EEPROMs, HLT fica solto e o clock **para** — normal |
| 3 | + Reset + Passos | LEDs T0…T4 andam e voltam a T0; RESET leva a T0 |
| 4 | + PC | PC só conta com PCI; teste forçando PCI = 1 com jumper no conector C_PC1 do backplane |
| 5 | + RAM/MAR | grave e leia valores em PROG (seção 7.3) |
| 6 | + IR + Controle (EEPROMs gravadas) | em T0/T1 o IR recebe o byte da RAM; o PC incrementa em T1 |
| 7 | + A, B, ULA, Saída, Display | rode `01-soma.asm` passo a passo e compare com o emulador |

## 8.3 Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Nada acende; PTC quente | fonte invertida ou curto | desligue, confira polaridade (centro +), procure curto entre +5 V e GND |
| Clock não pisca | HLT solto (nível alto = parado) | ligue o cabo C_CLOCK ao backplane (HLT vem do Controle) ou aterre HLT para testar |
| Clock "pula" passos no MANUAL | toque longo no botão PASSO | o monoestável dá ~0,12 s por pulso; solte o botão entre toques |
| Passos não voltam a T0 | cabo C_FETCH ou C_RESET invertido; /Y5 não chega à placa de Reset | confira os dois cabos (pino 1 com pino 1) |
| Reset não funciona / LED de reset sempre aceso | botão invertido, C1 invertido | confira C1 (polaridade) e SW1 |
| Barramento com valor "estranho", CIs 74LS245 quentes | dois módulos escrevendo ao mesmo tempo | EEPROMs trocadas (U1/U2/U3) ou gravadas com o microcódigo antigo; regrave com os `.bin` da v3.0 |
| Instruções erradas (ex.: LDA age como OR) | opcode chegando invertido | o cabo IR→Controle deve ser reto (OP3 no pino 1 dos dois lados) |
| ULA só faz XOR | AL0/AL1 não chegam | placa ULA antiga (1.0V) ou cabo C_ALU1 desligado |
| Subtração errada no bit 0 | carry de entrada (SUB) não chega ao 74LS283 | confira U18 (buffer) e o cabo C_ALU1 |
| RAM grava sozinha / perde dados | RMI ruidoso, C13/R18 do pulso de escrita | confira C13 = 1 nF e R18 = 1 kΩ; desacoplamento perto do 74S189 |
| Chaves DIP sem efeito | RN1/RN2 invertidas (pino 1 = comum) | o pino comum da rede resistiva vai no pad quadrado |
| Display apagado | display de ânodo comum, ou EEPROM do display não gravada | use display **cátodo comum**; grave `DISPLAY.bin` |
| Display tremendo/fantasma | varredura lenta ou rápida demais | ajuste R10/C5 (padrão 100 kΩ/15 nF ≈ 470 Hz) |
| Comportamento aleatório em clock alto | ruído na alimentação | acrescente 100 µF/10 V perto do J1 de cada placa, use cabos curtos |

## 8.4 Medidas de referência
- Alimentação em cada placa: **4,75 V a 5,25 V** (família 74LS).
- Nível alto TTL: ≥ 2,4 V; nível baixo: ≤ 0,4 V (com LEDs nas saídas, alto pode ficar entre 3 V e 4 V — normal).
- Corrente total típica: 1,0–1,4 A.

---
Anterior: [7. Programação e uso](07-programacao-e-uso.md) · Voltar ao [índice da documentação](README.md)
