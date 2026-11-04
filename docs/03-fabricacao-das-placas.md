# 3. Fabricação das placas (JLCPCB / PCBWay)

> Computador 8 Bits v3.0 — projeto de **Marcos Silva dos Santos** (MarcosObel). Licença GPL-3.0.

As 14 placas foram projetadas para **fabricação profissional** (2 camadas, furo metalizado) e, ao mesmo
tempo, para serem **didáticas**: quem pega a placa na mão consegue seguir o circuito.

## 3.1 O que a placa mostra (pensado para estudo)

| Na serigrafia (face de cima) | Para que serve |
|---|---|
| Nome do módulo e versão no topo | identificar a placa |
| **Nome e pinagem de cada conector** (ex.: `CONTROLE: CLK /ACI RST /ACO`) | saber o que entra e sai sem abrir o esquema |
| **Part number de cada CI** (74LS173, 74LS245…) e **valor** de resistores/capacitores | montar e estudar sem consultar a lista |
| **Sinal que cada LED mostra** (A7…A0, T0…T4, PROG/RUN…) | ver o computador "pensando" |
| Textos das chaves (END, DADO, GRAVAR, AUTO/MANUAL…) | operar o painel |
| Na face de baixo, em cobre: `8BITS <PLACA> v3.0 - M.S.SANTOS` | assinatura do projeto |

Os componentes seguem a ordem do fluxo do sinal (conectores em cima → CIs → LEDs embaixo), o que deixa
as trilhas fáceis de acompanhar com o esquemático (`0-esquematico.pdf`) ao lado.

**Regras de projeto:** 2 camadas · trilha 0,5 mm (alimentação 0,9 mm) · isolação 0,4 mm · via 1,6/0,8 mm ·
furos de 0,8 a 3,2 mm · 4 furos M3 de fixação · borda livre de 1,5 mm. Tudo dentro das capacidades
padrão (as mais baratas) dos fabricantes.

## 3.2 Arquivos (em `hardware/fabricacao/<placa>/`)

| Arquivo | Uso |
|---|---|
| **`<placa>-gerber.zip`** | **o arquivo que vai para a fábrica** (Gerber RS-274X + furação Excellon) |
| `0-esquematico.pdf` | diagrama elétrico da placa |
| `3-mascara-montagem-componentes.pdf` | guia de montagem em tamanho real: imprima e deixe ao lado durante a solda |
| `7-mapa-de-furacao.pdf` | diâmetros e posições dos furos |
| `lista-de-materiais.csv` | componentes da placa |
| `relatorio-drc.txt` | verificação de regras do KiCad (sem erros) |
| `1-…`, `2-…`, `4-…`, `5-…`, `6-…` | PDFs 1:1 das camadas de cobre e fotolitos — para estudo/conferência ou fabricação caseira (apêndice 3.5) |

## 3.3 Pedido no JLCPCB (o PCBWay é praticamente igual)

1. Acesse **jlcpcb.com** → *Order now* → **Add gerber file** → escolha `hardware/fabricacao/<placa>/<placa>-gerber.zip`.
2. O site lê o tamanho e mostra a placa. Confira/ajuste:

   | Opção | Valor |
   |---|---|
   | Base Material | FR-4 |
   | Layers | **2** |
   | PCB Qty | 5 (o mínimo; sobra para presentear/estudar) |
   | PCB Thickness | 1.6 mm |
   | PCB Color | à escolha (verde é a mais barata e rápida) |
   | Surface Finish | HASL (with lead) ou LeadFree HASL |
   | Outer Copper Weight | 1 oz |
   | Remove Order Number | *Specify a location* não é necessário — escolha "No" ou deixe o padrão |
   | PCB Assembly | **desligado** (você mesmo solda) |

3. *Save to cart* e repita para as outras placas (são 14; a Palavra de Controle é opcional e pode ser pedida depois). Fazer **um único pedido** com todas sai mais barato no frete.
4. Pague e acompanhe. Prazo típico: alguns dias de produção + o frete escolhido.

> Dica: o backplane (≈ 205 × 150 mm) e a ULA (≈ 220 × 130 mm) passam de 100 × 100 mm, faixa em que
> alguns fabricantes cobram mais. As demais placas são pequenas.

### Conferência antes de pedir (opcional)
Abra o `.zip` num visualizador de Gerber (o próprio site mostra; no Zorin dá para usar o
`gerbv`: `sudo apt install gerbv`) e confira o contorno e os furos.

## 3.4 Quando as placas chegarem
1. Confira visualmente: trilhas íntegras, furos todos abertos, serigrafia legível.
2. Multímetro em continuidade entre **+5V e GND** do conector `ALIMENTACAO` (J1): **não pode apitar**.
3. Siga para [4. Montagem das placas](04-montagem-das-placas.md).

## 3.5 Apêndice — fazer em casa (opcional)
Os PDFs `1-cobre-inferior-transferencia.pdf` e `2-cobre-superior-transferencia-espelhado.pdf` estão em
**escala 1:1** (há uma régua de 50 mm em cada um — imprima em 100 %). Dá para fazer as placas pequenas
(Reset, Clock, Passos, PC) por transferência térmica de toner em placa dupla face. Como os pads são
nas duas faces e não há metalização, é preciso:
- fazer cada **via** com um pedaço de fio rígido soldado dos dois lados;
- soldar **também por cima** todo terminal que tenha trilha na face de cima (use soquetes torneados, que
  deixam espaço para o ferro).

Para as placas grandes, a fabricação profissional é muito mais confiável.

---
Anterior: [2. Revisão e correções](02-revisao-e-correcoes.md) · Próximo: [4. Montagem das placas](04-montagem-das-placas.md)
