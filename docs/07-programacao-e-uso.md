# 7. Programação e uso

> Projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

## 7.1 Painel de controle (onde fica cada coisa)

| Placa | Controle | Função |
|---|---|---|
| Backplane | SW1 | liga/desliga |
| Reset | RESET | zera PC, MAR, A, B, IR, OUT e o contador de passos (o computador também se reseta sozinho ao ligar) |
| Clock | AUTO / MANUAL | clock automático (LED pisca) ou passo a passo |
| Clock | PASSO | um pulso de clock por toque (modo MANUAL) |
| Clock | VELOCIDADE | potenciômetro: ~0,7 Hz a ~140 Hz |
| RAM | PROG / RUN | PROG (LED vermelho) = você grava pelas chaves · RUN (LED verde) = o computador usa a RAM |
| RAM | END (DIP 4) | endereço a gravar (A3 A2 A1 A0) |
| RAM | DADO (DIP 8) | byte a gravar (D7 … D0) — **chave ligada = 1** |
| RAM | GRAVAR | grava o DADO no END (só em PROG) |
| Display | COM SINAL / SEM SINAL | mostra 0…255 ou −128…127 |

## 7.2 Escrever um programa

Programas ficam em `firmware/programas/*.asm`. Exemplo (`01-soma.asm`):

```asm
; Soma 28 + 14 = 42 e mostra no display.
        LDA x       ; A <- 28
        ADD y       ; A <- A + 14
        OUT         ; display = 42
        HLT
x:      DB 28
y:      DB 14
```

- Cada linha ocupa **1 byte** (16 bytes no total): instrução + operando de 4 bits, ou `DB` (dado de 8 bits).
- Rótulos (`x:`) viram o endereço da linha. Operandos aceitam decimal, `0x0F`, `0b1010` ou rótulo.

### Montar (gera a tabela das chaves)

```bash
cd firmware
python3 ferramentas/montador.py programas/01-soma.asm
```

Saída:

```
End  Chaves-END  Chaves-DADO   Hex  Binario    Instrucao
     (4 3 2 1)   (8 7 6 5 4 3 2 1)
 0   ····        ···█·█··     14   00010100   LDA x
 1   ···█        ·█···█·█     45   01000101   ADD y
 2   ··█·        ███·····     E0   11100000   OUT
 3   ··██        ████····     F0   11110000   HLT
 4   ·█··        ···███··     1C   00011100   DB 28
 5   ·█·█        ····███·     0E   00001110   DB 14
█ = chave LIGADA (1)   · = chave DESLIGADA (0).  Chave 1 = bit 0 (direita).
```

### Testar no emulador antes de gravar

```bash
python3 ferramentas/emulador.py programas/01-soma.asm            # Saidas no display: [42]
python3 ferramentas/emulador.py programas/01-soma.asm --passos   # cada passo, sinais e barramento
```

## 7.3 Gravar o programa na RAM (pelas chaves)

1. Clock em **MANUAL** (assim nada roda enquanto você grava).
2. RAM em **PROG** (LED vermelho aceso). Os LEDs amarelos mostram o endereço das chaves END e os verdes mostram o conteúdo da RAM nesse endereço.
3. Para cada linha da tabela do montador:
   1. ajuste **END** (chaves 4 3 2 1 = A3 A2 A1 A0);
   2. ajuste **DADO** (chaves 8 … 1 = D7 … D0);
   3. aperte **GRAVAR** — os LEDs verdes passam a mostrar o dado.
4. Confira passando de novo pelos endereços (sem apertar GRAVAR).

> A RAM 74S189 é volátil: o programa se perde ao desligar.

## 7.4 Executar
1. RAM em **RUN** (LED verde).
2. Aperte **RESET**.
3. Clock em **AUTO** (ou vá dando PASSO para acompanhar cada microinstrução nos LEDs).
4. O resultado aparece no display; `HLT` para o clock.

Acompanhe nos LEDs: Passos (T0…T4), PC, endereço da RAM, IR (opcode/operando), barramento (backplane), A, B, ULA e OUT.

## 7.5 Programas de exemplo (`firmware/programas/`)

| Arquivo | O que faz | Resultado no display |
|---|---|---|
| `01-soma.asm` | 28 + 14 | 42 |
| `02-subtracao.asm` | 100 − 58 | 42 |
| `03-contador.asm` | conta 0, 1, 2 … 255, 0 … | contagem infinita |
| `04-fibonacci.asm` | sequência de Fibonacci (usa STA, 16 bytes) | 0 1 1 2 3 5 8 13 21 34 55 89 144 233 … |
| `05-logica.asm` | AND, OR, XOR, NOT de 0xF0 e 0x3C | 48, 252, 204, 15 |
| `06-multiplica-por-soma.asm` | tabuada do 7 por soma repetida | 7, 14, 21, 28 … |

Todos foram verificados no emulador com os binários finais das EEPROMs.

## 7.6 Conjunto de instruções (resumo)

| Hex | Instrução | Operação |
|---|---|---|
| 0 | `NOP` | nada |
| 1 | `LDA end` | A ← RAM[end] |
| 2 | `SUB end` | A ← A − RAM[end] |
| 3 | `STA end` | RAM[end] ← A |
| 4 | `ADD end` | A ← A + RAM[end] |
| 5 | `LDI n` | A ← n (0…15) |
| 6 | `JMP end` | PC ← end |
| 7 | `AND end` | A ← A AND RAM[end] |
| 8 | `OR end` | A ← A OR RAM[end] |
| 9 | `XOR end` | A ← A XOR RAM[end] |
| A | `NOT` | A ← NOT A |
| B | `JC end` | salta se carry (requer placa de flags) |
| C | `JZ end` | salta se zero (requer placa de flags) |
| E | `OUT` | display ← A |
| F | `HLT` | para |

Detalhes de cada microinstrução: [1. Arquitetura](01-arquitetura.md#13-conjunto-de-instruções).

---
Anterior: [6. Gravação das EEPROMs](06-gravacao-das-eeproms.md) · Próximo: [8. Testes e diagnóstico](08-testes-e-diagnostico.md)
