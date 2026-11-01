# Hardware — Computador 8 Bits v3.0

> Projeto e PCBs de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0. Gerado por `tools/gerar_docs.py`.

- `kicad/<placa>/` — projeto KiCad (abra o `.kicad_pro`). Formato KiCad 7 (abre no 7, 8 e 9).
- `fabricacao/<placa>/` — **Gerber para a fábrica**, guia de montagem 1:1, esquemático, BOM, relatório DRC.
- [`esquema-eletrico-completo.pdf`](esquema-eletrico-completo.pdf) — todos os esquemáticos num único PDF.

Todas: 2 camadas, furo metalizado, trilha 0,5 mm (alimentação 0,9 mm), isolação 0,4 mm, vias 1,6/0,8 mm, 4 furos M3 nos cantos, serigrafia didática. Como pedir: [docs/03-fabricacao-das-placas.md](../docs/03-fabricacao-das-placas.md).

| Placa | Tamanho (mm) | Vias | Trilhas na face de cima | Esquema | Fabricação |
|---|---|---:|---:|---|---|
| **Clock Astavel / Monoestavel** | 105 × 86 | 4 | 96 segmentos | [PDF](fabricacao/clock-astavel-monoestavel/0-esquematico.pdf) | [arquivos](fabricacao/clock-astavel-monoestavel/) |
| **Circuito de Reset** | 67 × 58 | 0 | 33 segmentos | [PDF](fabricacao/reset-circuito/0-esquematico.pdf) | [arquivos](fabricacao/reset-circuito/) |
| **Contador de Programa (PC)** | 92 × 69 | 5 | 93 segmentos | [PDF](fabricacao/pc-contador-programa/0-esquematico.pdf) | [arquivos](fabricacao/pc-contador-programa/) |
| **Memoria RAM e MAR** | 145 × 139 | 151 | 866 segmentos | [PDF](fabricacao/ram-mar-memoria/0-esquematico.pdf) | [arquivos](fabricacao/ram-mar-memoria/) |
| **Registrador de Instrucao (IR)** | 102 × 69 | 6 | 125 segmentos | [PDF](fabricacao/ir-registrador-instrucao/0-esquematico.pdf) | [arquivos](fabricacao/ir-registrador-instrucao/) |
| **Decodificador de Controle (microcodigo)** | 161 × 61 | 6 | 144 segmentos | [PDF](fabricacao/cd-decodificador-controle/0-esquematico.pdf) | [arquivos](fabricacao/cd-decodificador-controle/) |
| **Contador de Passos (Fetch/Execute)** | 70 × 69 | 2 | 86 segmentos | [PDF](fabricacao/fetch-contador-passos/0-esquematico.pdf) | [arquivos](fabricacao/fetch-contador-passos/) |
| **Registrador A (Acumulador)** | 110 × 69 | 4 | 174 segmentos | [PDF](fabricacao/acc-registrador-a/0-esquematico.pdf) | [arquivos](fabricacao/acc-registrador-a/) |
| **Registrador B** | 110 × 69 | 8 | 160 segmentos | [PDF](fabricacao/b-registrador-b/0-esquematico.pdf) | [arquivos](fabricacao/b-registrador-b/) |
| **Unidade Logica e Aritmetica (ULA)** | 218 × 128 | 145 | 837 segmentos | [PDF](fabricacao/alu-unidade-logica-aritmetica/0-esquematico.pdf) | [arquivos](fabricacao/alu-unidade-logica-aritmetica/) |
| **Registrador de Saida (OUT)** | 110 × 69 | 0 | 95 segmentos | [PDF](fabricacao/out-registrador-saida/0-esquematico.pdf) | [arquivos](fabricacao/out-registrador-saida/) |
| **Display Decimal** | 134 × 112 | 11 | 174 segmentos | [PDF](fabricacao/display-decimal/0-esquematico.pdf) | [arquivos](fabricacao/display-decimal/) |
| **Backplane / Barramento (Assembly Layout)** | 204 × 153 | 14 | 202 segmentos | [PDF](fabricacao/backplane-barramento/0-esquematico.pdf) | [arquivos](fabricacao/backplane-barramento/) |

