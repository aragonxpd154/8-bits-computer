# Histórico de versões — Computador 8 Bits

Autor: **Marcos Silva dos Santos** (MarcosObel)

## 3.0.2 — 2026-11-03
- **Nova tabela de opcodes:** LDI = 2, SUB = 5, AND = 6, OR/ORL = 7, XOR = 8, NOT = 9, JMP = A
  (NOP, LDA, STA, ADD, OUT e HLT não mudaram); JC/JZ nos opcodes B/C. **Regrave as 3 EEPROMs do Decodificador**
  se já tinha gravado a versão anterior.
- **Nova placa opcional: Palavra de Controle** (`cw-palavra-de-controle`) — 18 LEDs mostram os sinais de controle
  em cada passo; 3× 74HCT541 reforçam as saídas das EEPROMs. Liga entre o Decodificador e o backplane, que
  **não muda** (a alimentação vem do conector P_CD e é repassada ao Decodificador).
- Montador aceita `.org`, `.end`, `ORL` e números `0Eh`/`1010b`; 14 programas de teste (um por instrução) em
  `firmware/programas/testes/` e o teste automático `firmware/ferramentas/testar.py`.
- `DISPLAY-com-zeros.bin`: tabela do display com zeros à esquerda (042, −014).
- Corrigido o texto sobre o R1 do Clock.

## 3.0.1 — 2026-11-02
- **Guia das placas** (`docs/placas/`): uma página por placa com função, explicação do circuito, diagrama de
  funcionamento, papel de cada CI, LEDs, chaves, esquemático em imagem, faces da placa como saem da fábrica,
  pinagem dos conectores (com o destino de cada cabo), lista de componentes, teste e mudanças da v3.0.
- **Placas em 3D** (`docs/3d/`): modelos `.glb` com as camadas reais (cobre, máscara, serigrafia, furos), `.stl`
  (visualização 3D direto no GitHub), `.step` em `hardware/fabricacao/<placa>/` e visualizador interativo (three.js).
- Novos geradores: `tools/render3d.py`, `tools/gerar_visualizador.py`, `tools/render_imagens3d.py`,
  `tools/gerar_placas.py`, `tools/diagramas_placas.py`, textos em `tools/placas_info.py`.
- Novo PDF: `docs/pdf/guia-das-placas.pdf`.

## 3.0 — 2026-11-01
- Projeto completo migrado para **KiCad** (`hardware/kicad/`), com esquemático e PCB de todas as 13 placas.
- **Novas placas:** Backplane/Barramento (antiga pasta ASSEMBLY LAYOUT, vazia) e PCB do Reset.
- **Correções:** seleção AL0/AL1 e AND dos bits 1/5 da ULA; /WE das EEPROMs do controle; polaridade dos
  sinais ativos-baixos no microcódigo; pull-down inválido no botão de reset; ordem dos bits do opcode;
  555 da RAM com THR solto; conteúdo da EEPROM do display; display cátodo comum.
- **Melhorias:** buffer de SUB/NOT na ULA, CARRY exposto, conector FLAGS (JC/JZ), chaves DIP com lógica
  direta (ligada = 1), LEDs de passo corretos, reset automático ao ligar, desacoplamento por CI.
- PCBs de 2 camadas para **fabricação profissional** (Gerber prontos para JLCPCB/PCBWay) com **serigrafia
  didática**; guias de montagem 1:1, mapa de furação e PDFs das camadas (apêndice para fazer em casa).
- Firmware: microcódigo completo (16 opcodes) em Python e C, EEPROM do display, montador, emulador e
  6 programas de exemplo.
- Documentação completa em português (`docs/`), **guia visual passo a passo** com diagramas e PDFs
  (guia visual, manual completo, esquema elétrico completo).

## 2.x — 2021-10/12 (EasyEDA)
- Capacitores de desacoplamento perto dos CIs; otimização de posicionamento; clock 2.1V testado em bancada.

## 1.0 — 2021-09/10 (EasyEDA)
- Primeiras versões dos módulos: ACC, B, ULA, Clock, Controle, Display, Fetch, IR, Saída, PC, RAM/MAR, Reset.
