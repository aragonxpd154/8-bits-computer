# Pacote parcial — Computador 8 Bits v3.0 (01/11/2026)

Autor: Marcos Silva dos Santos (MarcosObel)

## Pronto neste pacote
- Firmware completo: `firmware/` (microcódigo EEPROM0/1/2.bin, DISPLAY.bin, gerador em Python e em C, montador, emulador, 6 programas de exemplo testados)
- Documentação completa em `docs/` (8 capítulos), lista de materiais, diagrama de blocos, README novo
- Biblioteca de símbolos KiCad: `hardware/kicad/bibliotecas/`
- Placas prontas para a fábrica (DRC sem erros): **Reset** e **Contador de Programa (PC)**
- Gerador de todo o hardware: `tools/gerador-kicad/`

## Ainda em geração (vêm no pacote final)
- **Clock**: esquemático pronto; PCB com 1 ligação faltando — **não mande fabricar esta versão** (o Gerber foi retirado deste pacote de propósito)
- RAM/MAR, IR, Controle, Passos, Registrador A, Registrador B, ULA, Saída, Display e Backplane
- `hardware/esquema-eletrico-completo.pdf` (PDF único com todos os esquemáticos)

Este arquivo pode ser apagado quando o pacote final chegar.
