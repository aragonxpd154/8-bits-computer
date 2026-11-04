#!/usr/bin/env python3
"""Gera o visualizador 3D interativo das placas (docs/3d/visualizador.html).

Le os textos de tools/placas_info.py, os conectores de tools/gerador-kicad/designs.py e as medidas
de docs/3d/placas3d.json (criado por tools/render3d.py). Os modelos ficam em docs/3d/modelos/*.glb.

Uso:  python3 tools/gerar_visualizador.py [--corpo saida.html]
      --corpo grava so o conteudo da pagina (sem <!doctype>/<head>), para publicar como Artifact.

Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import re
import sys
import json
import html

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(AQUI, 'gerador-kicad'))
sys.path.insert(0, AQUI)
import designs  # noqa: E402
from placas_info import PLACAS, PASTAS  # noqa: E402

GITHUB = 'https://github.com/aragonxpd154/8-bits-computer/blob/main/'


def md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t


def nome_sinal(n):
    return n.replace('~{', '/').replace('}', '') if n else 'NC'


def destinos():
    """(placa, J) -> texto de onde o cabo vai; e o inverso para o backplane."""
    bs = {b.key: b for b in designs.all_boards()}
    bp = bs['BACKPLANE']
    d = {}
    for placa, j, dest in designs.CABOS:
        if isinstance(dest, tuple):
            d[(placa, j)] = f'cabo direto → {PLACAS[dest[0]]["nome"]} {dest[1]}'
            d[dest] = f'cabo direto → {PLACAS[placa]["nome"]} {j}'
        else:
            ref = bp.header_map[dest]
            d[(placa, j)] = f'backplane {ref} ({dest})'
            d[('BACKPLANE', ref)] = f'{PLACAS[placa]["nome"]} {j}'
    return d


def conectores(b, dest):
    out = []
    for c in b.comps.values():
        if c.group not in ('J', 'PWRIN') or not c.ref.startswith('J'):
            continue
        n = len(c.pins)
        labels = c.pinlabels or [nome_sinal(c.pins.get(str(i + 1))) for i in range(n)]
        out.append({'ref': c.ref, 'nome': c.value, 'pinos': labels[:4] if c.sym == 'Conn_01x04' else labels,
                    'liga': dest.get((b.key, c.ref), '')})
    out.sort(key=lambda x: int(re.sub(r'\D', '', x['ref']) or 0))
    return out


def dados():
    meta = json.load(open(os.path.join(RAIZ, 'docs', '3d', 'placas3d.json')))
    dest = destinos()
    lista = []
    for b in designs.all_boards():
        info = PLACAS[b.key]
        pasta = PASTAS[b.key]
        m = meta.get(pasta, {})
        ics = [c for c in b.comps.values() if c.group == 'IC']
        lista.append({
            'id': pasta, 'ordem': info['ordem'], 'nome': info['nome'], 'resumo': md_inline(info['resumo']),
            'funcao': md_inline(info['funcao']),
            'funcionamento': [md_inline(p) for p in info['funcionamento']],
            'blocos': [[md_inline(a), md_inline(t)] for a, t in info['blocos']],
            'leds': [[md_inline(a), md_inline(t)] for a, t in info['leds']],
            'controles': [[md_inline(a), md_inline(t)] for a, t in info['controles']],
            'conectores': conectores(b, dest),
            'w': m.get('largura_mm'), 'h': m.get('altura_mm'), 'furos': m.get('furos'),
            'ncomp': len(b.comps), 'nci': len(ics),
            'pagina': GITHUB + f'docs/placas/{pasta}.md',
        })
    lista.sort(key=lambda x: x['ordem'])
    return lista


CABECA = '''<title>Placas 3D — Computador 8 Bits</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="As 14 placas do Computador 8 Bits v3.0 de Marcos Silva dos Santos em 3D, com a função de cada uma.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Semi+Condensed:wght@500;600;700&display=swap">
'''

ESTILO = r'''<style>
/* Layout: bancada — lista de placas | placa em 3D | ficha técnica da placa. No celular empilha. */
:root {
  --bg: #eef1ec; --panel: #f8faf6; --ink: #17201a; --muted: #56625a; --line: #d2dad1;
  --mask: #1d5c34; --mask-soft: #dceadf; --copper: #a85f22; --stage-a: #e4eae2; --stage-b: #cfd8cd;
  --pin: #ffffff;
  --f-display: "Saira Semi Condensed", "Arial Narrow", system-ui, sans-serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0d120f; --panel: #141b16; --ink: #e2e9e1; --muted: #95a298; --line: #263129;
  --mask: #6cc58b; --mask-soft: #1c2c21; --copper: #e39a5c; --stage-a: #1b241e; --stage-b: #0f1511; --pin: #1b241e;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0d120f; --panel: #141b16; --ink: #e2e9e1; --muted: #95a298; --line: #263129;
  --mask: #6cc58b; --mask-soft: #1c2c21; --copper: #e39a5c; --stage-a: #1b241e; --stage-b: #0f1511; --pin: #1b241e;
  color-scheme: dark; }
*, *::before, *::after { box-sizing: border-box; }
html, body { height: 100%; }
body { margin: 0; }
[hidden] { display: none !important; }
body { background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 15px; line-height: 1.55; }
.app { display: grid; grid-template-columns: 250px minmax(0, 1fr) 380px; grid-template-rows: auto minmax(0, 1fr);
  height: 100%; min-height: 560px; }
header.topo { grid-column: 1 / -1; display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;
  padding-block: 12px; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); border-bottom: 1px solid var(--line); background: var(--panel); }
header.topo h1 { font-family: var(--f-display); font-weight: 700; font-size: 22px; letter-spacing: .01em; margin: 0; }
header.topo .autor { color: var(--muted); font-size: 13px; }
header.topo .ver { margin-left: auto; font-family: var(--f-mono); font-size: 12px; color: var(--muted); }
nav.lista { border-right: 1px solid var(--line); overflow-y: auto; padding: 10px 8px; background: var(--panel); }
nav.lista button { display: grid; grid-template-columns: 26px minmax(0, 1fr); align-items: baseline; gap: 6px; width: 100%;
  text-align: left; border: 0; background: transparent; color: var(--ink); padding: 7px 8px; border-radius: 6px;
  font: inherit; font-size: 14px; cursor: pointer; }
nav.lista button .n { font-family: var(--f-mono); font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }
nav.lista button:hover { background: var(--mask-soft); }
nav.lista button[aria-current="true"] { background: var(--mask); color: var(--panel); }
nav.lista button[aria-current="true"] .n { color: inherit; opacity: .8; }
nav.lista button:focus-visible, .ctl button:focus-visible, .ctl label:focus-within { outline: 2px solid var(--copper); outline-offset: 2px; }
.palco { position: relative; min-width: 0; background: radial-gradient(120% 90% at 50% 35%, var(--stage-a), var(--stage-b)); }
.palco canvas { display: block; width: 100%; height: 100%; touch-action: none; }
.ctl { position: absolute; left: 12px; right: 12px; bottom: 12px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; pointer-events: none; }
.ctl > * { pointer-events: auto; }
.ctl .grp { display: flex; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.ctl button, .ctl label { font: 500 13px var(--f-body); color: var(--ink); background: transparent; border: 0; padding: 7px 12px; cursor: pointer;
  display: flex; align-items: center; gap: 6px; }
.ctl .grp > * + * { border-left: 1px solid var(--line); }
.ctl button[aria-pressed="true"] { background: var(--mask); color: var(--panel); }
.ctl input { accent-color: var(--mask); margin: 0; }
.medida { position: absolute; top: 12px; left: 12px; font: 500 12px var(--f-mono); color: var(--muted);
  background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; font-variant-numeric: tabular-nums; }
.estado { position: absolute; inset: 0; display: grid; place-items: center; font: 500 14px var(--f-mono); color: var(--muted); pointer-events: none; }
aside.ficha { border-left: 1px solid var(--line); overflow-y: auto; background: var(--panel);
  padding-block: 18px 28px; padding-inline: 20px; }
.ficha h2 { font-family: var(--f-display); font-weight: 700; font-size: 28px; line-height: 1.1; margin: 0 0 6px; text-wrap: balance; }
.ficha .resumo { color: var(--muted); margin: 0 0 12px; }
.ficha .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 16px; padding: 0; list-style: none; }
.ficha .chips li { font: 500 12px var(--f-mono); padding: 3px 8px; border-radius: 4px; background: var(--mask-soft); color: var(--ink); font-variant-numeric: tabular-nums; }
.ficha h3 { font: 600 11px var(--f-body); text-transform: uppercase; letter-spacing: .09em; color: var(--copper); margin: 22px 0 8px; }
.ficha p { margin: 0 0 10px; }
.ficha ol, .ficha ul { margin: 0; padding-left: 18px; }
.ficha li { margin: 0 0 8px; }
.tab { width: 100%; border-collapse: collapse; font-size: 14px; }
.tab td { padding: 6px 0; border-top: 1px solid var(--line); vertical-align: top; }
.tab td:first-child { font: 500 13px var(--f-mono); padding-right: 12px; white-space: nowrap; color: var(--mask); }
.con { border-top: 1px solid var(--line); padding: 8px 0; }
.con .cab { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
.con .ref { font: 600 13px var(--f-mono); color: var(--mask); }
.con .nm { font: 500 13px var(--f-body); }
.con .liga { font-size: 12px; color: var(--muted); width: 100%; }
.pinos { display: flex; gap: 4px; margin-top: 5px; flex-wrap: wrap; }
.pinos span { font: 500 11.5px var(--f-mono); border: 1px solid var(--line); background: var(--pin); border-radius: 3px; padding: 1px 6px; }
.pinos span:first-child { border-color: var(--copper); }
.pinos span b { font-weight: 400; color: var(--muted); margin-right: 3px; }
details summary { cursor: pointer; color: var(--mask); font-weight: 500; }
a { color: var(--mask); }
.mais { display: inline-block; margin-top: 18px; font-weight: 600; }
code { font-family: var(--f-mono); font-size: .92em; }
@media (max-width: 1100px) { .app { grid-template-columns: 220px minmax(0, 1fr); }
  aside.ficha { grid-column: 1 / -1; border-left: 0; border-top: 1px solid var(--line); } .app { height: auto; } .palco { height: 70vh; } }
@media (max-width: 720px) {
  .app { display: block; }
  nav.lista { display: flex; overflow-x: auto; gap: 4px; border-right: 0; border-bottom: 1px solid var(--line); padding-inline: 12px; }
  nav.lista button { width: auto; flex: 0 0 auto; white-space: nowrap; display: flex; }
  .palco { height: 62vh; min-height: 340px; }
  aside.ficha { padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  header.topo .ver { margin-left: 0; }
}
.render header.topo, .render nav.lista, .render aside.ficha, .render .ctl, .render .medida, .render .estado { display: none !important; }
.render .app { display: block; height: 100%; } .render .palco { height: 100%; background: transparent; } .render body, body.render { background: transparent; }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>
'''

CORPO = r'''<div class="app">
  <header class="topo">
    <h1>Computador 8 Bits — placas em 3D</h1>
    <span class="autor">projeto de Marcos Silva dos Santos (MarcosObel)</span>
    <span class="ver">v3.0 · 14 placas · KiCad</span>
  </header>
  <nav class="lista" id="lista" aria-label="Placas"></nav>
  <main class="palco" id="palco">
    <canvas id="cena" aria-label="Modelo 3D da placa — arraste para girar, role para aproximar"></canvas>
    <div class="medida" id="medida"></div>
    <div class="estado" id="estado">carregando…</div>
    <div class="ctl">
      <div class="grp" role="group" aria-label="Vista">
        <button type="button" id="v-3d" aria-pressed="true">3D</button>
        <button type="button" id="v-topo" aria-pressed="false">Topo</button>
        <button type="button" id="v-fundo" aria-pressed="false">Fundo</button>
      </div>
      <div class="grp">
        <label for="c-comp"><input type="checkbox" id="c-comp" checked> Componentes</label>
        <label for="c-gira"><input type="checkbox" id="c-gira"> Girar</label>
      </div>
    </div>
  </main>
  <aside class="ficha" id="ficha" aria-live="polite"></aside>
</div>
<script>window.PLACAS = __DADOS__; window.BASE_MODELOS = "__BASE__"; window.MODELOS_B64 = __B64__;</script>
<script type="importmap">{"imports": {"three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const P = window.PLACAS, $ = (id) => document.getElementById(id);
if (/[?&]render\b/.test(location.search)) document.body.classList.add('render');
const canvas = $('cena'), palco = $('palco');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
const cena = new THREE.Scene();
const pm = new THREE.PMREMGenerator(renderer);
cena.environment = pm.fromScene(new RoomEnvironment(renderer), 0.04).texture;
const sol = new THREE.DirectionalLight(0xffffff, 1.4); sol.position.set(0.15, 0.35, 0.2); cena.add(sol);
cena.add(new THREE.HemisphereLight(0xffffff, 0x334433, 0.5));
const cam = new THREE.PerspectiveCamera(35, 1, 0.001, 10);
const ctl = new OrbitControls(cam, canvas);
ctl.enableDamping = true; ctl.dampingFactor = 0.08; ctl.autoRotateSpeed = 1.2;
const loader = new GLTFLoader();
const cache = new Map();
let atual = null, raio = 0.1, vista = '3d', anim = null;
const reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function tamanho() {
  const r = palco.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false);
  cam.aspect = r.width / Math.max(r.height, 1); cam.updateProjectionMatrix();
}
new ResizeObserver(tamanho).observe(palco);

function alvoVista(v) {
  const t = Math.tan(THREE.MathUtils.degToRad(cam.fov / 2));
  const d = Math.max(raio / t * 0.8, raio / (t * cam.aspect)) * (document.body.classList.contains('render') ? 1.45 : 1.18);
  if (v === 'topo') return new THREE.Vector3(0, d, 0.0001);
  if (v === 'fundo') return new THREE.Vector3(0, -d, 0.0001);
  return new THREE.Vector3(0.38, 0.72, 0.58).normalize().multiplyScalar(d * 1.05);
}
function irPara(v, instantaneo) {
  vista = v;
  ['3d', 'topo', 'fundo'].forEach((k) => $('v-' + k).setAttribute('aria-pressed', String(k === v)));
  const fim = alvoVista(v), ini = cam.position.clone();
  if (instantaneo || reduz) { cam.position.copy(fim); ctl.target.set(0, 0, 0); ctl.update(); return; }
  const t0 = performance.now();
  anim = (t) => { const k = Math.min((t - t0) / 650, 1), e = 1 - Math.pow(1 - k, 3);
    cam.position.lerpVectors(ini, fim, e); ctl.target.set(0, 0, 0); if (k >= 1) anim = null; };
}
function aplicaComponentes() {
  if (!atual) return;
  const mostra = $('c-comp').checked;
  atual.traverse((o) => { if (o.isMesh && !o.userData.placa) o.visible = mostra; });
}

async function carrega(p) {
  $('estado').hidden = false; $('estado').textContent = 'carregando ' + p.nome + '…';
  let g = cache.get(p.id);
  if (!g) {
    try {
      let gltf;
      if (window.MODELOS_B64) {   // versao publicada: o .glb vai como texto base64
        const r = await fetch(window.BASE_MODELOS + p.id + '.glb.txt');
        if (!r.ok) throw new Error(r.status);
        const bin = atob((await r.text()).trim()), u8 = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
        gltf = await loader.parseAsync(u8.buffer, '');
      } else {
        gltf = await loader.loadAsync(window.BASE_MODELOS + p.id + '.glb');
      }
      g = new THREE.Group();
      const m = gltf.scene;
      m.rotation.x = -Math.PI / 2;          // KiCad: placa no plano XY -> deitada no plano XZ
      m.traverse((o) => { if (o.isMesh) {
        o.userData.placa = /PCB|superficie/i.test(o.name) || /PCB|superficie/i.test(o.parent && o.parent.name || '');
        if (o.material && o.material.map) { o.material.map.anisotropy = renderer.capabilities.getMaxAnisotropy(); o.material.envMapIntensity = 0.35; }
      } });
      g.add(m);
      const box = new THREE.Box3().setFromObject(g), c = box.getCenter(new THREE.Vector3());
      m.position.sub(c);
      cache.set(p.id, g);
    } catch (e) {
      $('estado').textContent = 'Não foi possível abrir o modelo 3D (' + p.id + '.glb). Abra esta página por um servidor (veja docs/3d/README.md).';
      return;
    }
  }
  if (atual) cena.remove(atual);
  atual = g; cena.add(g);
  const s = new THREE.Box3().setFromObject(g).getSize(new THREE.Vector3());
  raio = Math.max(s.x, s.z) / 2;
  aplicaComponentes(); irPara(vista, true);
  $('estado').hidden = true;
  window.__pronto = p.id;
}

const br = (v) => String(v).replace('.', ',');
function ficha(p) {
  const lista = (arr) => arr.length ? '<table class="tab"><tbody>' + arr.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join('') + '</tbody></table>' : '';
  const con = (c) => `<div class="con"><div class="cab"><span class="ref">${c.ref}</span><span class="nm">${c.nome}</span>${c.liga ? `<span class="liga">${c.liga}</span>` : ''}</div>`
    + `<div class="pinos">${c.pinos.map((s, i) => `<span><b>${i + 1}</b>${s}</span>`).join('')}</div></div>`;
  const cons = p.conectores.length > 12
    ? `${p.conectores.slice(0, 4).map(con).join('')}<details><summary>mais ${p.conectores.length - 4} conectores</summary>${p.conectores.slice(4).map(con).join('')}</details>`
    : p.conectores.map(con).join('');
  $('ficha').innerHTML = `<h2>${p.nome}</h2><p class="resumo">${p.resumo}</p>
    <ul class="chips"><li>${br(p.w)} × ${br(p.h)} mm</li><li>${p.nci} ${p.nci === 1 ? 'CI' : 'CIs'}</li><li>${p.ncomp} componentes</li><li>${p.furos} furos</li><li>2 camadas</li></ul>
    <h3>Função</h3><p>${p.funcao}</p>
    <h3>Como funciona</h3>${p.funcionamento.map((t) => `<p>${t}</p>`).join('')}
    <h3>O que cada parte faz</h3>${lista(p.blocos)}
    ${p.leds.length ? '<h3>LEDs</h3>' + lista(p.leds) : ''}
    ${p.controles.length ? '<h3>Chaves e ajustes</h3>' + lista(p.controles) : ''}
    <h3>Conectores · pino 1 → 4</h3>${cons}
    <a class="mais" href="${p.pagina}" target="_blank" rel="noopener">Página completa da placa no GitHub ↗</a>`;
  $('medida').textContent = `${br(p.w)} × ${br(p.h)} mm`;
}

function seleciona(id, rolar) {
  const p = P.find((x) => x.id === id) || P[0];
  document.querySelectorAll('#lista button').forEach((b) => b.setAttribute('aria-current', String(b.dataset.id === p.id)));
  ficha(p); carrega(p);
  if (location.hash.slice(1) !== p.id) history.replaceState(null, '', '#' + p.id);
  if (rolar) { const b = document.querySelector(`#lista button[data-id="${p.id}"]`); b && b.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
}

$('lista').innerHTML = P.map((p) => `<button type="button" data-id="${p.id}"><span class="n">${String(p.ordem).padStart(2, '0')}</span><span>${p.nome}</span></button>`).join('');
$('lista').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) seleciona(b.dataset.id); });
['3d', 'topo', 'fundo'].forEach((k) => $('v-' + k).addEventListener('click', () => irPara(k)));
$('c-comp').addEventListener('change', aplicaComponentes);
$('c-gira').addEventListener('change', (e) => { ctl.autoRotate = e.target.checked; });
window.addEventListener('hashchange', () => seleciona(location.hash.slice(1), true));
window.__vista = (v) => irPara(v, true);
window.__componentes = (on) => { $('c-comp').checked = on; aplicaComponentes(); };

tamanho();
seleciona(location.hash.slice(1), true);
renderer.setAnimationLoop((t) => { if (anim) anim(t); ctl.update(); renderer.render(cena, cam); });
</script>
'''


def gerar(base='modelos/', b64=False):
    d = json.dumps(dados(), ensure_ascii=False).replace('</', '<\\/')
    return CORPO.replace('__DADOS__', d).replace('__BASE__', base).replace('__B64__', 'true' if b64 else 'false')


def main():
    if '--corpo' in sys.argv:
        saida = sys.argv[sys.argv.index('--corpo') + 1]
        open(saida, 'w').write(CABECA + ESTILO + gerar(b64=True))
        import base64
        pm = os.path.join(os.path.dirname(os.path.abspath(saida)), 'modelos')
        os.makedirs(pm, exist_ok=True)
        for f in sorted(os.listdir(os.path.join(RAIZ, 'docs', '3d', 'modelos'))):
            if f.endswith('.glb'):
                raw = open(os.path.join(RAIZ, 'docs', '3d', 'modelos', f), 'rb').read()
                open(os.path.join(pm, f + '.txt'), 'w').write(base64.b64encode(raw).decode())
        print('corpo ->', saida)
        return
    saida = os.path.join(RAIZ, 'docs', '3d', 'visualizador.html')
    doc = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + CABECA + ESTILO + '</head>\n<body>\n' + gerar() + '</body>\n</html>\n')
    open(saida, 'w').write(doc)
    print('visualizador ->', saida)


if __name__ == '__main__':
    main()
