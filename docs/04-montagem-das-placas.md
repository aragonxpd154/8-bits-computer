# 4. Montagem das placas — componente por componente

> Computador 8 Bits v3.0 — projeto de **Marcos Silva dos Santos** (MarcosObel). Licença GPL-3.0.

Antes de começar, tenha em mãos, para a placa que vai montar:
- o **guia de montagem** impresso (`hardware/fabricacao/<placa>/3-mascara-montagem-componentes.pdf`);
- a **lista de materiais** da placa (`lista-de-materiais.csv` na mesma pasta, ou [lista completa](lista-de-materiais-completa.md));
- o **esquemático** (`0-esquematico.pdf`).

## 4.1 Regras gerais (valem para todas as placas)

### Como identificar a orientação
| Componente | Marca na placa | No componente |
|---|---|---|
| CI / soquete | **pad quadrado = pino 1**; desenho com chanfro/meia-lua | chanfro ou bolinha marca o pino 1 |
| LED | **pad quadrado = cátodo (K)** | perna **curta** / lado chato do LED = cátodo |
| Capacitor eletrolítico / tântalo | **pad quadrado = +** | faixa com "−" = negativo; tântalo: marca/faixa = **positivo** |
| Diodo (1N5822) | **pad quadrado = cátodo** | faixa = cátodo |
| Rede resistiva SIP | **pad quadrado = pino 1 (comum)** | ponto/marca = pino 1 |
| Barra de pinos | pad quadrado = pino 1 | — |
| Capacitor cerâmico/poliéster, resistor | sem polaridade | — |

### Ordem de soldagem (do mais baixo para o mais alto)
1. **Resistores** e **redes resistivas** (SIP).
3. **Soquetes de CI** — **use soquete em todos os CIs** (principalmente nas EEPROMs, que você vai regravar). Respeite o chanfro.
4. **Capacitores cerâmicos/poliéster** (100 nF de desacoplamento ao lado de cada CI).
5. **LEDs** (deixe-os todos na mesma altura: solde uma perna, ajuste, depois a outra).
6. **Capacitores eletrolíticos/tântalo** (polaridade!).
7. **Barras de pinos** (conectores de 4 pinos).
8. **Chaves, botões, potenciômetro, display.**
9. **CIs nos soquetes** — só depois do teste de alimentação sem CIs (seção 4.2).

Todas as soldas são feitas **pela face de baixo** (a face com o texto `8BITS ...` em cobre). O furo metalizado já liga as duas faces.
Componentes ficam na face de cima, do lado da serigrafia.

### Boas práticas de solda
- Ferro limpo e estanhado, 330–360 °C. Encoste a ponta no pad **e** no terminal, 1–2 s, aplique o estanho, retire o estanho e depois o ferro. A solda deve ficar brilhante, em forma de "vulcão".
- Corte as pernas rente (≈1 mm) depois de soldar.
- Nos soquetes, solde primeiro dois pinos em cantos opostos, confira se o soquete está assentado e só então solde o resto.
- Após cada placa, limpe o fluxo com álcool isopropílico e uma escova de dentes velha.

## 4.2 Teste de alimentação (fazer em TODAS as placas)
1. **Sem nenhum CI nos soquetes**, ligue 5 V no conector `ALIMENTACAO` (J1): pinos 1 e 2 = +5 V, pinos 3 e 4 = GND.
2. Meça 5 V entre o pino de VCC e o pino de GND de **cada soquete**:

   | Encapsulamento | VCC | GND |
   |---|---|---|
   | DIP-8 (555) | 8 | 1 |
   | DIP-14 (74LS00/04/08/32/86/132, NE556) | 14 | 7 |
   | DIP-16 (74LS138/139/153/157/161/173/283, 74S189) | 16 | 8 |
   | DIP-20 (74LS245) | 20 | 10 |
   | DIP-24 (28C16) | 24 | 12 |

3. Desligue, insira os CIs (orientação!) e ligue de novo, de preferência com uma fonte com limite de corrente (~500 mA por placa). Se algum CI esquentar, desligue imediatamente e procure CI invertido ou curto.

> Dica: para os testes individuais abaixo, use jumpers macho-fêmea nas barras de pinos. "Nível alto" =
> ligar ao +5 V; "nível baixo" = ligar ao GND. **Entrada TTL desconectada é lida como nível ALTO.**

---

## 4.3 Montagem e teste de cada placa

Ordem recomendada de montagem (cada placa testada antes de seguir):
**Backplane → Clock → Reset → Contador de Passos → PC → RAM/MAR → IR → Controle → A → B → ULA → Saída → Display.**

### Backplane / Barramento (`backplane-barramento`)
- **O que tem:** entrada de 5 V (jack J1 *ou* borne J2), chave liga/desliga SW1, fusível rearmável F1 (PTC 3 A),
  diodo de proteção D1, capacitores C1/C2, LED de energia, 8 LEDs do barramento (D7…D0) e 45 conectores de 4 pinos.
