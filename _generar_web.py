# -*- coding: utf-8 -*-
"""Página web del libro v2.0 en un solo HTML, con las figuras adentro (TAR-0186).

pandoc arma el HTML del Manual; después cada <img src="figuras/F-xx.svg"> se cambia por un
<picture> con las dos diagramaciones en base64: la apaisada por defecto y la vertical en pantallas
de menos de 720 px. En base64 y no inline, porque los 86 SVG repiten los mismos id (marcadores,
tramas) y adentro de una misma página chocarían.
Uso (desde esta carpeta):  C:\\Python38\\python.exe _generar_web.py
"""
import base64
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).parent
SALIDA = AQUI / "Como_se_construye_una_empresa_que_escala_v2.0.html"
CORTE = 720   # px: debajo, la vertical (la apaisada quedaría con letra de menos de 9 px)


def datos(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.read_bytes()).decode("ascii")


def figura(m):
    nombre = m.group(1)
    ap, ve = AQUI / "figuras" / f"{nombre}.svg", AQUI / "figuras" / f"{nombre}_vertical.svg"
    return (f'<picture><source media="(max-width: {CORTE}px)" srcset="{datos(ve)}">'
            f'<img src="{datos(ap)}"{m.group(2)}></picture>')


def main():
    html = subprocess.run(
        ["pandoc", "MANUAL_EMPRESAS_QUE_ESCALAN.md", "-f", "markdown-tex_math_dollars-tex_math_single_backslash",
         "-t", "html5", "-s", "--section-divs", "--toc", "--toc-depth=2", "-H", "_estilo_web.html",
         "--metadata", "pagetitle=Cómo se construye una empresa que escala", "--metadata", "lang=es"],
        cwd=AQUI, capture_output=True, check=True).stdout.decode("utf-8")
    html, n = re.subn(r'<img src="figuras/([^"/]+)\.svg"([^>]*?)\s*/?>', figura, html)
    assert n == html.count("<picture><source") and "figuras/" not in html, "quedó una figura sin embeber"
    SALIDA.write_text(html, encoding="utf-8")
    print(f"{SALIDA.name}: {n} figuras, {SALIDA.stat().st_size:,} bytes".replace(",", "."))


if __name__ == "__main__":
    main()
