# Gerador KiCad (design-as-code) — Computador 8 Bits v3.0

Autor do projeto: **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

Todo o hardware da versão 3.0 é descrito em Python, em `designs.py` (uma função por placa, com cada
pino de cada componente ligado a uma rede com nome). A partir dessa descrição o gerador produz:

1. a biblioteca de símbolos `hardware/kicad/bibliotecas/computador8bits.kicad_sym`;
2. o esquemático `.kicad_sch` de cada placa (ligações por rótulos de rede, bloco de título com autoria);
3. a verificação da netlist exportada pelo KiCad contra `designs.py` (`verify.py`);
4. a PCB `.kicad_pcb`: posicionamento (`layouts.py`), autorroteamento com Freerouting, DRC;
5. os arquivos de fabricação (`fabricacao.py`): PDFs 1:1, fotolitos, Gerber, furação, BOM.

## Requisitos (Zorin OS 17 / Ubuntu 22.04+)

```bash
sudo add-apt-repository ppa:kicad/kicad-8.0-releases   # ou use o KiCad 7 do repositório padrão
sudo apt update && sudo apt install kicad openjdk-21-jre python3
wget https://github.com/freerouting/freerouting/releases/download/v2.0.1/freerouting-2.0.1.jar
```

> Os arquivos foram gerados com o KiCad 7.0 (formato que abre no KiCad 7, 8 e 9).
> O script usa o módulo `pcbnew` do KiCad, por isso roda com o Python do sistema (`/usr/bin/python3`).

## Uso

```bash
cd tools/gerador-kicad
export FREEROUTING_JAR=~/Downloads/freerouting-2.0.1.jar
/usr/bin/python3 gerar_tudo.py                 # todas as placas
/usr/bin/python3 gerar_tudo.py ALU RAM         # só algumas
/usr/bin/python3 gerar_tudo.py --sem-rotear    # só esquemático + posicionamento
python3 ../gerar_docs.py                       # tabelas da documentação
python3 ../diagramas.py                        # diagrama de blocos
```

Chaves das placas: `CLOCK RESET PC RAM IR CD FETCH ACC B ALU OUT DISPLAY BACKPLANE`.

> Atenção: regerar **substitui** os arquivos `.kicad_sch`/`.kicad_pcb`. Se você editar uma placa à mão no
> KiCad, passe a mantê-la manualmente (ou leve a mudança para `designs.py`/`layouts.py`).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `designs.py` | todas as placas, redes, conectores, tabela de cabos (`CABOS`) e verificação `verificar_cabos()` |
| `symlib.py` | símbolos (CIs retangulares com nomes de pinos, passivos, conectores, alimentação) |
| `sch.py` | escritor de esquemáticos KiCad 7 |
| `verify.py` | compara a netlist do KiCad com `designs.py` |
| `layouts.py` | ordem/posição dos componentes em cada placa e textos de serigrafia |
| `pcbgen.py` | PCB: footprints, pads só na face de baixo, regras, Freerouting, importação das trilhas, DRC |
| `fabricacao.py` | PDFs de impressão, Gerber e furação |
| `gerar_tudo.py` | orquestra tudo |