- **Montagem:** resistores R1–R9 → C2 → LEDs → C1 (polaridade) → D1 (faixa no pad quadrado) → F1 → SW1 → J1/J2 → todos os conectores (pino 1 = pad quadrado, à esquerda).
- **Proteção contra inversão:** se a fonte for ligada invertida, D1 conduz e o PTC F1 abre. Desligue, corrija e espere esfriar.
- **Teste:** ligue a fonte de 5 V; LED1 acende; meça 5 V nos pinos 1–2 de cada conector `P_xxx`. Os LEDs do barramento ficam apagados (barramento solto).

### Clock astável/monoestável (`clock-astavel-monoestavel`)
- **CIs:** U1 NE556, U2 74LS00, U3 74LS04.
- **Atenção:** C1 é **tântalo 10 µF** (polaridade: o lado marcado do tântalo é o **positivo**). R1 agora é 1 kΩ (era 150 Ω).
- **Montagem:** R1, R2 (10 Ω), R4 (10 k), R5 (330 k), R6 → soquetes → C2, C3 (10 nF), C4 (330 nF), C5–C7 (100 nF) → C1 → LED1 → J1, J2 → RV1 (potenciômetro) → SW1 (PASSO) → SW2 (AUTO/MANUAL).
- **Teste:** ligue o pino 3 de J2 (HLT) ao **GND** com um jumper (HLT solto = relógio parado!). Em AUTO, LED1 pisca e o potenciômetro muda a velocidade (~0,7 Hz a ~140 Hz). Em MANUAL, cada toque em PASSO dá um pulso. Ligue HLT ao +5 V: o clock para.

### Reset (`reset-circuito`)
- **CI:** U1 **74LS132** (NAND Schmitt; um 74LS00 também funciona).
- **Montagem:** R1, R2 (10 k), R3 (1 k) → soquete → C2 → LED1 → C1 10 µF (polaridade) → J1, J2 → SW1.
- **Teste:** ao ligar, LED1 pisca (reset automático de ~0,1 s). Apertar RESET: LED1 acende, J2.1 (RST) = 5 V e J2.2 (/RST) = 0 V. J2.4 (/STCLR) vai a 0 V durante o reset **ou** quando J2.3 (/Y5) é aterrado.

### Contador de Passos (`fetch-contador-passos`)
- **CIs:** U1 74LS161, U2 74LS138.
- **Montagem:** R1–R3 (330 Ω), R4–R8 (470 Ω) → soquetes → C1, C2 → LED1–LED3 (amarelos, binário T2 T1 T0) → LED4–LED8 (passos T0…T4) → J1–J3.
- **Teste (sem a placa de reset):** /STCLR (J3.3) em +5 V, pulse /CLK (J3.2). Os LEDs de passo andam T0→T7 (só T0–T4 têm LED). Agora ligue J3.1 (/Y5) em J3.3 (/STCLR) com um jumper: o contador passa a voltar para T0 depois de T4.

### Contador de Programa — PC (`pc-contador-programa`)
- **CIs:** U1 74LS161, U2 74LS245.
- **Montagem:** R1–R4 → soquetes → C1, C2 → LED1–LED4 (P3…P0) → J1–J5.
- **Teste:** /RST (J2.4) e /JMP (J2.3) em +5 V, PCI (J2.1) em +5 V. A cada pulso em CLK (J2.2) os LEDs contam 0…15. PCI em GND: para de contar. /PCO (J3.1) em GND: o valor aparece em BUS_L (J4); BUS_H (J5) fica em 0.

### RAM e MAR (`ram-mar-memoria`)
- **CIs:** U1, U2 74S189 · U3, U4 74LS04 · U5 74LS245 · U6 74LS173 (MAR) · U7–U10 74LS157 · U11 74LS00 · U12 NE555.
- **Montagem:** resistores R1–R18 → RN1 (SIP-9) e RN2 (SIP-5) com o **pino 1 (comum) no pad quadrado** → soquetes → C1–C12 (100 nF), C13 (1 nF), C14 (10 nF) → LEDs (verdes = dado, amarelos = endereço, vermelho LED13 = PROG, verde LED14 = RUN) → J1–J5 → SW1 (DIP 4), SW3 (DIP 8), SW4 (GRAVAR), SW2 (PROG/RUN).
- **Chaves DIP (mudança da v3.0):** chave **LIGADA = 1**. A chave 1 é o bit 0.
- **Teste de programação manual:** SW2 em PROG (LED vermelho). Escolha o endereço em SW1 e o dado em SW3, aperte GRAVAR: os LEDs verdes mostram o dado gravado. Mude o endereço e volte: o dado continua lá. Ligue /RMO (J3.3) ao GND e veja o dado em BUS_L/BUS_H.

