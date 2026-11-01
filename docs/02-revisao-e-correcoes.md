# 2. Revisão do projeto original e correções da versão 3.0

> Projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

A versão 3.0 partiu das últimas versões em EasyEDA de cada módulo (pastas originais `1.0V`, `2.0V`,
`2.1V`, `3.0V`, preservadas no Git na tag `v2-easyeda`). Todas as netlists originais foram lidas e
comparadas automaticamente, pino a pino, com a nova descrição em KiCad. As placas **A, B, IR, OUT,
Contador de Passos e Clock** ficaram eletricamente idênticas às originais; nas demais, as únicas
diferenças são exatamente as correções abaixo.

## 2.1 Erros que impediam o computador de funcionar

| # | Módulo | Problema encontrado | Correção na v3.0 |
|---|---|---|---|
| 1 | **ULA** (1.0V) | As entradas de seleção **A/B (pinos 14 e 2) dos quatro 74LS153** — sinais AL0/AL1 — não estavam ligadas a nenhum conector. Entrada TTL solta = nível alto, então a ULA ficaria presa em "XOR" e **nunca somaria**. | AL0 e AL1 levados ao conector CTRL1 (pinos 3 e 4) e ao backplane. |
| 2 | **ULA** (1.0V) | As saídas **2Y de U5 e U6** (AND dos bits 1 e 5) estavam ligadas ao **GND**, junto com as entradas 2C1 de U13 e U15. Isso é um curto-circuito de saída sempre que o AND der 1, e a operação AND perdia os bits 1 e 5. | Redes `AND1`/`AND5` criadas: U5.6 → U13.11 e U6.6 → U15.11. |
| 3 | **Decodificador de Controle** (1.0V) | O pino **/WE (21) das três EEPROMs estava no GND**. O datasheet só garante leitura com /WE em nível alto; com /WE baixo a EEPROM fica fora do modo de leitura especificado e qualquer ruído em /OE pode disparar uma escrita (corrompendo o microcódigo). | /WE ligado ao +5 V. |
| 4 | **Microcódigo** (2021) | O código gravava **0 nos passos sem sinal**, mas /ACO, /IRO, /RMO, /ALUO, /PCO, /ACI, /BRI, /ORI, /MAI, /IRI e /JMP são **ativos em nível baixo**. Resultado: em todo passo "vazio" quatro módulos escreveriam no barramento ao mesmo tempo. O emulador mostra o conflito já no primeiro passo: `RMO, IRO, ACO, ALU`. | Microcódigo reescrito em lógica positiva com máscara de inversão por EEPROM (`ATIVO_BAIXO`). |
| 5 | **Reset** (1.0V) | O botão de reset usava um **resistor de 10 kΩ para o GND** numa entrada TTL. Uma entrada 74LS "puxa" ~0,4 mA para fora; com 10 kΩ a tensão fica acima de 1,4 V e é lida como **nível alto** → **reset permanentemente ativo**. | Botão ligado ao GND com pull-up de 10 kΩ (lógica do primeiro gate invertida); 74LS132 (Schmitt) recomendado; reset automático ao ligar; LED indicador. Placa de reset ganhou PCB (antes só tinha esquemático). |
| 6 | **Ordem do opcode** | O conector "REGIST." do IR tem o bit 7 no pino 1, mas o Decodificador ligava o pino 1 ao A3 (bit menos significativo do opcode). Com cabo reto, todos os opcodes chegariam **espelhados** (LDA = 0001 viraria 1000). | Conector OPCODE do Decodificador agora tem OP3 no pino 1 → cabo reto funciona. |
| 7 | **Display** | Não existia o conteúdo da EEPROM de conversão binário→decimal. | Gerador `firmware/display/display.py` (sem sinal e com sinal, zeros à esquerda apagados). |
| 8 | **Display** | O 74LS139 acende o dígito colocando o comum em **nível baixo** → o display precisa ser **cátodo comum**. | Especificado na lista de materiais e na serigrafia. |
| 9 | **Montagem** (pasta ASSEMBLY LAYOUT vazia) | Não havia nada interligando os módulos. | **Backplane** novo + tabela com os 52 cabos de 4 vias, verificada pino a pino. |

