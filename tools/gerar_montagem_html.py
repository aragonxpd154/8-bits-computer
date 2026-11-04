#!/usr/bin/env python3
"""Gera docs/3d/montagem.html: o computador completo montado em 3D (base de madeira, espacadores,
tampa de acrilico, 58 cabos) com os LEDs e o display funcionando, rodando um programa de verdade.

Le docs/3d/montagem.json (tools/montagem3d.py) e os modelos docs/3d/modelos/*.glb.
Uso:  python3 tools/gerar_montagem_html.py [--corpo saida.html]
Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import sys
import json

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

CABECA = '''<title>Computador 8 Bits Montado</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="As 14 placas do Computador 8 Bits v3.0 montadas numa base de madeira com tampa de acrílico, rodando um programa.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Semi+Condensed:wght@600;700&display=swap">
'''

ESTILO = r'''<style>
/* Layout: palco 3D ocupando a tela; barra de comandos embaixo; painel de estado da CPU no canto. */
:root {
  --bg: #e9ede7; --panel: #f8faf6; --ink: #17201a; --muted: #56625a; --line: #d2dad1;
  --mask: #1d5c34; --copper: #a85f22; --stage-a: #eef1ec; --stage-b: #cfd6cc; --led: #c0302b;
  --f-display: "Saira Semi Condensed", "Arial Narrow", system-ui, sans-serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0c100d; --panel: #141b16; --ink: #e2e9e1; --muted: #95a298; --line: #263129;
  --mask: #6cc58b; --copper: #e39a5c; --stage-a: #1c241e; --stage-b: #0b0f0c; --led: #ff6b5e; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0c100d; --panel: #141b16; --ink: #e2e9e1; --muted: #95a298; --line: #263129;
  --mask: #6cc58b; --copper: #e39a5c; --stage-a: #1c241e; --stage-b: #0b0f0c; --led: #ff6b5e; color-scheme: dark; }
*, *::before, *::after { box-sizing: border-box; }
html, body { height: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 14px; }
[hidden] { display: none !important; }
.app { position: relative; height: 100%; min-height: 520px;
  background: radial-gradient(120% 90% at 50% 30%, var(--stage-a), var(--stage-b)); overflow: hidden; }
canvas#cena { display: block; width: 100%; height: 100%; touch-action: none; }
.topo { position: absolute; top: calc(12px + env(safe-area-inset-top, 0px)); left: max(16px, env(safe-area-inset-left, 0px));
  right: max(16px, env(safe-area-inset-right, 0px)); display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; pointer-events: none; }
.titulo h1 { font: 700 22px/1.1 var(--f-display); margin: 0; letter-spacing: .01em; }
.titulo p { margin: 3px 0 0; color: var(--muted); font-size: 13px; }
.cpu { pointer-events: auto; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
  font: 500 12.5px/1.55 var(--f-mono); font-variant-numeric: tabular-nums; min-width: 230px; }
.cpu .l { color: var(--muted); display: inline-block; width: 62px; }
.cpu .instr { font-weight: 600; color: var(--copper); }
.cpu .sinais { color: var(--mask); }
.ctl { position: absolute; left: max(16px, env(safe-area-inset-left, 0px)); right: max(16px, env(safe-area-inset-right, 0px));
  bottom: calc(14px + env(safe-area-inset-bottom, 0px)); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.grp { display: flex; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.grp > * + * { border-left: 1px solid var(--line); }
.ctl button, .ctl label, .ctl select { font: 500 13px var(--f-body); color: var(--ink); background: transparent; border: 0;
  padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 6px; }
.ctl select { appearance: auto; }
.ctl button[aria-pressed="true"] { background: var(--mask); color: var(--panel); }
.ctl input { accent-color: var(--mask); margin: 0; }
.ctl button:focus-visible, .ctl select:focus-visible, .ctl label:focus-within { outline: 2px solid var(--copper); outline-offset: 2px; }
.estado { position: absolute; inset: 0; display: grid; place-items: center; font: 500 14px var(--f-mono); color: var(--muted); pointer-events: none; }
.render .topo, .render .ctl, .render .estado { display: none !important; }
.render .app, body.render { background: transparent; }
@media (max-width: 640px) { .cpu { min-width: 0; font-size: 11.5px; } .titulo h1 { font-size: 18px; } .titulo p { display: none; } }
</style>
'''

CORPO = r'''<div class="app" id="app">
  <canvas id="cena" aria-label="Computador 8 Bits montado — arraste para girar, role para aproximar"></canvas>
  <div class="topo">
    <div class="titulo"><h1>Computador 8 Bits — montado</h1><p>14 placas · 58 cabos por baixo das placas, presos com enforca-gatos · base de madeira e tampa de acrílico · Marcos Silva dos Santos</p></div>
    <div class="cpu" id="cpu" aria-live="off"></div>
  </div>
  <div class="estado" id="estado">carregando as placas…</div>
  <div class="ctl">
    <div class="grp">
      <button type="button" id="b-run" aria-pressed="true">⏸ Pausar</button>
      <button type="button" id="b-passo">Passo</button>
      <button type="button" id="b-reset">Reset</button>
    </div>
    <div class="grp">
      <label for="s-prog">Programa <select id="s-prog"></select></label>
      <label for="s-vel">Clock <select id="s-vel"><option value="1">1 Hz</option><option value="3">3 Hz</option><option value="8" selected>8 Hz</option><option value="20">20 Hz</option><option value="60">60 Hz</option></select></label>
    </div>
    <div class="grp">
      <label for="c-tampa"><input type="checkbox" id="c-tampa" checked> Tampa</label>
      <label for="c-cabos"><input type="checkbox" id="c-cabos" checked> Cabos</label>
      <button type="button" id="b-vista">Vista de cima</button>
    </div>
  </div>
</div>
<script>window.BASE_MODELOS = "__BASE__"; window.MODELOS_B64 = __B64__; window.MONTAGEM = __DADOS__;</script>
<script type="importmap">{"imports": {"three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const M = window.MONTAGEM, $ = (id) => document.getElementById(id);
const RENDER = /[?&]render\b/.test(location.search), LEVE = RENDER || /[?&]leve\b/.test(location.search);
if (RENDER) document.body.classList.add('render');
const mm = (v) => v / 1000;
const [BW, BD, BT] = M.base, ESP = M.espacador, TAMPA = M.tampa;
const ZB = BT;                      // topo da base (mm) = y no mundo
const ZP = ZB + ESP;                // face de baixo das placas

const canvas = $('cena'), app = $('app');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.95;
renderer.shadowMap.enabled = !LEVE; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const cena = new THREE.Scene();
cena.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(renderer), 0.04).texture;
const sol = new THREE.DirectionalLight(0xffffff, 1.6); sol.position.set(0.2, 1.2, 0.6); sol.castShadow = true;
sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -0.5, right: 0.5, top: 0.5, bottom: -0.5, near: 0.1, far: 3 });
cena.add(sol); cena.add(new THREE.HemisphereLight(0xffffff, 0x3a2f22, 0.45));
const cam = new THREE.PerspectiveCamera(32, 1, 0.01, 20);
const ctl = new OrbitControls(cam, canvas); ctl.enableDamping = true; ctl.dampingFactor = 0.08; ctl.maxPolarAngle = Math.PI * 0.49;
const mundo = new THREE.Group(); mundo.position.set(-mm(BW) / 2, 0, -mm(BD) / 2); cena.add(mundo);
ctl.target.set(0, mm(40), 0);

function tamanho() { const r = app.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); cam.aspect = r.width / Math.max(r.height, 1); cam.updateProjectionMatrix(); }
new ResizeObserver(tamanho).observe(app); tamanho();
function vista(cima) {
  const d = 1.28 / Math.min(1, cam.aspect * 0.85);
  if (cima) cam.position.set(0, d * 1.12, 0.001); else cam.position.set(0.04 * d, 0.58 * d, 0.68 * d);
  ctl.target.set(0, cima ? 0 : mm(30), cima ? 0 : mm(20)); ctl.update();
}
vista(false);

// ---------- base de madeira ----------
function texMadeira() {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 1024; const g = c.getContext('2d');
  g.fillStyle = '#a06b3a'; g.fillRect(0, 0, c.width, c.height);
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 520; i++) {
    const y = rnd() * c.height, a = 0.05 + rnd() * 0.12, w = 1 + rnd() * 4;
    g.strokeStyle = rnd() > 0.5 ? `rgba(70,38,14,${a})` : `rgba(230,180,120,${a * 0.8})`; g.lineWidth = w; g.beginPath();
    for (let x = 0; x <= c.width; x += 32) g.lineTo(x, y + Math.sin(x / 260 + i) * 6 + Math.sin(x / 47 + i * 3) * 1.5);
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
const madeira = new THREE.MeshStandardMaterial({ map: texMadeira(), roughness: 0.62, metalness: 0 });
const lateral = new THREE.MeshStandardMaterial({ color: 0x6e4524, roughness: 0.7 });
const base = new THREE.Mesh(new THREE.BoxGeometry(mm(BW), mm(BT), mm(BD)), [lateral, lateral, madeira, lateral, lateral, lateral]);
base.position.set(mm(BW) / 2, mm(BT) / 2, mm(BD) / 2); base.receiveShadow = true; mundo.add(base);
// plaquinha
{ const c = document.createElement('canvas'); c.width = 1024; c.height = 160; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 160); gr.addColorStop(0, '#e9c873'); gr.addColorStop(1, '#b08a3e');
  g.fillStyle = gr; g.fillRect(0, 0, 1024, 160); g.strokeStyle = '#6b5122'; g.lineWidth = 6; g.strokeRect(8, 8, 1008, 144);
  g.fillStyle = '#3b2a0c'; g.font = '700 54px "Saira Semi Condensed", Arial'; g.textAlign = 'center'; g.fillText('COMPUTADOR 8 BITS  v3.0', 512, 74);
  g.font = '500 30px "IBM Plex Sans", Arial'; g.fillText('Marcos Silva dos Santos (MarcosObel) · lógica TTL · GPL-3.0', 512, 122);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const p = new THREE.Mesh(new THREE.BoxGeometry(mm(150), mm(1.2), mm(23.4)), new THREE.MeshStandardMaterial({ map: t, metalness: 0.6, roughness: 0.35 }));
  p.position.set(mm(95), mm(BT + 0.6), mm(BD - 40)); mundo.add(p); }

// ---------- tampa de acrilico e colunas ----------
const tampaG = new THREE.Group(); mundo.add(tampaG);
{ const acr = new THREE.MeshPhysicalMaterial({ color: 0xe6f4ff, transparent: true, opacity: 0.07, roughness: 0.02, metalness: 0,
    clearcoat: 1, clearcoatRoughness: 0.03, depthWrite: false, side: THREE.FrontSide, envMapIntensity: 1.4 });
  const t = new THREE.Mesh(new THREE.BoxGeometry(mm(BW - 4), mm(5), mm(BD - 4)), acr); t.position.set(mm(BW) / 2, mm(ZB + TAMPA), mm(BD) / 2); tampaG.add(t);
  const borda = new THREE.LineSegments(new THREE.EdgesGeometry(t.geometry), new THREE.LineBasicMaterial({ color: 0xbfd9e6, transparent: true, opacity: 0.55 }));
  borda.position.copy(t.position); tampaG.add(borda);
  const alu = new THREE.MeshStandardMaterial({ color: 0xc9ccd1, metalness: 0.9, roughness: 0.3 });
  for (const [x, z] of [[14, 14], [BW - 14, 14], [14, BD - 14], [BW - 14, BD - 14], [BW / 2, 14], [BW / 2, BD - 14]]) {
    const c = new THREE.Mesh(new THREE.CylinderGeometry(mm(6), mm(6), mm(TAMPA), 24), alu); c.position.set(mm(x), mm(ZB + TAMPA / 2), mm(z)); c.castShadow = true; tampaG.add(c);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(mm(8), mm(8), mm(4), 24), alu); cap.position.set(mm(x), mm(ZB + TAMPA + 4.5), mm(z)); tampaG.add(cap);
  } }

// ---------- placas ----------
const loader = new GLTFLoader();
const latao = new THREE.MeshStandardMaterial({ color: 0xc9a227, metalness: 0.85, roughness: 0.35 });
const preto = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.5 });
const ledsVis = [];      // {mesh, sprite, placa, led}
let display = null;
const halo = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.25, 'rgba(255,255,255,0.55)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();

async function carregaGLB(id) {
  if (window.MODELOS_B64) {
    const r = await fetch(window.BASE_MODELOS + id + '.glb.txt'); if (!r.ok) throw new Error(id);
    const bin = atob((await r.text()).trim()), u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return loader.parseAsync(u8.buffer, '');
  }
  return loader.loadAsync(window.BASE_MODELOS + id + '.glb');
}

function montaPlaca(p, gltf) {
  const g = new THREE.Group(); g.position.set(mm(p.x), mm(ZP), mm(p.y)); mundo.add(g);
  const m = gltf.scene; m.rotation.x = -Math.PI / 2;
  m.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; if (o.material && o.material.map) o.material.envMapIntensity = 0.35; } });
  g.add(m);
  for (const [x, y] of p.furos) {
    const s = new THREE.Mesh(new THREE.CylinderGeometry(mm(2.8), mm(2.8), mm(ESP), 6), latao); s.position.set(mm(x), -mm(ESP / 2), mm(y)); s.castShadow = true; g.add(s);
    const n = new THREE.Mesh(new THREE.CylinderGeometry(mm(3), mm(3), mm(2.4), 6), latao); n.position.set(mm(x), mm(1.6 + 1.2), mm(y)); g.add(n);
  }
  for (const l of p.leds) {
    const cor = new THREE.Color(l.cor);
    const mat = new THREE.MeshBasicMaterial({ color: cor.clone().multiplyScalar(0.25), toneMapped: false });
    const esf = new THREE.Mesh(new THREE.SphereGeometry(mm(1.75), 16, 12), mat); esf.position.set(mm(l.x), mm(1.6 + 4.2), mm(l.y)); g.add(esf);
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: halo, color: cor, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0 }));
    sp.scale.set(mm(11), mm(11), 1); sp.position.copy(esf.position); g.add(sp);
    ledsVis.push({ esf, sp, cor, placa: p.key, led: l });
  }
  if (p.display) {
    const [x0, y0, x1, y1] = p.display, c = document.createElement('canvas'); c.width = 600; c.height = Math.round(600 * (y1 - y0) / (x1 - x0));
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    const pl = new THREE.Mesh(new THREE.PlaneGeometry(mm(x1 - x0), mm(y1 - y0)), new THREE.MeshBasicMaterial({ map: t, transparent: true, toneMapped: false, depthWrite: false }));
    pl.rotation.x = -Math.PI / 2; pl.position.set(mm((x0 + x1) / 2), mm(1.6 + 8.12), mm((y0 + y1) / 2)); g.add(pl);
    display = { c, t };
  }
}

// ---------- cabos ----------
const cabosG = new THREE.Group(); mundo.add(cabosG);
const CORES_FITA = [0x7a4a1e, 0xd62a2a, 0xf08a18, 0xf4d21c], CORES_PWR = [0xd62a2a, 0xd62a2a, 0x1b1b1b, 0x1b1b1b];
const ALT_HOUS = 1.6 + 2.5 + 14;           // topo do conector femea (mm acima da face de baixo da placa)
function cabos() {
  // Cada cabo sai do conector, desce pela borda mais proxima da placa, corre colado na base (por baixo das
  // placas, que ficam em espacadores de 25 mm) e sobe na outra ponta. Enforca-gatos com base adesiva a cada ~7 cm.
  const mats = {}; const mat = (c) => (mats[c] ||= new THREE.MeshStandardMaterial({ color: c, roughness: 0.55 }));
  const branco = new THREE.MeshStandardMaterial({ color: 0xf1f1ec, roughness: 0.45 });
  const PL = Object.fromEntries(M.placas.map((p) => [p.key, p]));
  const YH = ZP + ALT_HOUS, YA = ZP + ALT_HOUS + 7, YC = ZB + 2.2;
  function borda(p, x, y) {                     // ponto 7 mm fora da borda mais proxima
    const c = [[x - p.x, -1, 0], [p.x + p.w - x, 1, 0], [y - p.y, 0, -1], [p.y + p.h - y, 0, 1]].sort((u, v) => u[0] - v[0])[0];
    return c[1] ? [c[1] < 0 ? p.x - 7 : p.x + p.w + 7, y, c[1], 0] : [x, c[2] < 0 ? p.y - 7 : p.y + p.h + 7, 0, c[2]];
  }
  M.cabos.forEach((cb, ic) => {
    const pa = PL[cb.de[0]], pb = PL[cb.para[0]];
    const ca = [(cb.a[0][0] + cb.a[3][0]) / 2, (cb.a[0][1] + cb.a[3][1]) / 2], cbb = [(cb.b[0][0] + cb.b[3][0]) / 2, (cb.b[0][1] + cb.b[3][1]) / 2];
    const ea = borda(pa, ...ca), eb = borda(pb, ...cbb);
    const faixa = ((ic % 7) - 3) * 3.2;         // cada cabo numa "pista" para nao ficarem todos sobrepostos
    // conectores femea
    for (const pts of [cb.a, cb.b]) {
      const [x1, y1] = pts[0], [x2, y2] = pts[3], L = Math.hypot(x2 - x1, y2 - y1) + 2.6;
      const h = new THREE.Mesh(new THREE.BoxGeometry(mm(L), mm(14), mm(2.6)), preto);
      h.position.set(mm((x1 + x2) / 2), mm(ZP + 1.6 + 2.5 + 7), mm((y1 + y2) / 2)); h.rotation.y = -Math.atan2(y2 - y1, x2 - x1); h.castShadow = true; cabosG.add(h);
    }
    // trajeto do centro do cabo na base (em L), com a pista
    const A = [ea[0] + (ea[3] ? faixa : 0), ea[1] + (ea[2] ? faixa : 0)], B = [eb[0] + (eb[3] ? faixa : 0), eb[1] + (eb[2] ? faixa : 0)];
    const meio = Math.abs(A[0] - B[0]) > Math.abs(A[1] - B[1]) ? [B[0], A[1]] : [A[0], B[1]];
    const trilho = [A, meio, B];
    for (let i = 0; i < 4; i++) {
      const off = (i - 1.5) * 1.35;               // fios lado a lado (cabo chato)
      const per = (u, v) => { const dx = v[0] - u[0], dy = v[1] - u[1], L = Math.hypot(dx, dy) || 1; return [-dy / L * off, dx / L * off]; };
      const o1 = per(trilho[0], trilho[1]), o2 = per(trilho[1], trilho[2]);
      const P = (x, y, z) => new THREE.Vector3(mm(x), mm(z), mm(y));
      const [xa, ya] = cb.a[i], [xb, yb] = cb.b[i];
      const pts = [P(xa, ya, YH), P(xa, ya, YA), P(A[0] + o1[0], A[1] + o1[1], YA), P(A[0] + o1[0], A[1] + o1[1], YC + 6),
        P(A[0] + o1[0], A[1] + o1[1], YC), P(meio[0] + o1[0] + o2[0], meio[1] + o1[1] + o2[1], YC),
        P(B[0] + o2[0], B[1] + o2[1], YC), P(B[0] + o2[0], B[1] + o2[1], YC + 6), P(B[0] + o2[0], B[1] + o2[1], YA), P(xb, yb, YA), P(xb, yb, YH)];
      const limpo = pts.filter((p, k) => k === 0 || p.distanceTo(pts[k - 1]) > 1e-4);
      const curva = new THREE.CatmullRomCurve3(limpo, false, 'catmullrom', 0.08);
      const tubo = new THREE.Mesh(new THREE.TubeGeometry(curva, Math.max(60, limpo.length * 14), mm(0.62), 6, false), mat((cb.energia ? CORES_PWR : CORES_FITA)[i]));
      tubo.castShadow = true; cabosG.add(tubo);
    }
    // enforca-gatos nos trechos da base
    for (const [u, v] of [[A, meio], [meio, B]]) {
      const L = Math.hypot(v[0] - u[0], v[1] - u[1]); if (L < 40) continue;
      const ang = Math.atan2(v[1] - u[1], v[0] - u[0]);
      for (let d = 30; d < L - 20; d += 70) {
        const x = u[0] + (v[0] - u[0]) * d / L, y = u[1] + (v[1] - u[1]) * d / L;
        const base = new THREE.Mesh(new THREE.BoxGeometry(mm(10), mm(1.6), mm(10)), branco); base.position.set(mm(x), mm(ZB + 0.8), mm(y)); base.rotation.y = -ang; cabosG.add(base);
        const fita = new THREE.Mesh(new THREE.BoxGeometry(mm(2.4), mm(3.6), mm(7.4)), branco); fita.position.set(mm(x), mm(YC + 0.2), mm(y)); fita.rotation.y = -ang; cabosG.add(fita);
        const cab = new THREE.Mesh(new THREE.BoxGeometry(mm(3), mm(3), mm(3)), branco); cab.position.set(mm(x), mm(YC + 1.2), mm(y + 0)); cab.rotation.y = -ang; cab.translateZ(mm(4.6)); cabosG.add(cab);
      }
    }
  });
  // cabo da fonte ate o jack do backplane
  const bp = PL.BACKPLANE, j = bp.conectores.JACK[0];
  const fonte = new THREE.CatmullRomCurve3([new THREE.Vector3(mm(bp.x + j[0] - 40), mm(ZB + 2), mm(-12)),
    new THREE.Vector3(mm(bp.x + j[0] - 40), mm(ZB + 2.5), mm(bp.y - 4)), new THREE.Vector3(mm(bp.x + j[0] - 40), mm(ZP + 8), mm(bp.y + j[1])),
    new THREE.Vector3(mm(bp.x + j[0] - 9), mm(ZP + 8), mm(bp.y + j[1]))], false, 'catmullrom', 0.2);
  cabosG.add(new THREE.Mesh(new THREE.TubeGeometry(fonte, 50, mm(1.8), 10, false), new THREE.MeshStandardMaterial({ color: 0x151515, roughness: 0.6 })));
}

// ---------- simulacao (mesmo microcodigo das EEPROMs) ----------
const S = { ram: [], pc: 0, mar: 0, ir: 0, a: 0, b: 0, out: 0, passo: 0, clk: 0, ciclo: 0, parado: false };
const ATIVOBAIXO = { IRI: 1, RMO: 1, MAI: 1, PCO: 1, JMP: 1, IRO: 1, ACO: 1, ACI: 1, ALU: 1, BRI: 1, ORI: 1 };
const REDE = { '~{ALUO}': 'ALU' };
let prog = Object.keys(M.programas)[0];
function reset() { Object.assign(S, { ram: M.programas[prog].slice(), pc: 0, mar: 0, ir: 0, a: 0, b: 0, out: 0, passo: 0, clk: 0, ciclo: 0, parado: false }); }
function sinais() {
  const op = S.ir >> 4, st = S.passo < 2 ? M.busca[S.passo] : (M.instrucoes[op].passos[S.passo - 2] || []);
  return new Set(st);
}
function ula(s) {
  const sel = (s.has('AL1') ? 2 : 0) | (s.has('AL0') ? 1 : 0);
  if (sel === 0) { const sub = s.has('SUB') ? 1 : 0; return (S.a + ((S.b ^ (sub ? 255 : 0)) & 255) + sub) & 255; }
  if (sel === 1) return S.a & S.b; if (sel === 2) return S.a | S.b; return S.a ^ (S.b | (s.has('NOT') ? 255 : 0));
}
function barramento(s) {
  if (s.has('PCO')) return S.pc; if (s.has('RMO')) return S.ram[S.mar]; if (s.has('IRO')) return S.ir & 15;
  if (s.has('ACO')) return S.a; if (s.has('ALU')) return ula(s); return null;
}
function meioCiclo() {
  if (S.parado) return;
  const s = sinais();
  if (S.clk === 0) {                         // borda de subida: registradores carregam
    if (s.has('HLT')) { S.parado = true; return; }
    const bus = barramento(s) ?? 0;
    const n = { mar: S.mar, ir: S.ir, a: S.a, b: S.b, pc: S.pc };
    if (s.has('MAI')) n.mar = bus & 15; if (s.has('RMI')) S.ram[S.mar] = bus; if (s.has('IRI')) n.ir = bus;
    if (s.has('ACI')) n.a = bus; if (s.has('BRI')) n.b = bus; if (s.has('ORI')) S.out = bus;
    if (s.has('JMP')) n.pc = bus & 15; else if (s.has('PCI')) n.pc = (S.pc + 1) & 15;
    Object.assign(S, n); S.clk = 1;
  } else {                                   // borda de descida: proximo passo
    S.clk = 0; S.passo = (S.passo + 1) % 5; S.ciclo++;
  }
}
function valor(placa, rede, s, bus) {
  const bit = (v, i) => (v >> i) & 1, nm = rede.replace(/^~\{|\}$/g, '');
  if (rede === '+5V') return 1;
  let m;
  if ((m = /^~\{S(\d)\}$/.exec(rede))) return S.passo === +m[1] ? 0 : 1;
  if ((m = /^T(\d)$/.exec(rede))) return bit(S.passo, +m[1]);
  if ((m = /^D(\d)$/.exec(rede))) return bus == null ? 0 : bit(bus, +m[1]);
  if ((m = /^A(\d)$/.exec(rede))) return bit(S.a, +m[1]);
  if ((m = /^B(\d)$/.exec(rede))) return bit(S.b, +m[1]);
  if ((m = /^I(\d)$/.exec(rede))) return bit(S.ir, +m[1]);
  if ((m = /^O(\d)$/.exec(rede))) return bit(S.out, +m[1]);
  if ((m = /^P(\d)$/.exec(rede))) return bit(S.pc, +m[1]);
  if ((m = /^R(\d)$/.exec(rede))) return bit(ula(s), +m[1]);
  if ((m = /^Q(\d)$/.exec(rede))) return bit(S.ram[S.mar], +m[1]);
  if ((m = /^RA(\d)$/.exec(rede))) return bit(S.mar, +m[1]);
  if (rede === 'CLK') return S.clk;
  if (rede === '~{RST}') return 1;
  if (rede === '~{SW_PROG}') return 1;        // modo RUN
  if (rede === '~{SW_RUN}') return 0;
  const sig = REDE[rede] || nm;               // sinais de controle
  const ativo = s.has(sig);
  return rede.startsWith('~{') ? (ativo ? 0 : 1) : (ativo ? 1 : 0);
}
const SEG = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B];
function desenhaDisplay() {
  if (!display) return;
  const { c, t } = display, g = c.getContext('2d'), W = c.width, H = c.height, dw = W / 4;
  g.clearRect(0, 0, W, H);
  const txt = String(S.out).padStart(4, ' ');
  g.strokeStyle = '#ff2a1a'; g.lineCap = 'round'; g.shadowColor = '#ff3b20'; g.shadowBlur = 14;
  for (let k = 0; k < 4; k++) {
    const ch = txt[k]; if (ch === ' ') continue;
    const code = SEG[+ch], cx = dw * k + dw * 0.45, a = dw * 0.26, b = H * 0.30, cy = H / 2;
    g.lineWidth = Math.max(4, dw * 0.07);
    const seg = { a: [-a, -b, a, -b], b: [a, -b, a, 0], c: [a, 0, a, b], d: [-a, b, a, b], e: [-a, 0, -a, b], f: [-a, -b, -a, 0], g: [-a, 0, a, 0] };
    const bits = { a: 6, b: 5, c: 4, d: 3, e: 2, f: 1, g: 0 };
    for (const [n, [xa, ya, xb, yb]] of Object.entries(seg)) if (code >> bits[n] & 1) { g.beginPath(); g.moveTo(cx + xa, cy + ya); g.lineTo(cx + xb, cy + yb); g.stroke(); }
  }
  t.needsUpdate = true;
}
function atualiza() {
  const s = sinais(), bus = barramento(s);
  for (const v of ledsVis) {
    const on = !S.parado || v.led.sinal !== 'CLK' ? valor(v.placa, v.led.sinal, s, bus) === v.led.nivel : false;
    v.esf.material.color.copy(v.cor).multiplyScalar(on ? 1.6 : 0.22);
    v.sp.material.opacity = on ? 0.95 : 0;
  }
  desenhaDisplay();
  const op = S.ir >> 4, mn = M.instrucoes[op].mn, h2 = (v) => v.toString(2).padStart(8, '0');
  $('cpu').innerHTML = `<div><span class="l">instr.</span><span class="instr">${S.ciclo < 2 && S.ir === 0 ? '—' : mn + (op && ![0, 9, 13, 14, 15].includes(op) ? ' ' + (S.ir & 15) : '')}</span>  T${S.passo}${S.parado ? '  (HLT)' : ''}</div>`
    + `<div><span class="l">PC</span>${S.pc}   <span class="l" style="width:auto">MAR</span> ${S.mar}</div>`
    + `<div><span class="l">A</span>${h2(S.a)} = ${S.a}</div><div><span class="l">B</span>${h2(S.b)} = ${S.b}</div>`
    + `<div><span class="l">bus</span>${bus == null ? '— (livre)' : h2(bus)}</div><div><span class="l">saída</span>${S.out}</div>`
    + `<div class="sinais"><span class="l">sinais</span>${[...s].join(' ') || '—'}</div>`;
}

// ---------- controles ----------
let rodando = true, hz = 8, acum = 0;
$('s-prog').innerHTML = Object.keys(M.programas).map((n) => `<option>${n}</option>`).join('');
$('s-prog').addEventListener('change', (e) => { prog = e.target.value; reset(); atualiza(); });
$('s-vel').addEventListener('change', (e) => { hz = +e.target.value; });
$('b-run').addEventListener('click', () => { rodando = !rodando; $('b-run').setAttribute('aria-pressed', String(rodando)); $('b-run').textContent = rodando ? '⏸ Pausar' : '▶ Rodar'; });
$('b-passo').addEventListener('click', () => { meioCiclo(); meioCiclo(); atualiza(); });
$('b-reset').addEventListener('click', () => { reset(); atualiza(); });
$('c-tampa').addEventListener('change', (e) => { tampaG.visible = e.target.checked; });
$('c-cabos').addEventListener('change', (e) => { cabosG.visible = e.target.checked; });
let cima = false; $('b-vista').addEventListener('click', () => { cima = !cima; vista(cima); $('b-vista').textContent = cima ? 'Vista 3D' : 'Vista de cima'; });
window.__vista = vista; window.__tampa = (v) => { tampaG.visible = v; };
window.__rodar = (n) => { for (let i = 0; i < n; i++) meioCiclo(); atualiza(); };

(async () => {
  reset(); cabos();
  let n = 0;
  await Promise.all(M.placas.map(async (p) => {
    try { montaPlaca(p, await carregaGLB(p.id)); } catch (e) { console.error(e); }
    $('estado').textContent = `carregando as placas… ${++n}/${M.placas.length}`;
  }));
  $('estado').hidden = true; atualiza(); window.__pronto = true;
  if (LEVE) { setInterval(() => { if (rodando && !RENDER) { meioCiclo(); atualiza(); } window.__frame(); }, 400); window.__frame(); }
})();
let t0 = performance.now();
window.__frame = () => { ctl.update(); renderer.render(cena, cam); };
if (!LEVE) renderer.setAnimationLoop((t) => {
  const dt = (t - t0) / 1000; t0 = t;
  if (rodando && !RENDER && window.__pronto) {
    acum += dt * hz * 2; let k = 0;
    while (acum >= 1 && k++ < 50) { acum -= 1; meioCiclo(); if (S.parado && S.ciclo > 0) { /* reinicia sozinho depois de 3 s */ } }
    if (k) atualiza();
    if (S.parado) { S._p = (S._p || 0) + dt; if (S._p > 3) { S._p = 0; reset(); } }
  }
  ctl.update(); renderer.render(cena, cam);
});
</script>
'''


def gerar(base='modelos/', b64=False):
    dados = json.load(open(os.path.join(RAIZ, 'docs', '3d', 'montagem.json')))
    d = json.dumps(dados, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return CORPO.replace('__DADOS__', d).replace('__BASE__', base).replace('__B64__', 'true' if b64 else 'false')


def main():
    if '--corpo' in sys.argv:
        saida = sys.argv[sys.argv.index('--corpo') + 1]
        open(saida, 'w').write(CABECA + ESTILO + gerar(b64=True))
        print('corpo ->', saida)
        return
    saida = os.path.join(RAIZ, 'docs', '3d', 'montagem.html')
    open(saida, 'w').write('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
                           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                           + CABECA + ESTILO + '</head>\n<body>\n' + gerar() + '</body>\n</html>\n')
    print('montagem ->', saida)


if __name__ == '__main__':
    main()