Vermelho = cobre da face de cima (componentes) · azul = cobre da face de baixo (solda) · amarelo = serigrafia.

## Clock Astavel / Monoestavel

NE556: metade astavel (clock automatico ajustavel) e metade monoestavel (passo manual sem repique). Chave AUTO/MANUAL, entrada HLT.

![Clock Astavel / Monoestavel](../docs/imagens/placas/clock-astavel-monoestavel.png)

## Circuito de Reset

Gera RST e ~{RST} (botao + reset automatico ao ligar) e o ~{STEPCLR} do contador de passos (= ~{RST} AND ~{Y5}).

![Circuito de Reset](../docs/imagens/placas/reset-circuito.png)

## Contador de Programa (PC)

Contador de 4 bits (74LS161) com carga (JMP) e saida para o barramento (74LS245).

![Contador de Programa (PC)](../docs/imagens/placas/pc-contador-programa.png)

## Memoria RAM e MAR

MAR (74LS173), RAM 16x8 (2x 74S189), multiplexadores PROG/RUN (74LS157), gravacao manual por chaves DIP e pulso de escrita sincronizado ao clock.

![Memoria RAM e MAR](../docs/imagens/placas/ram-mar-memoria.png)

## Registrador de Instrucao (IR)

Guarda a instrucao: nibble alto = opcode (para o decodificador), nibble baixo = operando (volta ao barramento por ~{IRO}).

![Registrador de Instrucao (IR)](../docs/imagens/placas/ir-registrador-instrucao.png)

## Decodificador de Controle (microcodigo)

3 EEPROMs 28C16 com o microcodigo: endereco = FLAGS(A8:A7) OPCODE(A6:A3) PASSO(A2:A0).

![Decodificador de Controle (microcodigo)](../docs/imagens/placas/cd-decodificador-controle.png)

## Contador de Passos (Fetch/Execute)

Contador de passos T0..T4 (74LS161 + 74LS138). ~{Y5} reinicia o contador via placa de Reset.

![Contador de Passos (Fetch/Execute)](../docs/imagens/placas/fetch-contador-passos.png)

## Registrador A (Acumulador)

Registrador A de 8 bits (2x 74LS173) com saida para o barramento (74LS245) e saida permanente para a ULA.

![Registrador A (Acumulador)](../docs/imagens/placas/acc-registrador-a.png)

## Registrador B

Registrador B de 8 bits; alimenta a entrada B da ULA.

![Registrador B](../docs/imagens/placas/b-registrador-b.png)

## Unidade Logica e Aritmetica (ULA)

Soma/subtracao (2x 74LS283 + 74LS86), AND, OR, XOR e NOT, selecionados por AL1:AL0 em 4x 74LS153.

![Unidade Logica e Aritmetica (ULA)](../docs/imagens/placas/alu-unidade-logica-aritmetica.png)

## Registrador de Saida (OUT)

Registrador de saida: guarda o valor exibido pelo display decimal.

![Registrador de Saida (OUT)](../docs/imagens/placas/out-registrador-saida.png)

## Display Decimal

Converte o valor de 8 bits do registrador OUT em decimal (0..255 ou -128..127) por EEPROM 28C16 e varredura de 4 digitos (555 + 74LS161 + 74LS139).

![Display Decimal](../docs/imagens/placas/display-decimal.png)

## Backplane / Barramento (Assembly Layout)

Placa-mae de interligacao: entrada de 5 V protegida, distribuicao de alimentacao, barramento de dados D0..D7 com LEDs, e roteamento de todos os sinais de controle entre os modulos. Cada conector tem a mesma pinagem do conector correspondente no modulo: use cabos de 4 vias RETOS (pino 1 com pino 1).

![Backplane / Barramento (Assembly Layout)](../docs/imagens/placas/backplane-barramento.png)

