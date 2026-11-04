# Placas em 3D — Computador 8 Bits v3.0

> Modelos 3D das 14 placas — projeto de **Marcos Silva dos Santos** (MarcosObel) — GPL-3.0.

<p align="center"><a href="https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html"><img alt="Abrir o 3D Viewer" src="https://img.shields.io/badge/%E2%96%B6%20Abrir%20o%203D%20Viewer-as%2013%20placas%20em%203D-1d5c34?style=for-the-badge&logo=threedotjs&logoColor=white&labelColor=0f3a20" height="36"></a></p>

<p align="center"><img alt="ULA em 3D" src="../imagens/3d/alu-unidade-logica-aritmetica.png" width="760"></p>

| Pasta / arquivo | O que é | Como abrir |
|---|---|---|
| [`montagem.html`](montagem.html) | o computador **montado**: base de madeira, tampa de acrílico, cabos por baixo das placas com enforca-gatos; LEDs e display funcionando (roda o microcódigo de verdade) | [online](https://aragonxpd154.github.io/8-bits-computer/docs/3d/montagem.html) ou servidor local, como o visualizador |
| [`montagem.json`](montagem.json) | posição de cada placa na base, conectores, LEDs e cabos (gerado por `tools/montagem3d.py`) | — |
| [`visualizador.html`](visualizador.html) | visualizador interativo das 13 placas, com a função de cada uma, LEDs e pinagem dos conectores | veja abaixo |
| [`stl/<placa>.stl`](stl/) | malha 3D (sem cores), em milímetros | **o GitHub mostra em 3D** — é só clicar no arquivo |
| [`modelos/<placa>.glb`](modelos/) | modelo com cores e as camadas reais da placa (cobre, máscara verde, serigrafia, furos) | visualizador, Blender, [gltf-viewer.donmccurdy.com](https://gltf-viewer.donmccurdy.com/), Windows "Visualizador 3D" |
| [`texturas/`](texturas/) | imagem da face de cima e de baixo de cada placa, como sai da fábrica | qualquer visualizador de imagens |
| `../../hardware/fabricacao/<placa>/<placa>.step` | modelo mecânico (para projetar a caixa/base) | FreeCAD, Fusion 360, SolidWorks, KiCad |
| [`placas3d.json`](placas3d.json) | medidas, furos e posição de cada componente | — |

## Abrir o visualizador

**Online:** [https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html](https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html) — abre direto no navegador (computador ou celular).
Para abrir já numa placa, acrescente `#nome-da-placa` no fim do endereço
(ex.: [`…/visualizador.html#ram-mar-memoria`](https://aragonxpd154.github.io/8-bits-computer/docs/3d/visualizador.html#ram-mar-memoria)).

**No seu computador:** o navegador não deixa uma página aberta direto do disco (`file://`) carregar os
modelos `.glb`. Use um servidor local (o Python já vem no Zorin OS/Ubuntu):

```bash
cd 8-bits-computer/docs/3d
python3 -m http.server 8000
# abra http://localhost:8000/visualizador.html
```

### Ligar o GitHub Pages (uma vez só)

O `publicar-no-github.sh` tenta ligar sozinho (precisa do GitHub CLI: `sudo apt install gh` e `gh auth login`).
Para ligar à mão: no repositório, **Settings → Pages → Build and deployment → Source: Deploy from a branch →
Branch: `main` / `(root)` → Save**. Em 1 a 2 minutos o endereço acima passa a funcionar. O arquivo `.nojekyll`
na raiz faz o GitHub publicar os arquivos exatamente como estão, e o `index.html` da raiz redireciona
`https://aragonxpd154.github.io/8-bits-computer/` para o visualizador.

Arraste para girar, role para aproximar, botão direito para mover. Botões **Topo/Fundo** mostram cada face;
**Componentes** liga/desliga as peças para ver as trilhas. O endereço aceita `#nome-da-placa`
(ex.: `visualizador.html#ram-mar-memoria`).

## Regerar os modelos

```bash
sudo apt install kicad kicad-packages3d librsvg2-bin
pip install trimesh cascadio pillow numpy playwright && python3 -m playwright install chromium
python3 tools/render3d.py              # STEP + GLB + STL + texturas (todas as placas)
python3 tools/gerar_visualizador.py    # docs/3d/visualizador.html
python3 tools/render_imagens3d.py      # imagens docs/imagens/3d/*.png
python3 tools/gerar_placas.py          # páginas docs/placas/*.md
python3 tools/montagem3d.py            # arranjo na base + cabos (docs/3d/montagem.json)
python3 tools/gerar_montagem_html.py   # docs/3d/montagem.html
```

Peças sem modelo na biblioteca do KiCad (display de 7 segmentos, chave deslizante, potenciômetro, PTC e borne)
recebem um modelo simplificado gerado pelo `render3d.py`.

Detalhes de cada placa: [docs/placas](../placas/README.md).