## 2.2 Melhorias de confiabilidade

| Módulo | Melhoria |
|---|---|
| ULA | **U18 74LS04 como buffer** de SUB e NOT: cada um desses sinais aciona 8–9 entradas TTL, mais do que a saída da EEPROM consegue drenar (≈2 mA). |
| ULA | **CARRY** (C4 do somador alto) disponível no conector CTRL2 para um futuro registrador de flags. |
| RAM | Pino THR (6) do 555 da chave PROG/RUN estava solto → ligado ao GND; CV com 10 nF. |
| RAM | Chaves DIP agora vão ao +5 V com redes de pull-down de 1 kΩ: **chave ligada = 1** (antes era invertido e as entradas ficavam flutuando). |
| RAM | Entradas não usadas do 74LS157 (U10) aterradas. Barramento entra e sai pelos mesmos 2 conectores (antes eram 5). |
| Contador de Passos | LEDs de passo agora acendem no passo **ativo** (antes acendiam os inativos) e ganharam resistores; entradas de carga do 74LS161 aterradas. |
| Contador de Programa | Alimentação em conector próprio (antes misturada com /PCO); o 74LS245 coloca 0 no nibble alto do barramento durante /PCO. |
| Clock | R1 de 150 Ω para 1 kΩ (corrente do pino de descarga do 556). |
| Decodificador | Linhas A7/A8 (CF/ZF) em conector FLAGS com pull-down → `JC`/`JZ` já funcionam quando a placa de flags existir. |
| Display | Resistores de 100 Ω em série com os segmentos; metade não usada do 74LS139 com entradas fixadas. |
| Todos | Desacoplamento de 100 nF ao lado de **cada** CI; PCBs de 2 camadas para fabricação profissional, com serigrafia didática (nome de cada sinal nos conectores e LEDs, part number e valor de cada componente). |

## 2.3 Verificações automáticas feitas

1. **Netlist original × nova** (pino a pino, por CI) — só as diferenças intencionais acima.
2. **Esquemático KiCad × descrição** — a netlist exportada pelo `kicad-cli` de cada placa é comparada com `designs.py`: 0 diferenças.
3. **PCB** — DRC do KiCad sem erros e 0 ligações faltando em todas as placas (relatório em `hardware/fabricacao/<placa>/relatorio-drc.txt`).
4. **Cabos** — os 52 cabos (44 para o backplane + 8 diretos) foram verificados: cada pino liga o mesmo sinal nas duas pontas.
5. **Microcódigo** — o emulador em nível de sinais roda os programas de exemplo usando os **binários reais** das EEPROMs, verificando conflito de barramento em cada passo. As versões em Python e em C geram binários idênticos.

## 2.4 Checklist de revisão (atualiza o do README original)

- [x] Reviewer ACC REGISTER
- [x] Reviewer ARITHMETIC LOGIC UNIT
- [x] Reviewer ASSEMBLY LAYOUT (backplane novo)
- [x] Reviewer ASTABLE AND MONOSTABLE CLOCK CIRCUIT
- [x] Reviewer B REGISTER
- [x] Reviewer CONTROL DECODER
- [x] Reviewer DECIMAL DISPLAY
- [x] Reviewer FETCH EXECUTION COUNTER
- [x] Reviewer INSTRUCTION REGISTER
- [x] Reviewer OUTPUT REGISTER
- [x] Reviewer PROGRAM COUNTER
- [x] Reviewer RAM & MAR
- [x] Reviewer RESERT CIRCUIT

Os testes **em bancada** de cada placa produzida ainda serão registrados (o Clock 2.1V já foi testado).

---
Anterior: [1. Arquitetura](01-arquitetura.md) · Próximo: [3. Fabricação das placas](03-fabricacao-das-placas.md)
