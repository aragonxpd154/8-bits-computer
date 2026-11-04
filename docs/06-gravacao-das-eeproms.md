# 6. Gravação das EEPROMs (no Zorin OS / Ubuntu)

> Projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

O computador usa **4 EEPROMs 28C16** (AT28C16, CAT28C16A ou equivalente, 2 KB, DIP-24 largo):

| Arquivo | Chip | Placa | Conteúdo |
|---|---|---|---|
| `firmware/microcodigo/EEPROM2.bin` | **U1** | Decodificador de Controle | HLT PCI /JMP /PCO /MAI RMI /RMO /IRI |
| `firmware/microcodigo/EEPROM1.bin` | **U2** | Decodificador de Controle | /IRO /ACO /ACI SUB AL1 AL0 /ALUO NOT |
| `firmware/microcodigo/EEPROM0.bin` | **U3** | Decodificador de Controle | /BRI /ORI (+ 6 bits livres) |
| `firmware/display/DISPLAY.bin` | **U1** | Display Decimal | tabela binário → 7 segmentos |

Cada arquivo tem exatamente 2048 bytes. Também há versões `.hex` (Intel HEX) para gravadores que preferem esse formato.

> **Display com zeros à esquerda:** se preferir ver sempre 3 dígitos (`042`, `-014`), grave
> `firmware/display/DISPLAY-com-zeros.bin` no lugar do `DISPLAY.bin`.
>
> ⚠️ **Use só os `EEPROM0/1/2.bin` deste repositório.** Os 11 sinais ativos em nível baixo já estão gravados
> invertidos: microcódigos de outros projetos, feitos para placas com inversores 74LS04 entre a EEPROM e os
> módulos, ligariam os sinais ao contrário.

> **Etiquete cada chip** (fita crepe: "CD-U1 EEPROM2", "CD-U2 EEPROM1", "CD-U3 EEPROM0", "DISPLAY").
> Trocar dois chips de lugar faz o computador "enlouquecer" sem nenhum dano — mas é difícil de achar.

## 6.1 Gerar (ou regerar) os binários

Os binários já vêm prontos no repositório. Para regerar depois de mudar o microcódigo:

```bash
cd firmware/microcodigo
python3 microcodigo.py          # gera EEPROM0/1/2.bin e .hex e imprime a tabela de instruções
cd ../display
python3 display.py              # gera DISPLAY.bin e .hex
```

Versão em C (mesma saída, byte a byte):

```bash
cd firmware/microcodigo/c
make bins                        # compila com gcc e gera EEPROM0/1/2.bin
```

## 6.2 Gravar com TL866II Plus / XGecu T48 usando `minipro`

1. Instale o `minipro` (programa livre para os gravadores TL866/T48):

   ```bash
   sudo apt update
   sudo apt install minipro        # disponível no Ubuntu 23.04+ / Debian 12+
   ```

   Se o pacote não existir na sua versão do Zorin, compile:

   ```bash
   sudo apt install build-essential pkg-config git libusb-1.0-0-dev zlib1g-dev
   git clone https://gitlab.com/DavidGriffith/minipro.git
   cd minipro && make && sudo make install
   sudo cp udev/*.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

2. Encontre o nome exato do seu chip na lista do `minipro`:

   ```bash
   minipro -l | grep -i 28C16
   ```

3. Coloque a EEPROM no soquete ZIF (pino 1 do lado da alavanca, alinhada embaixo — veja a figura do gravador) e grave:

   ```bash
   minipro -p "AT28C16" -w firmware/microcodigo/EEPROM2.bin      # chip U1 do Controle
   minipro -p "AT28C16" -w firmware/microcodigo/EEPROM1.bin      # chip U2 do Controle
   minipro -p "AT28C16" -w firmware/microcodigo/EEPROM0.bin      # chip U3 do Controle
   minipro -p "AT28C16" -w firmware/display/DISPLAY.bin          # chip U1 do Display
   ```

   O `minipro` grava e confere automaticamente. Para conferir de novo depois:

   ```bash
   minipro -p "AT28C16" -m firmware/microcodigo/EEPROM2.bin
   ```

   Se aparecer erro de ID do chip, acrescente `-y` (as 28C16 não têm ID eletrônico).

## 6.3 Sem gravador?

Dá para gravar uma 28C16 com um Arduino e dois 74HC595 (o "EEPROM programmer" popularizado pelo
Ben Eater). Use os arquivos `.bin` deste repositório como dados. Lembre-se: o computador em si
continua sem nenhum microcontrolador — o Arduino só serve como ferramenta de gravação.

## 6.4 Conferir sem o computador montado

O emulador lê os mesmos `.bin` e executa um programa sinal a sinal, acusando qualquer conflito no barramento:

```bash
cd firmware
python3 ferramentas/emulador.py programas/01-soma.asm            # resultado: [42]
python3 ferramentas/emulador.py programas/04-fibonacci.asm --max 400
python3 ferramentas/emulador.py programas/01-soma.asm --passos   # mostra cada passo T0..T4
```

---
Anterior: [5. Interligação](05-interligacao-e-backplane.md) · Próximo: [7. Programação e uso](07-programacao-e-uso.md)
