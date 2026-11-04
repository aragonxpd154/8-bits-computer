# Lista de materiais completa - Computador 8 Bits v3.0

> Autor do projeto: **Marcos Silva dos Santos** (MarcosObel). Gerada automaticamente a partir de `tools/gerador-kicad/designs.py`.

Compre **10 % a mais** de resistores, capacitores, LEDs e barras de pinos, e **1 CI reserva** de cada tipo mais usado (74LS173, 74LS245, 74LS157).

## Totais (todas as 14 placas)

| Quantidade | Componente |
|---:|---|
| 3 | CI 74HCT541 (DIP-20) |
| 2 | CI 74LS00 (DIP-14) |
| 4 | CI 74LS04 (DIP-14) |
| 2 | CI 74LS08 (DIP-14) |
| 1 | CI 74LS132 (DIP-14) |
| 1 | CI 74LS138 (DIP-16) |
| 1 | CI 74LS139 (DIP-16) |
| 4 | CI 74LS153 (DIP-16) |
| 4 | CI 74LS157 (DIP-16) |
| 3 | CI 74LS161 (DIP-16) |
| 9 | CI 74LS173 (DIP-16) |
| 6 | CI 74LS245 (DIP-20) |
| 2 | CI 74LS283 (DIP-16) |
| 4 | CI 74LS32 (DIP-14) |
| 4 | CI 74LS86 (DIP-14) |
| 2 | CI 74S189 (DIP-16) |
| 4 | CI AT28C16 (DIP-24) |
| 2 | CI NE555 (DIP-8) |
| 1 | CI NE556 (DIP-14) |
| 1 | 1N5822 |
| 118 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) |
| 1 | Borne 5 V |
| 3 | Botao tactil 6x6 mm (4 terminais) |
| 60 | Capacitor 100nF |
| 4 | Capacitor 10nF |
| 1 | Capacitor 10uF eletrolitico |
| 1 | Capacitor 10uF tantalo |
| 1 | Capacitor 15nF |
| 1 | Capacitor 1nF |
| 1 | Capacitor 330nF |
| 1 | Capacitor 470uF 10V eletrolitico |
| 1 | Chave DIP 4 vias |
| 1 | Chave DIP 8 vias |
| 4 | Chave deslizante SPDT 3 terminais passo 2,54 mm |
| 1 | Display 7 segmentos 4 digitos 0,4" catodo comum (12 pinos) |
| 1 | Jack DC 5,5x2,1 (5 V) |
| 7 | LED amarelo 3mm |
| 19 | LED azul 3mm |
| 59 | LED verde 3mm |
| 10 | LED vermelho 3mm |
| 1 | PTC 3 A (MF-RG300) |
| 1 | Potenciometro 100k linear 9 mm (Alps RK09K) |
| 1 | Rede resistiva SIP-5 1k comum no pino 1 (4 resistores) |
| 1 | Rede resistiva SIP-9 1k comum no pino 1 (8 resistores) |
| 1 | Resistor 10 1/4 W |
| 8 | Resistor 100 1/4 W |
| 1 | Resistor 100k 1/4 W |
| 6 | Resistor 10k 1/4 W |
| 32 | Resistor 1k 1/4 W |
| 3 | Resistor 330 1/4 W |
| 1 | Resistor 330k 1/4 W |
| 65 | Resistor 470 1/4 W |

### Soquetes (recomendados para todos os CIs)

| Quantidade | Item |
|---:|---|
| 18 | Soquete DIP-14 (300 mil) |
| 26 | Soquete DIP-16 (300 mil) |
| 9 | Soquete DIP-20 (300 mil) |
| 4 | Soquete DIP-24 largo (600 mil) - ou ZIF 24 pinos |
| 2 | Soquete DIP-8 (300 mil) |

Total de circuitos integrados: **59** (+ 1 display).

### Itens gerais

| Quantidade | Item |
|---:|---|
| 1 | Fonte 5 V regulada, 2 A ou mais, plugue P4 5,5 x 2,1 mm (centro positivo) |
| 58 | Cabo femea-femea de 4 vias (tamanhos na tabela de cabos do capitulo 5: 30 a 80 cm); ou fio flat de 4 vias + conectores Dupont 1x4 femea crimpados |
| 1 | Base de madeira/MDF 65 x 56 cm, 18 mm |
| 56 | Espacador M3 x 25 mm + parafuso + porca (4 por placa) |
| 1 | Tampa de acrilico transparente 4-5 mm, 64 x 55 cm |
| 6 | Coluna/espacador de aluminio ~105 mm (M6 ou M4) para a tampa |
| ~100 | Abracadeira de nylon (enforca-gato) 100 mm + base adesiva 20 x 20 mm |
| 1 | Gravador de EEPROM (TL866II Plus / XGecu T48) - para as 4 EEPROMs 28C16 |
| - | Placa de fenolite/fibra de vidro cobreada dupla face (ver tamanhos em hardware/README.md) |
| - | Percloreto de ferro, papel couche/glossy, fio rigido 0,6 mm (vias), estanho, fluxo |

