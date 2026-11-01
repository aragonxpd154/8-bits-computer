# Hardware — Computador 8 Bits v3.0

> Projeto e PCBs de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0. Gerado por `tools/gerar_docs.py`.

- `kicad/<placa>/` — projeto KiCad (abra o `.kicad_pro`). Formato KiCad 7 (abre no 7, 8 e 9).
- `fabricacao/<placa>/` — **Gerber para a fábrica**, guia de montagem 1:1, esquemático, BOM, relatório DRC.
- [`esquema-eletrico-completo.pdf`](esquema-eletrico-completo.pdf) — todos os esquemáticos num único PDF.

Todas: 2 camadas, furo metalizado, trilha 0,5 mm (alimentação 0,9 mm), isolação 0,4 mm, vias 1,6/0,8 mm, 4 furos M3 nos cantos, serigrafia didática. Como pedir: [docs/03-fabricacao-das-placas.md](../docs/03-fabricacao-das-placas.md).

| Placa | Tamanho (mm) | Vias | Trilhas na face de cima | Esquema | Fabricação |
|---|---|---:|---:|---|---|
| **Clock Astavel / Monoestavel** | 105 × 86 | 4 | 102 segmentos | [PDF](fabricacao/clock-astavel-monoestavel/0-esquematico.pdf) | [arquivos](fabricacao/clock-astavel-monoestavel/) |
| **Circuito de Reset** | 67 × 58 | 0 | 33 segmentos | [PDF](fabricacao/reset-circuito/0-esquematico.pdf) | [arquivos](fabricacao/reset-circuito/) |
| **Contador de Programa (PC)** | 92 × 69 | 5 | 93 segmentos | [PDF](fabricacao/pc-contador-programa/0-esquematico.pdf) | [arquivos](fabricacao/pc-contador-programa/) |

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

