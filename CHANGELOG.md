# Histórico de versões — Computador 8 Bits

Autor: **Marcos Silva dos Santos** (MarcosObel)

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