## Por placa

### Clock (`CLOCK`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 1 | Capacitor 10uF tantalo | C1 |
| 2 | Capacitor 10nF | C2 C3 |
| 1 | Capacitor 330nF | C4 |
| 3 | Capacitor 100nF | C5 C6 C7 |
| 2 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 |
| 1 | LED azul 3mm | LED1 |
| 1 | Resistor 1k 1/4 W | R1 |
| 1 | Resistor 10 1/4 W | R2 |
| 1 | Resistor 10k 1/4 W | R4 |
| 1 | Resistor 330k 1/4 W | R5 |
| 1 | Resistor 470 1/4 W | R6 |
| 1 | Potenciometro 100k linear 9 mm (Alps RK09K) | RV1 |
| 1 | Botao tactil 6x6 mm (4 terminais) | SW1 |
| 1 | Chave deslizante SPDT 3 terminais passo 2,54 mm | SW2 |
| 1 | CI NE556 (DIP-14) | U1 |
| 1 | CI 74LS00 (DIP-14) | U2 |
| 1 | CI 74LS04 (DIP-14) | U3 |

### Reset (`RESET`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 1 | Capacitor 10uF eletrolitico | C1 |
| 1 | Capacitor 100nF | C2 |
| 2 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 |
| 1 | LED vermelho 3mm | LED1 |
| 2 | Resistor 10k 1/4 W | R1 R2 |
| 1 | Resistor 1k 1/4 W | R3 |
| 1 | Botao tactil 6x6 mm (4 terminais) | SW1 |
| 1 | CI 74LS132 (DIP-14) | U1 |

### Contador de Programa (`PC`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 2 | Capacitor 100nF | C1 C2 |
| 5 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 |
| 4 | LED verde 3mm | LED1 LED2 LED3 LED4 |
| 4 | Resistor 470 1/4 W | R1 R2 R3 R4 |
| 1 | CI 74LS161 (DIP-16) | U1 |
| 1 | CI 74LS245 (DIP-20) | U2 |

### RAM e MAR (`RAM`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 12 | Capacitor 100nF | C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12 |
| 1 | Capacitor 1nF | C13 |
| 1 | Capacitor 10nF | C14 |
| 5 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 |
| 9 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 LED14 |
| 4 | LED amarelo 3mm | LED9 LED10 LED11 LED12 |
| 1 | LED vermelho 3mm | LED13 |
| 14 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R14 R15 |
| 3 | Resistor 1k 1/4 W | R13 R16 R18 |
| 1 | Resistor 10k 1/4 W | R17 |
| 1 | Rede resistiva SIP-9 1k comum no pino 1 (8 resistores) | RN1 |
| 1 | Rede resistiva SIP-5 1k comum no pino 1 (4 resistores) | RN2 |
| 1 | Chave DIP 4 vias | SW1 |
| 1 | Chave deslizante SPDT 3 terminais passo 2,54 mm | SW2 |
| 1 | Chave DIP 8 vias | SW3 |
| 1 | Botao tactil 6x6 mm (4 terminais) | SW4 |
| 2 | CI 74S189 (DIP-16) | U1 U2 |
| 2 | CI 74LS04 (DIP-14) | U3 U4 |
| 1 | CI 74LS245 (DIP-20) | U5 |
| 1 | CI 74LS173 (DIP-16) | U6 |
| 4 | CI 74LS157 (DIP-16) | U7 U8 U9 U10 |
| 1 | CI 74LS00 (DIP-14) | U11 |
| 1 | CI NE555 (DIP-8) | U12 |

### Reg. Instrucao (`IR`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 3 | Capacitor 100nF | C1 C2 C3 |
| 5 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 |
| 8 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 |
| 8 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 |
| 2 | CI 74LS173 (DIP-16) | U1 U2 |
| 1 | CI 74LS245 (DIP-20) | U3 |

### Decodificador de Controle (`CD`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 3 | Capacitor 100nF | C1 C2 C3 |
| 9 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 J7 J8 J9 |
| 2 | Resistor 10k 1/4 W | R1 R2 |
| 3 | CI AT28C16 (DIP-24) | U1 U2 U3 |

### Palavra de Controle (opcional) (`CW`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 3 | Capacitor 100nF | C1 C2 C3 |
| 12 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 J7 J8 J9 J10 J11 J12 |
| 18 | LED azul 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 LED9 LED10 LED11 LED12 LED13 LED14 LED15 LED16 LED17 LED18 |
| 18 | Resistor 1k 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R13 R14 R15 R16 R17 R18 |
| 3 | CI 74HCT541 (DIP-20) | U1 U2 U3 |

