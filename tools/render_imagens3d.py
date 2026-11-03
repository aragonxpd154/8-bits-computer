#!/usr/bin/env python3
"""Tira as imagens 3D (PNG transparente) de cada placa a partir do visualizador.

Gera docs/imagens/3d/<placa>.png (vista 3D com componentes) e <placa>-nua.png (so a placa).
Requer: pip install playwright && python3 -m playwright install chromium
Se nao houver internet para o three.js, aponte THREE_DIR para uma pasta node_modules/three local.

Projeto: Marcos Silva dos Santos (MarcosObel) - GPL-3.0
"""
import os
import sys
import json
import time
import subprocess

from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D3 = os.path.join(RAIZ, 'docs', '3d')
SAIDA = os.path.join(RAIZ, 'docs', 'imagens', '3d')
THREE_DIR = os.environ.get('THREE_DIR')


def main():
    os.makedirs(SAIDA, exist_ok=True)
    placas = sys.argv[1:] or sorted(json.load(open(os.path.join(D3, 'placas3d.json'))))
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8766', '-d', D3],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
                                          '--ignore-gpu-blocklist'])
            pg = nav.new_page(viewport={'width': 1400, 'height': 900}, device_scale_factor=1)
            if THREE_DIR:
                def cdn(route):
                    rel = route.request.url.split('three@0.160.0/')[1]
                    route.fulfill(path=os.path.join(THREE_DIR, rel), content_type='application/javascript')
                pg.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', cdn)
            pg.route('https://fonts.googleapis.com/**', lambda r: r.abort())
            for nome in placas:
                pg.goto(f'http://localhost:8766/visualizador.html?render#{nome}')
                pg.wait_for_function(f'window.__pronto === "{nome}"', timeout=120000)
                pg.wait_for_timeout(800)
                pg.screenshot(path=os.path.join(SAIDA, nome + '.png'), omit_background=True)
                pg.evaluate('window.__componentes(false)')
                pg.wait_for_timeout(400)
                pg.screenshot(path=os.path.join(SAIDA, nome + '-nua.png'), omit_background=True)
                pg.evaluate('window.__componentes(true)')
                print(nome, flush=True)
            nav.close()
    finally:
        srv.terminate()
    # recorta as bordas transparentes
    from PIL import Image
    for f in os.listdir(SAIDA):
        if f.endswith('.png'):
            im = Image.open(os.path.join(SAIDA, f))
            bb = im.getchannel('A').getbbox()
            if bb:
                im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height))) \
                  .save(os.path.join(SAIDA, f), optimize=True)


if __name__ == '__main__':
    main()
