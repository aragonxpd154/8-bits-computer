<h1 align="center">
<img alt="8 Bits Computer" src="docs/imagens/logo.png"/>
<br>
</h1>

<h4 align="center">

Computador de 8 bits feito só com lógica TTL (série 74LS), EEPROMs e temporizadores 555 —
**sem microcontrolador, sem CPU pronta**, "como antigamente". Projeto educacional e hobby,
com esquemas, placas (PCB) e manual para fabricar e montar tudo em casa.

</h4>

<p align="center">
<img alt="Github top language" src="https://img.shields.io/github/languages/top/aragonxpd154/8-bits-computer">
<img alt="Repository size" src="https://img.shields.io/github/repo-size/aragonxpd154/8-bits-computer">
<img alt="Github last commit" src="https://img.shields.io/github/last-commit/aragonxpd154/8-bits-computer">
<a href="https://github.com/aragonxpd154/8-bits-computer/issues"><img alt="Repository issues" src="https://img.shields.io/github/issues/aragonxpd154/8-bits-computer"></a>
<img alt="Github license" src="https://img.shields.io/github/license/aragonxpd154/8-bits-computer">
</p>

<p align="center">
<a href="#-o-que-é">O que é</a> ·
<a href="#-status">Status</a> ·
<a href="#-faça-você-mesmo">Faça você mesmo</a> ·
<a href="#-conteúdo-do-repositório">Conteúdo</a> ·
<a href="#-ferramentas">Ferramentas</a> ·
<a href="#-licença">Licença</a>
</p>

<p align="center">
<img alt="Diagrama de blocos" src="docs/imagens/diagrama-blocos.png" width="820">
</p>

## 🧠 O que é

Um computador completo de 8 bits dividido em **12 módulos** + **1 backplane** (placa-mãe de interligação):

| Módulo | Principais CIs | Função |
|---|---|---|
| Clock | NE556, 74LS00, 74LS04 | clock automático (0,7–140 Hz) ou passo a passo, HLT |
| Reset | 74LS132 | reset por botão e ao ligar |
| Contador de Programa | 74LS161, 74LS245 | endereço da próxima instrução |
| RAM e MAR | 2× 74S189, 74LS173, 4× 74LS157 | 16 bytes, programação manual por chaves DIP |
| Registrador de Instrução | 2× 74LS173, 74LS245 | opcode + operando |
| Decodificador de Controle | 3× EEPROM 28C16 | microcódigo: 18 sinais de controle |
| Contador de Passos | 74LS161, 74LS138 | passos T0…T4 |
| Registrador A / B | 2× 74LS173 (+ 74LS245) | acumulador e segundo operando |
| ULA | 74LS283, 74LS86, 74LS08, 74LS32, 74LS153 | soma, subtração, AND, OR, XOR, NOT |
| Registrador de Saída | 2× 74LS173 | valor do display |
| Display Decimal | 28C16, 555, 74LS161, 74LS139 | 0…255 ou −128…127 em 4 dígitos |
| Backplane | — | 5 V protegido, barramento D0…D7 com LEDs, todos os sinais |

**16 instruções:** `NOP LDA SUB STA ADD LDI JMP AND OR XOR NOT JC JZ OUT HLT` (JC/JZ prontos para uma futura placa de flags).
Detalhes em [docs/01-arquitetura.md](docs/01-arquitetura.md).

## 💻 Status

**Versão 3.0 (novembro/2026)** — projeto completo em **KiCad** (abre no Zorin OS/Ubuntu/Windows):

- [x] Esquemáticos de todos os módulos, com bloco de título e autoria
- [x] PCBs roteadas de todas as 13 placas, **DRC sem erros** — prontas para fabricação profissional (JLCPCB/PCBWay) e com **serigrafia didática** (sinais nos conectores e LEDs, valores dos componentes)
- [x] PDFs 1:1 para transferência térmica, fotolitos, mapa de furação e Gerbers para fabricação industrial
- [x] Backplane (antiga pasta *ASSEMBLY LAYOUT*, que estava vazia) e placa de Reset (que não tinha PCB)
- [x] Microcódigo completo (Python e C), EEPROM do display, montador e emulador
- [x] Revisão de todos os circuitos — 9 erros corrigidos (veja [docs/02-revisao-e-correcoes.md](docs/02-revisao-e-correcoes.md))
- [x] Manual completo de fabricação, montagem, gravação e uso
- [ ] Testes em bancada de cada placa produzida (o Clock da versão 2.1 já foi testado)
- [ ] Placa de flags (carry/zero) para `JC`/`JZ`

## ☕ Passo a passo (faça você mesmo)

Siga a documentação em ordem — tudo em português:

1. [Arquitetura](docs/01-arquitetura.md) — entenda o computador
2. [Revisão e correções](docs/02-revisao-e-correcoes.md) — o que mudou desde a versão EasyEDA
3. [Fabricação das placas](docs/03-fabricacao-das-placas.md) — enviar os Gerbers para a China (JLCPCB/PCBWay)
4. [Montagem das placas](docs/04-montagem-das-placas.md) — componente por componente, com testes
5. [Interligação e backplane](docs/05-interligacao-e-backplane.md) — os 52 cabos e o arranjo na base
6. [Gravação das EEPROMs](docs/06-gravacao-das-eeproms.md) — microcódigo e display com `minipro`
7. [Programação e uso](docs/07-programacao-e-uso.md) — escrever, montar e rodar programas
8. [Testes e diagnóstico](docs/08-testes-e-diagnostico.md)