### Registrador de Instrução — IR (`ir-registrador-instrucao`)
- **CIs:** U1, U2 74LS173, U3 74LS245.
- **Montagem:** R1–R8 → soquetes → C1–C3 → LED1–LED8 (LED1–4 = opcode, LED5–8 = operando) → J1–J5.
- **Teste:** coloque um valor em BUS_L/BUS_H com jumpers, /IRI (J2.2) em GND e dê um pulso de CLK: os LEDs mostram o valor. RST (J2.3) em +5 V apaga. Com /IRO (J2.4) em GND, só o **nibble baixo** volta ao barramento (o alto sai como 0).

### Decodificador de Controle (`cd-decodificador-controle`)
- **CIs:** U1 = EEPROM2.bin, U2 = EEPROM1.bin, U3 = EEPROM0.bin (28C16 / AT28C16). **Grave antes** ([6. Gravação](06-gravacao-das-eeproms.md)) e marque cada chip com uma etiqueta.
- **Correção crítica da v3.0:** o pino 21 (/WE) agora vai ao +5 V. Na placa antiga ele estava no GND.
- **Montagem:** R1, R2 (10 k) → soquetes de 24 pinos **largos (600 mil)** → C1–C3 → J1–J9.
- **Teste:** com PASSO (J2) e OPCODE (J3) todos em GND (instrução NOP, passo T0), os sinais ativos devem ser apenas `/PCO` e `/MAI` (nível **baixo** em J6.1 e J5.4); os demais sinais ativos-baixos ficam em 5 V e os ativos-altos em 0 V. Use a tabela de sinais em [1. Arquitetura](01-arquitetura.md).

### Registrador A (`acc-registrador-a`) e Registrador B (`b-registrador-b`)
- **CIs:** U1, U2 74LS173, U3 74LS245 (as duas placas são idênticas, mudam só os nomes dos sinais).
- **Montagem:** R1–R8 → soquetes → C1–C3 → LED1–LED8 (LED1 = bit 7, à esquerda) → J1–J6.
- **Teste:** igual ao IR, com /ACI (ou /BRI) e /ACO. As saídas ALU_L/ALU_H (J5/J6) mostram sempre o conteúdo.

### Unidade Lógica e Aritmética — ULA (`alu-unidade-logica-aritmetica`)
- **CIs:** U1, U2 74LS283 · U3, U4, U10, U12 74LS86 · U5, U6 74LS08 · U7, U8, U9, U11 74LS32 · U13–U16 74LS153 · U17 74LS245 · U18 74LS04 (novo, buffer de SUB/NOT).
- **Atenção:** é a placa com mais CIs (18). Confira **duas vezes** o tipo de cada CI antes de inserir — 74LS08, 74LS32 e 74LS86 têm a mesma pinagem e são fáceis de confundir.
- **Montagem:** R1–R8 → 18 soquetes → C1–C18 → LED1–LED8 → J1–J9.
- **Teste (com A e B ligadas pelos cabos diretos, ou com jumpers):**

  | AL1 | AL0 | SUB | NOT | Resultado nos LEDs |
  |---|---|---|---|---|
  | 0 | 0 | 0 | 0 | A + B |
  | 0 | 0 | 1 | 0 | A − B |
  | 0 | 1 | 0 | 0 | A AND B |
  | 1 | 0 | 0 | 0 | A OR B |
  | 1 | 1 | 0 | 0 | A XOR B |
  | 1 | 1 | 0 | 1 | NOT A |

### Registrador de Saída — OUT (`out-registrador-saida`)
- **CIs:** U1, U2 74LS173. Sem 74LS245 (não escreve no barramento).
- **Montagem:** R1–R8 → soquetes → C1, C2 → LEDs → J1–J6.
- **Teste:** como o registrador A, usando /ORI.

### Display Decimal (`display-decimal`)
- **CIs:** U1 = DISPLAY.bin (28C16), U2 NE555, U3 74LS161, U4 74LS139. **DS1 = display de 4 dígitos 0,4" CÁTODO COMUM** (12 pinos).
- **Atenção:** o display tem de ser **cátodo comum** (ex.: 5641AS / FJ4401AH / CC 0,4"). Um de ânodo comum não acende com este circuito. Confira a pinagem do seu display no datasheet: 1=e 2=d 3=dp 4=c 5=g 6=DIG4 7=b 8=DIG3 9=DIG2 10=f 11=a 12=DIG1, fileiras distantes 12,7 mm.
- **Montagem:** R1 (1 k), R10 (100 k), R2–R9 (100 Ω, segmentos) → soquetes → C1–C6 → J1–J3 → SW1 → DS1 (pode usar barra de pinos fêmea como soquete).
- **Teste:** com as entradas (J2/J3) em GND o display mostra **0**; com todas em +5 V mostra **255** (chave em "sem sinal") ou **-1** (chave em "com sinal").

---
Anterior: [3. Fabricação das placas](03-fabricacao-das-placas.md) · Próximo: [5. Interligação e backplane](05-interligacao-e-backplane.md)