### Contador de Passos (`FETCH`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 2 | Capacitor 100nF | C1 C2 |
| 3 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 |
| 3 | LED amarelo 3mm | LED1 LED2 LED3 |
| 5 | LED verde 3mm | LED4 LED5 LED6 LED7 LED8 |
| 3 | Resistor 330 1/4 W | R1 R2 R3 |
| 5 | Resistor 470 1/4 W | R4 R5 R6 R7 R8 |
| 1 | CI 74LS161 (DIP-16) | U1 |
| 1 | CI 74LS138 (DIP-16) | U2 |

### Registrador A (`ACC`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 3 | Capacitor 100nF | C1 C2 C3 |
| 6 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 |
| 8 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 |
| 8 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 |
| 2 | CI 74LS173 (DIP-16) | U1 U2 |
| 1 | CI 74LS245 (DIP-20) | U3 |

### Registrador B (`B`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 3 | Capacitor 100nF | C1 C2 C3 |
| 6 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 |
| 8 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 |
| 8 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 |
| 2 | CI 74LS173 (DIP-16) | U1 U2 |
| 1 | CI 74LS245 (DIP-20) | U3 |

### ULA (`ALU`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 18 | Capacitor 100nF | C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12 C13 C14 C15 C16 C17 C18 |
| 9 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 J7 J8 J9 |
| 8 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 |
| 8 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 |
| 2 | CI 74LS283 (DIP-16) | U1 U2 |
| 4 | CI 74LS86 (DIP-14) | U3 U4 U10 U12 |
| 2 | CI 74LS08 (DIP-14) | U5 U6 |
| 4 | CI 74LS32 (DIP-14) | U7 U8 U9 U11 |
| 4 | CI 74LS153 (DIP-16) | U13 U14 U15 U16 |
| 1 | CI 74LS245 (DIP-20) | U17 |
| 1 | CI 74LS04 (DIP-14) | U18 |

### Registrador de Saida (`OUT`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 2 | Capacitor 100nF | C1 C2 |
| 6 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 J4 J5 J6 |
| 8 | LED verde 3mm | LED1 LED2 LED3 LED4 LED5 LED6 LED7 LED8 |
| 8 | Resistor 470 1/4 W | R1 R2 R3 R4 R5 R6 R7 R8 |
| 2 | CI 74LS173 (DIP-16) | U1 U2 |

### Display Decimal (`DISPLAY`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 4 | Capacitor 100nF | C1 C2 C3 C4 |
| 1 | Capacitor 15nF | C5 |
| 1 | Capacitor 10nF | C6 |
| 1 | Display 7 segmentos 4 digitos 0,4" catodo comum (12 pinos) | DS1 |
| 3 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J1 J2 J3 |
| 1 | Resistor 1k 1/4 W | R1 |
| 8 | Resistor 100 1/4 W | R2 R3 R4 R5 R6 R7 R8 R9 |
| 1 | Resistor 100k 1/4 W | R10 |
| 1 | Chave deslizante SPDT 3 terminais passo 2,54 mm | SW1 |
| 1 | CI AT28C16 (DIP-24) | U1 |
| 1 | CI NE555 (DIP-8) | U2 |
| 1 | CI 74LS161 (DIP-16) | U3 |
| 1 | CI 74LS139 (DIP-16) | U4 |

### Backplane (`BACKPLANE`)

| Qtd | Componente | Referencias |
|---:|---|---|
| 1 | Capacitor 470uF 10V eletrolitico | C1 |
| 1 | Capacitor 100nF | C2 |
| 1 | 1N5822 | D1 |
| 1 | PTC 3 A (MF-RG300) | F1 |
| 1 | Jack DC 5,5x2,1 (5 V) | J1 |
| 1 | Borne 5 V | J2 |
| 45 | Barra de pinos macho 1x4 2,54 mm (90 graus ou reta) | J3 J4 J5 J6 J7 J8 J9 J10 J11 J12 J13 J14 J15 J16 J17 J18 J19 J20 J21 J22 J23 J24 J25 J26 J27 J28 J29 J30 J31 J32 J33 J34 J35 J36 J37 J38 J39 J40 J41 J42 J43 J44 J45 J46 J47 |
| 1 | LED verde 3mm | LED1 |
| 8 | LED vermelho 3mm | LED2 LED3 LED4 LED5 LED6 LED7 LED8 LED9 |
| 1 | Resistor 470 1/4 W | R1 |
| 8 | Resistor 1k 1/4 W | R2 R3 R4 R5 R6 R7 R8 R9 |
| 1 | Chave deslizante SPDT 3 terminais passo 2,54 mm | SW1 |