📄 **Esquema elétrico completo em um único PDF:** [hardware/esquema-eletrico-completo.pdf](hardware/esquema-eletrico-completo.pdf)
🧾 **Lista de materiais:** [docs/lista-de-materiais-completa.md](docs/lista-de-materiais-completa.md)
🛠️ **Placas (imagens, tamanhos, arquivos):** [hardware/README.md](hardware/README.md)

## 📁 Conteúdo do repositório

```
8-bits-computer/
├── README.md                     este arquivo (visão geral, passo a passo, conteúdo)
├── CHANGELOG.md                  histórico de versões
├── LICENSE                       GPL-3.0
├── docs/                         MANUAL COMPLETO (pt-BR)
│   ├── 01-arquitetura.md             blocos, instruções, tabela de todos os sinais
│   ├── 02-revisao-e-correcoes.md     erros corrigidos em relação à versão EasyEDA
│   ├── 03-fabricacao-das-placas.md   como pedir as PCBs no JLCPCB/PCBWay
│   ├── 04-montagem-das-placas.md     soldagem e teste de cada placa
│   ├── 05-interligacao-e-backplane.md os 52 cabos e o arranjo na base
│   ├── 06-gravacao-das-eeproms.md    gravação com minipro (Zorin/Ubuntu)
│   ├── 07-programacao-e-uso.md       painel, montador, emulador, exemplos
│   ├── 08-testes-e-diagnostico.md    subida do sistema e problemas comuns
│   ├── lista-de-materiais-completa.md
│   └── imagens/                      diagrama de blocos e imagem de cada placa
├── hardware/
│   ├── README.md                     tabela das 13 placas (tamanho, imagens, links)
│   ├── esquema-eletrico-completo.pdf capa + diagrama + interligação + 13 esquemáticos
│   ├── kicad/<placa>/                projeto KiCad (.kicad_pro / .kicad_sch / .kicad_pcb)
│   ├── kicad/bibliotecas/            símbolos e footprints do projeto
│   └── fabricacao/<placa>/           <placa>-gerber.zip (vai para a fábrica), esquemático PDF,
│                                     guia de montagem 1:1, mapa de furação, BOM, relatório DRC
├── firmware/
│   ├── microcodigo/                  EEPROM0/1/2.bin + gerador (Python e C)
│   ├── display/                      DISPLAY.bin + gerador
│   ├── programas/                    6 programas de exemplo (.asm)
│   └── ferramentas/                  montador.py e emulador.py
└── tools/                            geradores: hardware (KiCad), documentação, diagramas, PDF completo
```

### As 13 placas

| # | Placa | Pasta |
|---|---|---|
| 1 | Backplane / Barramento | `backplane-barramento` |
| 2 | Clock | `clock-astavel-monoestavel` |
| 3 | Reset | `reset-circuito` |
| 4 | Contador de Programa | `pc-contador-programa` |
| 5 | RAM e MAR | `ram-mar-memoria` |
| 6 | Registrador de Instrução | `ir-registrador-instrucao` |
| 7 | Decodificador de Controle | `cd-decodificador-controle` |
| 8 | Contador de Passos | `fetch-contador-passos` |
| 9 | Registrador A | `acc-registrador-a` |
| 10 | Registrador B | `b-registrador-b` |
| 11 | ULA | `alu-unidade-logica-aritmetica` |
| 12 | Registrador de Saída | `out-registrador-saida` |
| 13 | Display Decimal | `display-decimal` |

> As versões antigas em EasyEDA (1.0V–3.0V, 2021) ficam preservadas no histórico do Git, na tag
> [`v2-easyeda`](https://github.com/aragonxpd154/8-bits-computer/tree/v2-easyeda).

## 🚀 Ferramentas

- [KiCad](https://www.kicad.org/) 7 ou superior — esquemáticos e PCBs
- [Freerouting](https://github.com/freerouting/freerouting) — autorroteamento
- Python 3 — microcódigo, montador, emulador e geradores
- `minipro` + TL866II Plus/T48 — gravação das EEPROMs
- Histórico: EasyEDA, LTspice, MultisimLive, Hexplorer, Code::Blocks

Para regerar todo o hardware a partir da descrição em Python, veja [tools/gerador-kicad/README.md](tools/gerador-kicad/README.md).

## 📝 Licença

Este projeto está sob a licença GPL v3.0. Veja o arquivo [LICENSE](LICENSE).

---

Projeto e autoria: **Marcos Silva dos Santos (MarcosObel)** ♥ — [LinkedIn](https://www.linkedin.com/in/marcosobel) · [GitHub](https://github.com/aragonxpd154)

<sub>English summary: an 8-bit TTL computer (SAP-1 style, no microcontroller) by Marcos Silva dos Santos. Version 3.0 contains complete KiCad schematics and home-fabrication-friendly PCBs for all 13 boards, corrected microcode, EEPROM images, an assembler/emulator, and a full build manual (in Portuguese) under `docs/`.</sub>
