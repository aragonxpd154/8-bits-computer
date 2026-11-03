#!/usr/bin/env python3
"""Gera os modelos 3D das 13 placas do Computador 8 Bits v3.0.

Para cada placa:
  hardware/fabricacao/<placa>/<placa>.step   modelo mecanico (abre no FreeCAD/Fusion/KiCad)
  docs/3d/modelos/<placa>.glb                modelo com cores + texturas reais das camadas
                                             (cobre, mascara, serigrafia, furos) -> visualizador
  docs/3d/stl/<placa>.stl                    malha simples (o GitHub mostra STL em 3D no navegador)
  docs/3d/texturas/<placa>-{topo,fundo}.png  imagem das camadas como sai da fabrica

Requisitos: KiCad 7 (kicad-cli + modulo pcbnew), pacote kicad-packages3d, e
  pip install trimesh cascadio pillow numpy
Uso:  python3 tools/render3d.py [placa ...]

Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import re
import sys
import json
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KICAD = os.path.join(RAIZ, 'hardware', 'kicad')
FAB = os.path.join(RAIZ, 'hardware', 'fabricacao')
D3 = os.path.join(RAIZ, 'docs', '3d')
MODELOS3D = os.environ.get('KICAD_3DMODELS', '/usr/share/kicad/3dmodels')
PX_MM = float(os.environ.get('PX_MM', '12'))          # resolucao das texturas
MAX_PX = 4096                                          # limite por lado (placas grandes)

# cores "de fabrica" (mascara verde + acabamento HASL + serigrafia branca)
COR_MASCARA = np.array([22, 92, 50], float)
COR_MASCARA_CU = np.array([46, 128, 70], float)       # mascara por cima do cobre (mais clara)
COR_HASL = np.array([206, 206, 196], float)           # cobre exposto estanhado
COR_FR4 = np.array([196, 178, 120], float)            # fibra sem mascara/cobre
COR_SILK = np.array([245, 245, 240], float)
COR_BORDA = (18, 70, 38, 255)                         # lateral da placa no modelo 3D


def placas():
    return sorted(d for d in os.listdir(KICAD) if os.path.isfile(os.path.join(KICAD, d, d + '.kicad_pcb')))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + r.stdout + r.stderr)
    return r


# ---------------------------------------------------------------- dados da placa (pcbnew)
def dados_placa(pcb):
    import pcbnew
    b = pcbnew.LoadBoard(pcb)
    bb = b.GetBoardEdgesBoundingBox()
    mm = pcbnew.ToMM
    x0, y0, w, h = mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetWidth()), mm(bb.GetHeight())
    # o bounding box inclui a espessura da linha do contorno -> usa o eixo da linha (= borda real)
    lw = max([mm(d.GetWidth()) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts] or [0])
    x0, y0, w, h = x0 + lw / 2, y0 + lw / 2, w - lw, h - lw
    furos = []
    for p in b.GetPads():
        d = p.GetDrillSize()
        if d.x > 0:
            pos = p.GetPosition()
            furos.append((mm(pos.x) - x0, mm(pos.y) - y0, mm(d.x), mm(d.y)))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            pos = t.GetPosition()
            dv = mm(t.GetDrillValue())
            furos.append((mm(pos.x) - x0, mm(pos.y) - y0, dv, dv))
    comps, sem_modelo = [], []
    for fp in b.GetFootprints():
        fpn = fp.GetFPID().GetLibItemName().wx_str()
        if not fpn.startswith('MountingHole'):
            existe = False
            for m3 in fp.Models():
                f = re.sub(r'\$\{KICAD\d_3DMODEL_DIR\}', MODELOS3D, m3.m_Filename)
                existe |= os.path.exists(os.path.splitext(f)[0] + '.step') or os.path.exists(f)
            if not existe:
                r = fp.GetBoundingBox(False, False)
                sem_modelo.append({'ref': fp.GetReference(), 'fp': fpn, 'valor': fp.GetValue(),
                                   'bb': [mm(r.GetX()) - x0, mm(r.GetY()) - y0, mm(r.GetRight()) - x0,
                                          mm(r.GetBottom()) - y0]})
        comps.append({'ref': fp.GetReference(), 'valor': fp.GetValue(),
                      'x': round(mm(fp.GetPosition().x) - x0, 2), 'y': round(mm(fp.GetPosition().y) - y0, 2),
                      'lado': 'fundo' if fp.IsFlipped() else 'topo'})
    return {'x0': x0, 'y0': y0, 'w': w, 'h': h, 'furos': furos, 'comps': comps, 'sem_modelo': sem_modelo,
            'vias': sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')}


# ---------------------------------------------------------------- texturas
def camada_png(pcb, camada, info, td, escala):
    """Exporta uma camada como SVG (pagina inteira, coordenadas reais em mm), recorta no contorno e rasteriza."""
    svg = os.path.join(td, camada.replace('.', '_') + '.svg')
    run(['kicad-cli', 'pcb', 'export', 'svg', '--layers', camada, '--black-and-white', '--page-size-mode', '0',
         '--exclude-drawing-sheet', '-o', svg, pcb])
    t = open(svg).read()
    vb = f'{info["x0"]:.4f} {info["y0"]:.4f} {info["w"]:.4f} {info["h"]:.4f}'
    t = re.sub(r'width="[^"]*mm" height="[^"]*mm" viewBox="[^"]*"',
               f'width="{info["w"]:.4f}mm" height="{info["h"]:.4f}mm" viewBox="{vb}"', t, count=1)
    open(svg, 'w').write(t)
    png = svg[:-4] + '.png'
    W, H = round(info['w'] * escala), round(info['h'] * escala)
    run(['rsvg-convert', '-w', str(W), '-h', str(H), '-o', png, svg])
    a = np.asarray(Image.open(png).convert('RGBA'), float)[..., 3] / 255.0
    return a


def textura(pcb, lado, info, td, escala):
    L = 'F' if lado == 'topo' else 'B'
    cu = camada_png(pcb, f'{L}.Cu', info, td, escala)
    ab = camada_png(pcb, f'{L}.Mask', info, td, escala)        # aberturas na mascara
    sk = camada_png(pcb, f'{L}.SilkS', info, td, escala)
    cu3, ab3 = cu[..., None], ab[..., None]
    sob_mascara = COR_MASCARA * (1 - cu3) + COR_MASCARA_CU * cu3
    exposto = COR_FR4 * (1 - cu3) + COR_HASL * cu3
    rgb = sob_mascara * (1 - ab3) + exposto * ab3
    s3 = (sk * (1 - ab))[..., None]                            # a fabrica corta a serigrafia sobre os pads
    rgb = rgb * (1 - s3) + COR_SILK * s3
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    # furos transparentes
    alfa = Image.new('L', img.size, 255)
    dr = ImageDraw.Draw(alfa)
    for x, y, dx, dy in info['furos']:
        rx, ry = dx * escala / 2, dy * escala / 2
        cx, cy = x * escala, y * escala
        if abs(dx - dy) < 1e-3:
            dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=0)
        else:  # furo oblongo
            r = min(rx, ry)
            dr.rounded_rectangle((cx - rx, cy - ry, cx + rx, cy + ry), radius=r, fill=0)
    img.putalpha(alfa)
    return img


# ---------------------------------------------------------------- modelo 3D
def exportar_step(pcb, step, info):
    env = dict(os.environ, KICAD6_3DMODEL_DIR=MODELOS3D, KICAD7_3DMODEL_DIR=MODELOS3D)
    run(['kicad-cli', 'pcb', 'export', 'step', '--subst-models', '--user-origin',
         f'{info["x0"]}x{info["y0"]}mm', '-f', '-o', step, pcb], env=env)


def _caixa(trimesh, x0, y0, x1, y1, z0, z1, cor):
    """caixa em coordenadas da placa (mm, y para baixo) -> metros no sistema do GLB"""
    ext = [(x1 - x0) / 1000, (y1 - y0) / 1000, (z1 - z0) / 1000]
    T = np.eye(4)
    T[:3, 3] = [(x0 + x1) / 2000, -(y0 + y1) / 2000, (z0 + z1) / 2000]
    m = trimesh.creation.box(extents=ext, transform=T)
    m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile(cor, (len(m.faces), 1)))
    return m


def _cilindro(trimesh, cx, cy, r, z0, z1, cor):
    T = np.eye(4)
    T[:3, 3] = [cx / 1000, -cy / 1000, (z0 + z1) / 2000]
    m = trimesh.creation.cylinder(radius=r / 1000, height=(z1 - z0) / 1000, sections=32, transform=T)
    m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile(cor, (len(m.faces), 1)))
    return m


def _face_display(trimesh, x0, y0, x1, y1, z):
    """frente do display de 7 segmentos (4 digitos '8.') desenhada em textura"""
    from trimesh.visual.material import PBRMaterial
    from trimesh.visual import TextureVisuals
    W, H = 600, int(600 * (y1 - y0) / (x1 - x0))
    img = Image.new('RGB', (W, H), (24, 24, 26))
    d = ImageDraw.Draw(img)
    seg = (70, 30, 30)
    dw = W / 4
    for k in range(4):
        cx = dw * k + dw * 0.45
        a, b_ = dw * 0.26, H * 0.30           # meia largura / meia altura do 8
        t = max(4, int(dw * 0.07))
        cy = H / 2
        for (xa, ya, xb, yb) in [(-a, -b_, a, -b_), (-a, 0, a, 0), (-a, b_, a, b_)]:
            d.line((cx + xa, cy + ya, cx + xb, cy + yb), fill=seg, width=t)
        for (xa, ya, xb, yb) in [(-a, -b_, -a, 0), (a, -b_, a, 0), (-a, 0, -a, b_), (a, 0, a, b_)]:
            d.line((cx + xa, cy + ya, cx + xb, cy + yb), fill=seg, width=t)
        d.ellipse((cx + a + t, cy + b_ - t / 2, cx + a + 2.2 * t, cy + b_ + t / 1.2), fill=seg)
    v = np.array([[x0, -y1, z], [x1, -y1, z], [x1, -y0, z], [x0, -y0, z]]) / 1000
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    mat = PBRMaterial(baseColorTexture=img, metallicFactor=0.0, roughnessFactor=0.35)
    return trimesh.Trimesh(vertices=v, faces=[[0, 1, 2], [0, 2, 3]], visual=TextureVisuals(uv=uv, material=mat),
                           process=False)


def modelos_proprios(trimesh, info, esp_mm):
    """Modelos simples para os footprints que nao tem 3D na biblioteca do KiCad."""
    out = []
    z = esp_mm
    for c in info.get('sem_modelo', []):
        x0, y0, x1, y1 = c['bb']
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        fp = c['fp']
        if 'Display_7seg' in fp:
            m = 0.4
            out += [_caixa(trimesh, x0 + m, y0 + m, x1 - m, y1 - m, z + 0.5, z + 8.0, (235, 235, 230, 255)),
                    _face_display(trimesh, x0 + m, y0 + m, x1 - m, y1 - m, z + 8.02)]
        elif 'SW_Slide' in fp:
            horiz = (x1 - x0) >= (y1 - y0)
            L, P = 10.0, 4.4
            ax, ay = (L / 2, P / 2) if horiz else (P / 2, L / 2)
            out.append(_caixa(trimesh, cx - ax, cy - ay, cx + ax, cy + ay, z + 0.3, z + 5.0, (30, 30, 32, 255)))
            bx, by = (1.2, 0.9) if horiz else (0.9, 1.2)
            out.append(_caixa(trimesh, cx - 1.6 - bx, cy - by, cx - 1.6 + bx, cy + by, z + 5.0, z + 8.5,
                              (215, 215, 210, 255)) if horiz else
                       _caixa(trimesh, cx - bx, cy - 1.6 - by, cx + bx, cy - 1.6 + by, z + 5.0, z + 8.5,
                              (215, 215, 210, 255)))
        elif 'Potentiometer' in fp:
            m = 1.0
            out.append(_caixa(trimesh, x0 + m, y0 + m, x1 - m, y1 - m, z + 0.5, z + 7.0, (40, 70, 140, 255)))
            out.append(_cilindro(trimesh, cx, cy, 3.0, z + 7.0, z + 9.0, (190, 190, 185, 255)))
            out.append(_cilindro(trimesh, cx, cy, 3.0, z + 9.0, z + 20.0, (165, 165, 160, 255)))
        elif 'Fuse' in fp:
            out.append(_caixa(trimesh, x0 + 0.2, cy - 1.6, x1 - 0.2, cy + 1.6, z + 3.0, z + 13.0, (235, 190, 40, 255)))
        elif 'bornier' in fp or 'TerminalBlock' in fp:
            m = 0.3
            out.append(_caixa(trimesh, x0 + m, y0 + m, x1 - m, y1 - m, z, z + 10.0, (40, 110, 60, 255)))
        else:
            m = 0.5
            out.append(_caixa(trimesh, x0 + m, y0 + m, x1 - m, y1 - m, z, z + 5.0, (90, 90, 95, 255)))
    return out


def montar_glb(step, glb, stl, tex_topo, tex_fundo, info, td):
    import cascadio
    import trimesh
    from trimesh.visual.material import PBRMaterial
    from trimesh.visual import TextureVisuals
    bruto = os.path.join(td, 'bruto.glb')
    cascadio.step_to_glb(step, bruto, tol_linear=0.05, tol_angular=0.5)
    cena = trimesh.load(bruto)
    esp = 0.0016
    for nome, g in cena.geometry.items():
        if nome.endswith(' PCB'):
            g.visual = trimesh.visual.ColorVisuals(g, face_colors=np.tile(COR_BORDA, (len(g.faces), 1)))
            zmin, zmax = g.bounds[0][2], g.bounds[1][2]
            esp = zmax - zmin
    W, H = info['w'] / 1000.0, info['h'] / 1000.0

    def plano(img, z, para_baixo):
        v = np.array([[0, -H, z], [W, -H, z], [W, 0, z], [0, 0, z]])
        f = np.array([[0, 2, 1], [0, 3, 2]]) if para_baixo else np.array([[0, 1, 2], [0, 2, 3]])
        uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
        mat = PBRMaterial(baseColorTexture=img, metallicFactor=0.0, roughnessFactor=0.55, alphaMode='MASK',
                          alphaCutoff=0.5, doubleSided=False)
        return trimesh.Trimesh(vertices=v, faces=f, visual=TextureVisuals(uv=uv, material=mat), process=False)

    for i, m in enumerate(modelos_proprios(trimesh, info, esp * 1000)):
        cena.add_geometry(m, geom_name=f'modelo_proprio_{i}', node_name=f'modelo_proprio_{i}')
    # STL (sem cores) antes das texturas, em milimetros
    malha = cena.to_geometry()
    malha.apply_scale(1000.0)
    malha.export(stl)
    cena.add_geometry(plano(tex_topo, esp + 0.00003, False), geom_name='superficie_topo', node_name='superficie_topo')
    cena.add_geometry(plano(tex_fundo, -0.00003, True), geom_name='superficie_fundo', node_name='superficie_fundo')
    cena.export(glb)


def processar(nome):
    pcb = os.path.join(KICAD, nome, nome + '.kicad_pcb')
    os.makedirs(os.path.join(D3, 'modelos'), exist_ok=True)
    os.makedirs(os.path.join(D3, 'stl'), exist_ok=True)
    os.makedirs(os.path.join(D3, 'texturas'), exist_ok=True)
    info = dados_placa(pcb)
    escala = min(PX_MM, MAX_PX / max(info['w'], info['h']))
    with tempfile.TemporaryDirectory() as td:
        topo = textura(pcb, 'topo', info, td, escala)
        fundo = textura(pcb, 'fundo', info, td, escala)
        tt = os.path.join(D3, 'texturas', f'{nome}-topo.png')
        tf = os.path.join(D3, 'texturas', f'{nome}-fundo.png')
        topo.save(tt, optimize=True)
        # a imagem do fundo e salva espelhada = como voce ve a placa virada
        fundo.transpose(Image.FLIP_LEFT_RIGHT).save(tf, optimize=True)
        step = os.path.join(FAB, nome, nome + '.step')
        exportar_step(pcb, step, info)
        glb = os.path.join(D3, 'modelos', nome + '.glb')
        stl = os.path.join(D3, 'stl', nome + '.stl')
        montar_glb(step, glb, stl, topo, fundo, info, td)
    res = {'placa': nome, 'largura_mm': round(info['w'], 2), 'altura_mm': round(info['h'], 2),
           'furos': len(info['furos']), 'vias': info['vias'], 'componentes': info['comps'],
           'glb_kb': round(os.path.getsize(glb) / 1024), 'stl_kb': round(os.path.getsize(stl) / 1024),
           'step_kb': round(os.path.getsize(step) / 1024)}
    return res


def main():
    alvo = sys.argv[1:] or placas()
    meta_p = os.path.join(D3, 'placas3d.json')
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    for nome in alvo:
        r = processar(nome)
        meta[nome] = r
        print(f'{nome}: {r["largura_mm"]}x{r["altura_mm"]} mm  furos={r["furos"]}  '
              f'glb={r["glb_kb"]} kB  stl={r["stl_kb"]} kB  step={r["step_kb"]} kB', flush=True)
    json.dump(dict(sorted(meta.items())), open(meta_p, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
