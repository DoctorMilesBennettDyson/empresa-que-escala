# -*- coding: utf-8 -*-
"""Láminas PNG 1080×1350 (4:5) del libro, una por figura, para WhatsApp e Instagram (TAR-0186).

Cada lámina es la diagramación vertical (F-xx_vertical.svg, 600 de ancho), que ya trae título,
conclusión, condición y crédito, centrada sobre el fondo de la figura. Si la vertical es más alta
que 4:5, se achica para entrar por alto y quedan márgenes a los costados.
Uso:  C:\\Python38\\python.exe _generar_laminas.py [nombre ...]
Salida: ..\\laminas\\L-NN_nombre.png, con NN = número de la figura en el libro (orden de FIGURAS).
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import _generar_figuras as g

ANCHO, ALTO = 1080, 1350
SALIDA = g.AQUI.parent / "laminas"
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def edge():
    return next(p for p in EDGE if Path(p).exists())


def lamina(nombre, numero):
    svg = (g.AQUI / f"{nombre}_vertical.svg").read_text(encoding="utf-8")
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).group(1, 2))
    s = min(ANCHO / w, ALTO / h)
    svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{w * s:.0f}" height="{h * s:.0f}"', svg, count=1)
    pagina = (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;width:{ANCHO}px;'
              f'height:{ALTO}px;background:{g.FONDO};overflow:hidden}}body{{display:flex;'
              f'align-items:center;justify-content:center}}</style>{svg}')
    with tempfile.TemporaryDirectory(prefix="laminas_") as tmp:
        html = Path(tmp) / "l.html"
        html.write_text(pagina, encoding="utf-8")
        destino = SALIDA / f"L-{numero:02d}_{nombre}.png"
        # ruta absoluta: Edge no resuelve --screenshot relativo al cwd y no avisa
        subprocess.run([edge(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        "--user-data-dir=" + str(Path(tmp) / "perfil"), "--virtual-time-budget=2000",
                        f"--window-size={ANCHO},{ALTO}", "--screenshot=" + str(destino.resolve()),
                        html.as_uri()], capture_output=True, timeout=90)
    return destino, s


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    pedidas = sys.argv[1:] or list(g.FIGURAS)
    for n, nombre in enumerate(g.FIGURAS, 1):
        if nombre in pedidas:
            destino, s = lamina(nombre, n)
            # s < 1,8: la vertical entró por alto; la letra de 11 px queda en 11·s px
            print(f"{destino.name}  {'OK' if destino.exists() else 'FALTA'}  escala {s:.2f}")
