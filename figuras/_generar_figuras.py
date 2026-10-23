# -*- coding: utf-8 -*-
"""Genera las figuras SVG del libro «Cómo se construye una empresa que escala» (v2.0).

Cada figura es una función fig_x(diagramacion) que devuelve el SVG como texto; los datos
se calculan acá, no se dibujan a mano. Dos diagramaciones por figura:
    "apaisada"  -> 900 de ancho (PDF A4, web de escritorio)   ->  F-xx.svg
    "vertical"  -> 600 de ancho (PDF A5, láminas, celular)    ->  F-xx_vertical.svg
Uso:  C:\\Python38\\python.exe _generar_figuras.py
El número de cada figura en el libro sale del orden de FIGURAS (= orden de aparición en el Manual).
"""
import math
from pathlib import Path

AQUI = Path(__file__).parent

# Paleta (validada: dataviz, slots 1-2 sobre superficie clara). Además del color, cada
# serie lleva un trazo distinto (lleno / rayado / punteado / hueco) para la fotocopia B/N.
FONDO = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
TINTA3 = "#8a8984"
GRILLA = "#e6e5e0"
AZUL = "#2a78d6"      # la serie (lo que es)
AZUL_SUAVE = "#cde2fb"
NARANJA = "#eb6834"   # la lectura equivocada, el riesgo
NARANJA_SUAVE = "#fbd9ca"
GRIS = "#b4b3ad"
GRIS_SUAVE = "#ecebe6"
FUENTE = "Segoe UI, Helvetica Neue, Arial, sans-serif"
CREDITO = ("© Pablo Luciano Rainieri Blasco · CC BY 4.0 · "
           "Fuente: Cómo se construye una empresa que escala")

DEFS = (
    '<defs>'
    f'<marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{TINTA}"/></marker>'
    f'<marker id="fl_az" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{AZUL}"/></marker>'
    f'<marker id="fl_na" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{NARANJA}"/></marker>'
    f'<pattern id="rayas" width="7" height="7" patternUnits="userSpaceOnUse" '
    f'patternTransform="rotate(45)"><rect width="7" height="7" fill="{NARANJA_SUAVE}"/>'
    f'<line x1="0" y1="0" x2="0" y2="7" stroke="{NARANJA}" stroke-width="3"/></pattern>'
    f'<pattern id="rayas_gris" width="6" height="6" patternUnits="userSpaceOnUse" '
    f'patternTransform="rotate(45)"><rect width="6" height="6" fill="{GRIS_SUAVE}"/>'
    f'<line x1="0" y1="0" x2="0" y2="6" stroke="{GRIS}" stroke-width="2.5"/></pattern>'
    '</defs>')

SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def pot(k):
    """3 -> '10³'."""
    return "10" + str(k).translate(SUP)


def miles(n):
    """1024 -> '1.024' (separador de miles castellano)."""
    return f"{n:,}".replace(",", ".")


def coma(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def texto(x, y, s, tam=12, color=TINTA, peso=400, anc="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{tam}" fill="{color}" '
            f'font-weight="{peso}" text-anchor="{anc}" {extra}>{esc(s)}</text>')


def ancho_txt(s, tam, peso=400):
    """Ancho aproximado en px (Segoe UI; algo holgado para no chocar)."""
    return len(s) * tam * (0.54 if peso >= 600 else 0.50)


def envolver(s, tam, ancho, peso=400):
    lineas, act = [], ""
    s = s.replace(" %", " %")   # «10 %» no se corta
    for p in s.split(" "):
        prueba = (act + " " + p).strip()
        if not act or ancho_txt(prueba, tam, peso) <= ancho:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    return lineas


def bloque(o, x, y, w, s, tam, color=TINTA, peso=400, interl=1.35, anc="start"):
    """Párrafo envuelto; y = borde superior. Devuelve el borde inferior."""
    xa = {"start": x, "middle": x + w / 2, "end": x + w}[anc]
    for l in envolver(s, tam, w, peso):
        o.append(texto(xa, y + tam, l, tam, color, peso, anc))
        y += tam * interl
    return y


def alto(s, tam, w, peso=400, interl=1.35):
    return len(envolver(s, tam, w, peso)) * tam * interl


def linea(o, x1, y1, x2, y2, color=TINTA3, ancho=1.0, dash=None, flecha=None, inicio=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{flecha})"' if flecha else ""
    if flecha and inicio:
        m += f' marker-start="url(#{flecha})"'
    o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
             f'stroke="{color}" stroke-width="{ancho}"{d}{m}/>')


def caja_txt(x, y, s, tam, peso=400, anc="start"):
    """Caja aproximada de un texto: (x0, x1, y0, y1); y es la línea de base."""
    w = ancho_txt(s, tam, peso)
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anc]
    return x0, x0 + w, y - tam * 0.8, y + tam * 0.25


def vgrilla(o, x, ya, yb, cajas, color=GRILLA):
    """Línea vertical de grilla de ya a yb, cortada donde pasaría por un rótulo."""
    y = ya
    for y0, y1 in sorted((c[2] - 2, c[3] + 2) for c in cajas if c[0] - 3 <= x <= c[1] + 3):
        if y0 > y:
            linea(o, x, y, x, min(y0, yb), color)
        y = max(y, y1)
    if y < yb:
        linea(o, x, y, x, yb, color)


def caja(o, x, y, w, h, fill, stroke="none", sw=1.0, dash=None, rx=6):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0.8):.1f}" height="{h:.1f}" rx="{rx}" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def barra(x, y, w, h, trazo):
    """Rectángulo con trazo distinguible en blanco y negro."""
    base = f'x="{x:.1f}" y="{y:.1f}" width="{max(w, 1):.1f}" height="{h:.1f}"'
    if trazo == "lleno":
        return f'<rect {base} fill="{NARANJA}"/>'
    if trazo == "lleno_azul":
        return f'<rect {base} fill="{AZUL}"/>'
    if trazo == "rayado":
        return f'<rect {base} fill="url(#rayas)" stroke="{NARANJA}" stroke-width="1.5"/>'
    if trazo == "punteado":
        return (f'<rect {base} fill="{AZUL_SUAVE}" stroke="{AZUL}" stroke-width="2" '
                f'stroke-dasharray="5 4"/>')
    if trazo == "suave":
        return f'<rect {base} fill="{AZUL_SUAVE}" stroke="{AZUL}" stroke-width="1.5"/>'
    if trazo == "hueco":
        return f'<rect {base} fill="{FONDO}" stroke="{AZUL}" stroke-width="2.25"/>'
    if trazo == "gris":
        return f'<rect {base} fill="url(#rayas_gris)" stroke="{TINTA3}" stroke-width="1.2"/>'
    raise ValueError(trazo)


class Lienzo:
    """Pila vertical: título-pregunta, cuerpo, conclusión, condición honesta y crédito."""

    def __init__(self, diagramacion):
        if diagramacion not in ("apaisada", "vertical"):
            raise ValueError(diagramacion)
        self.ap = diagramacion == "apaisada"
        self.W = 900 if self.ap else 600
        self.M = 40
        self.A = self.W - 2 * self.M
        self.o = []
        self.y = 0.0

    def par(self, s, tam, color=TINTA, peso=400, interl=1.38):
        self.y = bloque(self.o, self.M, self.y, self.A, s, tam, color, peso, interl)

    def cabeza(self, pregunta, sub):
        self.y = 16
        self.par(pregunta, 21, TINTA, 700, 1.3)
        self.y += 2
        self.par(sub, 13.5, TINTA2)
        self.y += 22

    def pie(self, conclusion, detalle="", condicion=""):
        self.y += 18
        linea(self.o, self.M, self.y, self.W - self.M, self.y, GRILLA)
        self.y += 12
        self.par(conclusion, 15, TINTA, 700, 1.35)
        if detalle:
            self.y += 3
            self.par(detalle, 12.5, TINTA2)
        if condicion:
            self.y += 8
            self.par(condicion, 11, TINTA3, 400, 1.42)
        self.y += 6
        # una sola línea a 11 px: a 10,5 px quedaba en 6,3 pt impresa en A5 (mínimo 6,5)
        self.o.append(texto(self.M, self.y + 11, CREDITO, 11, TINTA3))
        self.y += 11 * 1.38 + 14

    def svg(self, titulo, desc):
        H = int(math.ceil(self.y))
        cab = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {H}" '
               f'width="{self.W}" height="{H}" font-family="{FUENTE}" role="img" '
               f'aria-labelledby="t d">',
               f'<title id="t">{esc(titulo)}</title>', f'<desc id="d">{esc(desc)}</desc>',
               DEFS, f'<rect width="{self.W}" height="{H}" fill="{FONDO}"/>']
        return "\n".join(cab + self.o + ['</svg>'])


def barras_h(o, x0, y0, A, filas, lo, hi, marcas, rot_w, etq_marca=miles,
             alto_b=28, sep=22, margen_valor=120):
    """Barras horizontales en escala logarítmica. filas: dicts rot, sub, v, trazo, etq.
    rot_w = 0 pone el rótulo arriba de la barra (diagramación vertical). Devuelve el alto."""
    bx0, bx1 = x0 + rot_w, x0 + A - margen_valor
    l0, l1 = math.log10(lo), math.log10(hi)
    X = lambda v: bx0 + (math.log10(v) - l0) / (l1 - l0) * (bx1 - bx0)
    y, ys = y0, []
    for f in filas:
        if rot_w == 0:
            o.append(texto(x0, y + 13, f["rot"], 13, TINTA, 700))
            y += 18
            if f.get("sub"):
                o.append(texto(x0, y + 12, f["sub"], 11.5, TINTA2))
                y += 17
            y += 4
        ys.append(y)
        y += alto_b + sep
    bot = y - sep
    for f, yb in zip(filas, ys):
        e0, e1 = X(f["v"]) + 2, X(f["v"]) + 8 + ancho_txt(f["etq"], 13, 700) + 4   # el rótulo del valor
        for v in marcas:
            if not e0 <= X(v) <= e1:
                linea(o, X(v), yb - 4, X(v), yb + alto_b + 4, GRILLA)
        if rot_w:
            o.append(texto(bx0 - 10, yb + 13, f["rot"], 12.5, TINTA, 600, anc="end"))
            if f.get("sub"):
                o.append(texto(bx0 - 10, yb + 28, f["sub"], 11, TINTA2, anc="end"))
        o.append(barra(bx0, yb, X(f["v"]) - bx0, alto_b, f["trazo"]))
        o.append(texto(X(f["v"]) + 8, yb + alto_b / 2 + 5, f["etq"], 13, TINTA, 700))
        linea(o, bx0, yb - 6, bx0, yb + alto_b + 6, TINTA3)
    for v in marcas:
        o.append(texto(X(v), bot + 20, etq_marca(v), 11, TINTA3, anc="middle"))
    return bot + 26 - y0


# ---------------------------------------------------------------------------
# Fig. 1 · F-00 · Los cinco niveles (El mapa)
# ---------------------------------------------------------------------------
NIVELES = [
    ("1", "Repetir", "¿La cosa se repite, o cada vez se empieza de cero?",
     "la unidad que se repite"),
    ("2", "Margen", "Cada vez que pasa una unidad, ¿entra más de lo que sale?",
     "el margen de cada unidad"),
    ("3", "Curva de aprendizaje", "¿Cuánto baja el costo cada vez que se duplica la producción?",
     "la tasa y las duplicaciones que faltan"),
    ("4", "El lazo", "¿El sistema se sostiene solo, o hay que empujarlo para siempre?",
     "la ganancia del lazo"),
    ("5", "Capital y ruina", "¿Alcanza el dinero para llegar hasta donde el negocio se sostiene solo?",
     "la profundidad y el ancho del pozo"),
]


def _estilo_nivel(k):
    return (AZUL_SUAVE, AZUL, None) if k < 2 else (FONDO, AZUL, "6 4")


def fig_cinco_niveles(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Esto puede crecer? La misma pregunta, cinco veces",
             "Cada nivel responde una pregunta y entrega lo que el siguiente necesita.")
    x0, y0, A = L.M, L.y, L.A
    if L.ap:
        gap, esc_y, h0 = 18, 28, 205
        w = (A - 4 * gap) / 5
        base = y0 + 4 * esc_y + h0
        for k, (n, nombre, preg, da) in enumerate(NIVELES):
            x, top = x0 + k * (w + gap), y0 + (4 - k) * esc_y
            fill, st, dash = _estilo_nivel(k)
            caja(o, x, top, w, base - top, fill, st, 1.6, dash)
            o.append(texto(x + 12, top + 22, f"Nivel {n}", 12, AZUL, 700))
            y = bloque(o, x + 12, top + 28, w - 24, nombre, 15, TINTA, 700, 1.22)
            bloque(o, x + 12, y + 4, w - 24, preg, 12, TINTA2, 400, 1.35)
            o.append(texto(x + 12, base - 66, "Da:", 11.5, TINTA3, 700))
            bloque(o, x + 12, base - 62, w - 24, da, 12.5, TINTA, 600, 1.3)
            if k < 4:
                linea(o, x + w + 2, base - 30, x + w + gap - 2, base - 30, TINTA, 1.5, flecha="fl")
        yb = base + 14
        xa1 = x0 + 2 * w + gap
        linea(o, x0, yb, xa1, yb, AZUL, 2)
        linea(o, xa1 + gap, yb, x0 + A, yb, AZUL, 2, "6 4")
        o.append(texto(x0, yb + 22, "Se ven: un dibujo alcanza", 13, TINTA, 700))
        o.append(texto(xa1 + gap, yb + 22, "Necesitan lápiz: sólo texto y cuenta propia", 13, TINTA, 700))
        L.y = yb + 30
    else:
        sang, gap = 14, 24
        y = y0
        for k, (n, nombre, preg, da) in enumerate(NIVELES):
            if k in (0, 2):
                rot = "Se ven: un dibujo alcanza" if k == 0 else "Necesitan lápiz: sólo texto y cuenta propia"
                o.append(texto(x0, y + 13, rot, 13, TINTA, 700))
                y += 24
            x = x0 + k * sang
            w = A - 4 * sang
            hi = 16 + 20 + alto(preg, 12.5, w - 24) + 8 + alto("Da: " + da, 12.5, w - 24, 600) + 10
            fill, st, dash = _estilo_nivel(k)
            caja(o, x, y, w, hi, fill, st, 1.6, dash)
            o.append(texto(x + 12, y + 24, f"Nivel {n} · {nombre}", 15, TINTA, 700))
            yy = bloque(o, x + 12, y + 32, w - 24, preg, 12.5, TINTA2)
            bloque(o, x + 12, yy + 4, w - 24, "Da: " + da, 12.5, TINTA, 600)
            y += hi
            if k < 4:
                linea(o, x + 30, y + 2, x + 30 + sang, y + gap - 2, TINTA, 1.5, flecha="fl")
                y += gap
        L.y = y
    L.pie("Los niveles 1 y 2 se entienden con un dibujo; del 3 al 5 hace falta lápiz, "
          "y por eso casi no circulan.",
          "Las cinco respuestas forman un motor: el activo que deja cada etapa es el piso "
          "de la misión siguiente.",
          "[hipótesis] Que los niveles 3 a 5 se transmitan peor es la hipótesis central de este "
          "libro; nadie la midió todavía.")
    return L.svg("Los cinco niveles",
                 "Cinco preguntas en escalera: repetir, margen, curva de aprendizaje, lazo y capital. "
                 "Los niveles 1 y 2 se ven en un dibujo; del 3 al 5 hace falta lápiz.")


# ---------------------------------------------------------------------------
# Fig. 2 · F-13 · De Marte al acero (§2.5)
# ---------------------------------------------------------------------------
ESLABONES = [
    ("Misión", "carga masiva a Marte: el costo por kilo tiene que bajar unas 27 veces"),
    ("Reutilización", "un cohete que se tira no llega: hay que reutilizar las dos etapas"),
    ("Recarga en órbita", "no alcanza sin varios vuelos cisterna por cada vuelo útil"),
    ("Cadencia", "una ventana hacia Marte cada 26 meses: lanzar seguido pasa a ser requisito"),
    ("Propelente", "el de la vuelta se fabrica allá con CO₂ y agua (Sabatier): metano y oxígeno"),
    ("Motor", "metano, alta presión y reutilización rápida"),
    ("Fabricación", "muchos motores: diseñados para costar poco, no para el máximo rendimiento"),
    ("Estructura", "muchos vehículos, soldados al aire libre y rotos seguido en las pruebas"),
    ("Material", "acero inoxidable: barato, se suelda en un galpón y es más resistente en frío"),
]


def _eslabon(o, i, x, y, w, h, tam_det):
    nombre, det = ESLABONES[i]
    if i == len(ESLABONES) - 1:
        caja(o, x, y, w, h, AZUL_SUAVE, AZUL, 2.25)
    elif i == 0:
        caja(o, x, y, w, h, FONDO, TINTA, 2)
    else:
        caja(o, x, y, w, h, FONDO, TINTA3, 1)
    o.append(f'<circle cx="{x + 20:.1f}" cy="{y + 21:.1f}" r="11" fill="{AZUL}"/>')
    o.append(texto(x + 20, y + 25.5, i + 1, 12, FONDO, 700, anc="middle"))
    o.append(texto(x + 38, y + 26, nombre, 14, TINTA, 700))
    bloque(o, x + 14, y + 38, w - 28, det, tam_det, TINTA2)


def fig_marte(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Por qué un cohete de acero, el material de las ollas?",
             "De la misión al material en nueve eslabones: cada uno obliga al siguiente.")
    x0, y0, A = L.M, L.y, L.A
    if L.ap:
        gx, gy = 40, 44
        w = (A - 2 * gx) / 3
        h = 38 + max(alto(d, 12, w - 28) for _, d in ESLABONES) + 12
        for i in range(9):
            f, c = divmod(i, 3)
            x, y = x0 + c * (w + gx), y0 + f * (h + gy)
            _eslabon(o, i, x, y, w, h, 12)
            if c < 2:
                linea(o, x + w + 3, y + h / 2, x + w + gx - 3, y + h / 2, TINTA, 1.5, flecha="fl")
            elif i < 8:
                xs, xd, ym = x + w / 2, x0 + w / 2, y + h + gy / 2
                o.append(f'<path d="M{xs:.1f},{y + h + 3:.1f} V{ym:.1f} H{xd:.1f} V{y + h + gy - 3:.1f}" '
                         f'fill="none" stroke="{TINTA}" stroke-width="1.5" marker-end="url(#fl)"/>')
        L.y = y0 + 3 * h + 2 * gy
    else:
        gy = 20
        y = y0
        for i in range(9):
            h = 38 + alto(ESLABONES[i][1], 12.5, A - 28) + 10
            _eslabon(o, i, x0, y, A, h, 12.5)
            y += h
            if i < 8:
                linea(o, x0 + 20, y + 2, x0 + 20, y + gy - 2, TINTA, 1.5, flecha="fl")
                y += gy
        L.y = y
    L.pie("Leída desde abajo, la elección del acero parece un capricho. Leída desde la misión, "
          "no había otra.",
          "Ésa es la diferencia entre una decisión de ingeniería y una decisión de misión.",
          "Cadena reconstruida por este libro a partir de lo que SpaceX explicó en público; "
          "no es un documento de diseño de la empresa, y el orden real de las decisiones fue más desordenado.")
    return L.svg("De la misión al material",
                 "Nueve eslabones: misión a Marte, reutilización, recarga en órbita, cadencia, propelente "
                 "fabricado en Marte, motor de metano, fabricación barata, estructura soldada y acero inoxidable.")


# ---------------------------------------------------------------------------
# Fig. 3 · F-33 · Costo por kilo a órbita baja (§2.5)
# ---------------------------------------------------------------------------
KILO = [  # US$ por kilo; Jones 2018 (NASA); el último es un objetivo declarado
    ("Transbordador espacial", "1981-2011", 54500, "lleno"),
    ("Falcon 9", "Jones 2018", 2720, "lleno_azul"),
    ("Starship", "objetivo declarado, no un dato", 100, "hueco"),
]


def fig_costo_kilo(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    L.cabeza("¿Cuánto cuesta subir un kilo a la órbita baja?",
             "Dólares por kilo, en escala logarítmica: cada marca vale diez veces la anterior.")
    filas = [dict(rot=r, sub=s, v=v, trazo=t, etq=("≈ " if t == "hueco" else "") + miles(v))
             for r, s, v, t in KILO]
    L.y += barras_h(L.o, L.M, L.y, L.A, filas, 10, 100000, [10, 100, 1000, 10000, 100000],
                    210 if L.ap else 0, alto_b=32, margen_valor=90)
    d1 = KILO[0][2] / KILO[1][2]
    d2 = KILO[1][2] / KILO[2][2]
    L.pie(f"Del transbordador al Falcon 9, el costo por kilo se dividió por {d1:.0f}. "
          f"El objetivo del Starship pide dividirlo otra vez por {d2:.0f}.",
          "Eso no sale de optimizar el cohete anterior: sale de cambiar el diseño entero (figura 2).",
          "Transbordador y Falcon 9: Jones 2018 (NASA). Barra hueca: objetivo declarado por SpaceX, "
          "no un costo medido.")
    return L.svg("Costo por kilo a órbita baja",
                 "Transbordador espacial ≈ 54.500 dólares por kilo, Falcon 9 ≈ 2.720, y el objetivo "
                 "declarado del Starship, del orden de 100.")


# ---------------------------------------------------------------------------
# Fig. 4 · F-R9 · El mismo cohete, cuatro precios (§2.5, receta R9)
# Datos, verificados contra las fuentes el 2026-10-04:
# - NASA, «Falcon 9 Launch Vehicle NAFCOM Cost Estimates», agosto de 2011
#   (586023main_8-3-11_NAFCOM.pdf), diapositivas 2, 5 y 9. Millones de US$ de 2010.
#   3.977 y 1.695: estimación inicial, ambas a costo más honorario. 443 y 1.383:
#   estimación corregida con los mismos datos técnicos, a precio fijo y a costo más
#   honorario. El precio fijo excluye honorario, soporte del programa e imprevistos.
# - SpaceX: «approximately $300 million» para el Falcon 9; con los ≈ 90 del Falcon 1,
#   ≈ 390. NASA 2010 (Commercial Market Assessment), citado por Zapata 2017
#   (NTRS 20170008895, p. 2), que agrega «NASA has verified these costs».
# - Actuador: Vance 2015, una sola fuente (Steve Davis, Falcon 1).
# ---------------------------------------------------------------------------
COHETE = [
    ("Inicial · cultura NASA", "costo más honorario", 3977, "lleno"),
    ("Inicial · enfoque comercial", "también costo más honorario", 1695, "rayado"),
    ("Corregida · precio fijo", "sin honorario, soporte ni imprevistos", 443, "punteado"),
    ("Declarado por SpaceX", "sólo Falcon 9; con Falcon 1, ≈ 390", 300, "hueco"),
]
CORREGIDA_COSTO_MAS = 1383
ACTUADOR = [
    ("cotizado", 120000, "lleno"),
    ("tope fijado", 5000, "punteado"),
    ("costo final", 3900, "lleno_azul"),
]


def _panel_cohete(o, x0, y0, ancho, rot_w):
    o.append(texto(x0, y0, "A · Desarrollar el Falcon 9, en millones de US$", 14, TINTA, 700))
    o.append(texto(x0, y0 + 17, "escala logarítmica (cada marca vale 10 veces la anterior) · dólares de 2010",
                   12, TINTA2))
    bx0, bx1 = x0 + rot_w, x0 + ancho - 70
    lo, hi = math.log10(100), math.log10(10000)
    X = lambda v: bx0 + (math.log10(v) - lo) / (hi - lo) * (bx1 - bx0)
    top = y0 + 44
    alto_b, sep = 30, 22
    bot = top + len(COHETE) * (alto_b + sep) - sep + 10
    i_grilla = len(o)          # la grilla se inserta acá, detrás de las barras, cuando se sepa dónde van los rótulos
    linea(o, bx0, top - 6, bx0, bot, TINTA3)
    cajas = []
    for i, (rot, sub, v, trazo) in enumerate(COHETE):
        y = top + i * (alto_b + sep)
        o.append(texto(bx0 - 10, y + 13, rot, 12.5, TINTA, 600, anc="end"))
        o.append(texto(bx0 - 10, y + 28, sub, 11, TINTA2, anc="end"))
        o.append(barra(bx0, y, X(v) - bx0, alto_b, trazo))
        pref = "≈ " if trazo == "hueco" else ""
        o.append(texto(X(v) + 8, y + 20, pref + miles(v), 13, TINTA, 700))
        cajas.append(caja_txt(X(v) + 8, y + 20, pref + miles(v), 13, 700))
        if trazo == "punteado":
            xc = X(CORREGIDA_COSTO_MAS)
            linea(o, xc, y - 3, xc, y + alto_b + 3, NARANJA, 2.5, "3 2")
            for dy, s, tam, peso in ((13, miles(CORREGIDA_COSTO_MAS), 11.5, 700),
                                     (27, "mismos datos, a costo", 11, 400), (39, "más honorario", 11, 400)):
                o.append(texto(xc + 6, y + dy, s, tam, TINTA if peso == 700 else TINTA2, peso))
                cajas.append(caja_txt(xc + 6, y + dy, s, tam, peso))
    g = []
    for v in (100, 300, 1000, 3000, 10000):
        vgrilla(g, X(v), top - 6, bot, cajas)
        g.append(texto(X(v), bot + 16, miles(v), 11, TINTA3, anc="middle"))
    o[i_grilla:i_grilla] = g
    return bot + 16, COHETE[0][2] / COHETE[-1][2]


def _panel_actuador(o, x0, y0, ancho, alto_graf):
    o.append(texto(x0, y0, "B · Actuador del Falcon 1, en US$", 14, TINTA, 700))
    o.append(texto(x0, y0 + 17, "escala logarítmica, en dólares", 12, TINTA2))
    top = y0 + 50
    bot = top + alto_graf
    lo, hi = math.log10(1000), math.log10(200000)
    Y = lambda v: bot - (math.log10(v) - lo) / (hi - lo) * (bot - top)
    gx0, gx1 = x0 + 46, x0 + ancho
    for v in (1000, 10000, 100000):
        linea(o, gx0, Y(v), gx1, Y(v), GRILLA)
        o.append(texto(gx0 - 6, Y(v) + 4, miles(v), 11, TINTA3, anc="end"))
    linea(o, gx0, bot, gx1, bot, TINTA3)
    paso = (gx1 - gx0) / len(ACTUADOR)
    bw = min(paso * 0.56, 54)
    for i, (rot, v, trazo) in enumerate(ACTUADOR):
        cx = gx0 + paso * (i + 0.5)
        o.append(barra(cx - bw / 2, Y(v), bw, bot - Y(v), trazo))
        o.append(texto(cx, Y(v) - 7, miles(v), 12.5, TINTA, 700, anc="middle"))
        o.append(texto(cx, bot + 16, rot, 11, TINTA2, anc="middle"))
    return bot + 16, ACTUADOR[0][1] / ACTUADOR[-1][1]


def fig_mismo_cohete(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Cuánto cuesta un cohete? Depende de quién paga si el costo sube.",
             "Tres estimaciones de la NASA y el dato de SpaceX para el mismo Falcon 9: "
             "lo que más cambia es cómo se contrata.")
    if L.ap:
        fin_a, r_a = _panel_cohete(o, L.M, L.y + 14, 570, 235)
        fin_b, r_b = _panel_actuador(o, 640, L.y + 14, 220, fin_a - 16 - (L.y + 14 + 50))
        L.y = max(fin_a, fin_b) + 6
    else:
        fin_a, r_a = _panel_cohete(o, L.M, L.y + 14, L.A, 228)
        fin_b, r_b = _panel_actuador(o, L.M, fin_a + 44, L.A - 120, 170)
        L.y = fin_b + 6
    rc = CORREGIDA_COSTO_MAS / COHETE[2][2]
    L.pie(f"Con los mismos datos, cambiar sólo el contrato divide el costo por {rc:.0f}. "
          f"De punta a punta, por {r_a:.0f}.",
          "SpaceX estima que cada dólar que sale de la empresa cuesta entre 3 y 5, por los gastos y la "
          f"ganancia de los subcontratistas. El actuador: un proveedor cotizó 120.000; hecho en casa, en "
          f"nueve meses, costó 3.900 (factor {r_b:.0f}).",
          "NASA, agosto de 2011 (modelo NAFCOM). La NASA no analizó en detalle de dónde sale la diferencia "
          "con el costo real. Barra hueca: dato de la empresa, no del modelo; la NASA dice haberlo verificado "
          "(NASA 2010, citado por Zapata 2017). Actuador: Vance 2015, una sola fuente.")
    return L.svg("El mismo cohete, cuatro precios",
                 "Costo de desarrollo del Falcon 9 según cuatro formas de contratarlo (NASA 2011): 3.977, "
                 "1.695 y 443 millones de dólares de 2010 (1.383 con los mismos datos a costo más honorario), "
                 "contra unos 300 declarados por SpaceX; y un actuador cotizado en 120.000 dólares que "
                 "terminó costando 3.900.")


# ---------------------------------------------------------------------------
# Fig. 5 · F-N1 · El avión tirado o reutilizado (§3.1)
# ---------------------------------------------------------------------------
AVION_US = 50e6
ASIENTOS = 180
VUELOS = 50000


def fig_avion(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    por_pas = AVION_US / ASIENTOS
    reus = por_pas / VUELOS
    L.cabeza("¿Cuánto cuesta el avión en cada pasaje?",
             f"Un avión de pasillo único: unos US$50 millones y {ASIENTOS} asientos. "
             "Tirado después de un vuelo, o usado toda su vida.")
    x0, A = L.M, L.A
    y = L.y
    hb = 34
    # Fila 1: tirado
    o.append(texto(x0, y + 14, "Se tira después de un vuelo", 14, TINTA, 700))
    o.append(texto(x0, y + 32, f"≈ US${miles(int(round(por_pas, -4)))} por pasajero", 13, NARANJA, 700))
    y += 44
    xe = x0 + A - 34
    o.append(barra(x0, y, xe - x0 - 14, hb, "lleno"))
    # borde roto: zigzag
    zz = " ".join(f"{xe - 14 + (6 if k % 2 else 0):.1f},{y + k * hb / 6:.1f}" for k in range(7))
    o.append(f'<polygon points="{xe - 14:.1f},{y:.1f} {zz} {xe - 14:.1f},{y + hb:.1f}" fill="{NARANJA}"/>')
    linea(o, xe + 2, y + hb / 2, x0 + A, y + hb / 2, NARANJA, 2, "4 3", flecha="fl_na")
    bloque(o, x0, y + hb + 6, A, "y sigue: si la barra de abajo mide 1 milímetro, ésta mide 50 metros", 12,
           TINTA2, 400, anc="end")
    y += hb + 46
    # Fila 2: reutilizado
    o.append(texto(x0, y + 14, f"Se reutiliza: unos {miles(VUELOS)} vuelos en su vida", 14, TINTA, 700))
    o.append(texto(x0, y + 32, f"≈ US${reus:.0f} por pasajero", 13, AZUL, 700))
    y += 44
    o.append(barra(x0, y, 3, hb, "lleno_azul"))
    linea(o, x0 + 8, y + hb / 2, x0 + 44, y + hb / 2, TINTA, 1.2)
    o.append(texto(x0 + 50, y + hb / 2 + 4.5, "esta rayita: 1 milímetro", 12.5, TINTA, 600))
    L.y = y + hb
    L.pie(f"Mismo metal, mismo combustible, misma tripulación: la diferencia no es tecnología, "
          f"es una división por {miles(VUELOS)}.",
          condicion="Orden de magnitud: ilustra el cociente, no es una contabilidad. Cuenta sólo el avión, "
          "sin combustible, tripulación ni mantenimiento.")
    return L.svg("El mismo avión, tirado o reutilizado",
                 "Un avión de 50 millones de dólares y 180 asientos cuesta unos 280.000 dólares por pasajero "
                 "si se tira tras un vuelo, y unos 6 si se reutiliza 50.000 vuelos: una división por 50.000.")


# ---------------------------------------------------------------------------
# Fig. 6 · F-N2 · El signo del margen (§3.2)
# ---------------------------------------------------------------------------
CF = 1000
M_POS, M_NEG = 10, -5


def fig_signo(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Vender más salva un negocio?",
             f"Ganancia del mes según las unidades vendidas, con el mismo costo fijo de {miles(CF)} "
             "y dos márgenes por unidad.")
    x0, A = L.M, L.A
    top = L.y + 8
    hg = 270 if L.ap else 300
    bot = top + hg
    px0 = x0 + 62
    px1 = x0 + A - (190 if L.ap else 10)
    qmax, pmin, pmax = 200, -2500, 1100
    X = lambda q: px0 + q / qmax * (px1 - px0)
    Y = lambda p: bot - (p - pmin) / (pmax - pmin) * (bot - top)
    for p in (-2000, -1000, 0, 1000):
        linea(o, px0, Y(p), px1, Y(p), TINTA3 if p == 0 else GRILLA, 1.4 if p == 0 else 1)
        o.append(texto(px0 - 8, Y(p) + 4, ("−" if p < 0 else "") + miles(abs(p)), 11, TINTA3, anc="end"))
    for q in (0, 50, 100, 150, 200):
        o.append(texto(X(q), bot + 18, q, 11, TINTA3, anc="middle"))
    o.append(texto((px0 + px1) / 2, bot + 36, "unidades vendidas por mes", 11.5, TINTA2, anc="middle"))
    yc = (top + bot) / 2
    o.append(texto(x0 + 6, yc, "ganancia del mes", 11.5, TINTA2, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 6} {yc})"'))
    o.append(texto(px1, Y(0) - 6, "equilibrio", 11, TINTA3, anc="end"))
    # rectas
    linea(o, X(0), Y(-CF), X(qmax), Y(M_POS * qmax - CF), AZUL, 2.5)
    linea(o, X(0), Y(-CF), X(qmax), Y(M_NEG * qmax - CF), NARANJA, 2.5, "8 5")
    qs = CF / M_POS
    o.append(f'<circle cx="{X(qs):.1f}" cy="{Y(0):.1f}" r="5" fill="{AZUL}" stroke="{FONDO}" stroke-width="2"/>')
    o.append(texto(X(qs) - 10, Y(0) - 12, f"Q* = CF ÷ m = {qs:.0f}", 12.5, TINTA, 700, anc="end"))
    if L.ap:
        o.append(texto(X(qmax) + 10, Y(M_POS * qmax - CF) + 4, "m = +10 por unidad", 12.5, AZUL, 700))
        o.append(texto(X(qmax) + 10, Y(M_POS * qmax - CF) + 20, "el volumen lleva al equilibrio", 11.5, TINTA2))
        o.append(texto(X(qmax) + 10, Y(M_NEG * qmax - CF) + 4, "m = −5 por unidad", 12.5, NARANJA, 700))
        o.append(texto(X(qmax) + 10, Y(M_NEG * qmax - CF) + 20, "cada venta agranda la pérdida", 11.5, TINTA2))
    else:
        o.append(texto(px0 + 10, Y(1000) + 24, "— m = +10 por unidad", 12.5, AZUL, 700))
        o.append(texto(px0 + 10, Y(1000) + 42, "- - m = −5 por unidad", 12.5, NARANJA, 700))
    linea(o, X(1), Y(-CF) + 4, X(9), Y(-1780) - 12, TINTA3, 1)
    o.append(texto(X(9), Y(-1780), f"vender cero: se pierde el costo fijo ({miles(CF)})", 11.5, TINTA2))
    L.y = bot + 40
    L.pie("Con margen positivo, el volumen lleva al equilibrio. Con margen negativo, crecer acelera la quiebra.",
          "Si cada unidad empobrece, está prohibido escalar: primero se arregla el margen.",
          "Números ilustrativos. El margen m = precio − costo variable se mide con todos los costos variables: "
          "materiales, horas, comisiones, envío.")
    return L.svg("El signo del margen",
                 "Dos rectas de ganancia contra unidades vendidas con costo fijo de 1.000: con margen +10 llega "
                 "al equilibrio en 100 unidades; con margen −5, cada venta agranda la pérdida.")


# ---------------------------------------------------------------------------
# Fig. 7 · F-N3b · 88 contra millones (§3.3)
# ---------------------------------------------------------------------------
TASAS = [  # r, rótulo del volumen como en la tabla del texto
    (0.30, "≈ 88 ×"), (0.25, "≈ 256 ×"), (0.20, "≈ 1.280 ×"), (0.15, "≈ 18.400 ×"), (0.10, "≈ 3,8 millones ×"),
]


def _etq_pot(v):
    k = round(math.log10(v))
    return {0: "1", 1: "10", 2: "100", 3: "1.000", 4: "10.000", 5: "100.000",
            6: "1 millón", 7: "10 mill."}[k]


def fig_88_contra_millones(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    L.cabeza("Para dividir el costo por diez, ¿cuánto más hay que fabricar?",
             "Volumen acumulado necesario según la tasa de aprendizaje r (cuánto baja el costo "
             "cada vez que se duplica lo hecho). Escala logarítmica.")
    filas = []
    for r, etq in TASAS:
        n = math.log(0.1) / math.log(1 - r)
        v = 2 ** n
        assert abs(v / float(etq.split()[1].replace(".", "").replace(",", ".")) /
                   (1e6 if "millones" in etq else 1) - 1) < 0.02, (r, v, etq)
        trazo = "lleno_azul" if r == 0.30 else ("lleno" if r == 0.10 else "suave")
        filas.append(dict(rot=f"r = {r * 100:.0f} %", sub=f"{coma(n)} duplicaciones", v=v, trazo=trazo, etq=etq))
    marcas = [1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7] if L.ap else [1, 100, 1e4, 1e6]
    L.y += barras_h(L.o, L.M, L.y, L.A, filas, 1, 1e7, marcas,
                    150 if L.ap else 118, etq_marca=_etq_pot, alto_b=26, sep=18,
                    margen_valor=150 if L.ap else 120)
    L.pie("Con 30 % de aprendizaje alcanza con 88 veces el volumen; con 10 %, casi cuatro millones.",
          "Es el mismo objetivo y son dos universos: uno es un plan de negocios, el otro una fantasía. "
          "Y depende de un número que casi nadie mide.",
          "Ley de Wright: duplicaciones N = ln(0,1) ÷ ln(1 − r); el volumen acumulado se multiplica por 2^N. "
          "Supone que r se mantiene; hay que medirlo en cada caso.")
    return L.svg("Para dividir el costo por diez",
                 "Volumen acumulado necesario para bajar el costo a la décima parte: con r de 30 % es 88 veces; "
                 "25 %, 256; 20 %, 1.280; 15 %, 18.400; 10 %, unos 3,8 millones de veces.")


# ---------------------------------------------------------------------------
# Fig. 8 · F-N3a · El «piso» es muchas veces un efecto del eje (§3.3)
# ---------------------------------------------------------------------------
def _piso_panel_a(o, px, py, w, r, costo):
    ax0, ax1 = px + 30, px + w
    top, bot = py + 50, py + 280
    X = lambda n: ax0 + n / 1024 * (ax1 - ax0)
    Y = lambda c: bot - c / 100 * (bot - top)
    o.append(texto(px, py, "A · Como se mira casi siempre", 14, TINTA, 700))
    o.append(texto(px, py + 17, "eje común: unidades de 0 a 1.024", 12, TINTA2))
    for c in (0, 25, 50, 75, 100):
        linea(o, ax0, Y(c), ax1, Y(c), GRILLA)
        o.append(texto(ax0 - 8, Y(c) + 4, c, 11, TINTA3, anc="end"))
    for n in (0, 256, 512, 768, 1024):
        o.append(texto(X(n), bot + 18, miles(n), 11, TINTA3, anc="middle"))
    o.append(texto((ax0 + ax1) / 2, bot + 36, "unidades hechas en total", 11.5, TINTA2, anc="middle"))
    o.append(texto(ax0 - 52, (top + bot) / 2, "costo por unidad (la 1.ª = 100)", 11.5, TINTA2,
                   anc="middle", extra=f'transform="rotate(-90 {ax0 - 52} {(top + bot) / 2})"'))
    y_piso = Y(14)
    linea(o, X(230), y_piso, ax1, y_piso, NARANJA, 2, "6 5")
    # el rótulo va entre las grillas de 25 y 50, para que ninguna lo cruce
    o.append(texto(X(640), Y(25) - 24, "«ya no baja:", 12.5, TINTA, 600, anc="middle"))
    o.append(texto(X(640), Y(25) - 8, "llegué al piso»", 12.5, TINTA, 600, anc="middle"))
    linea(o, X(640), Y(25) - 2, X(640), y_piso - 5, NARANJA, 1.5)
    pts, n = [], 1.0
    while n <= 1024:
        pts.append(f"{X(n):.1f},{Y(costo(n)):.1f}")
        n = n * 1.04 if n > 4 else n + 0.05
    pts.append(f"{X(1024):.1f},{Y(costo(1024)):.1f}")
    o.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{AZUL}" '
             f'stroke-width="2.25" stroke-linejoin="round"/>')
    for k in range(11):
        o.append(f'<circle cx="{X(2 ** k):.1f}" cy="{Y(costo(2 ** k)):.1f}" r="4.5" fill="{AZUL}" '
                 f'stroke="{FONDO}" stroke-width="2"/>')
    yb = top - 14
    o.append(f'<path d="M{X(1):.1f},{yb + 8} V{yb} H{X(128):.1f} V{yb + 8}" fill="none" '
             f'stroke="{TINTA}" stroke-width="1.2"/>')
    o.append(texto(X(128) + 12, yb + 32, "8 de los 11 puntos", 12, TINTA, 700))   # debajo de la grilla de 100
    o.append(texto(X(128) + 12, yb + 47, "están amontonados acá,", 12, TINTA2))
    o.append(texto(X(128) + 12, yb + 62, "en el primer 12 % del eje", 12, TINTA2))
    return 320


def _piso_panel_b(o, px, py, w, r):
    bx0, bx1 = px + 20, px + w
    top, bot = py + 50, py + 280
    paso = (bx1 - bx0) / 10
    XB = lambda k: bx0 + k * paso
    lo, hi = math.log10(9), math.log10(100)
    YB = lambda c: top + (hi - math.log10(c)) / (hi - lo) * (bot - top)
    o.append(texto(px, py, "B · Como hay que mirarla", 14, TINTA, 700))
    o.append(texto(px, py + 17, "cada marca del eje es el doble de la anterior", 12, TINTA2))
    d = f"M{XB(0):.1f},{bot}"
    for k in range(10):
        d += f" V{YB(100 * (1 - r) ** k):.1f} H{XB(k + 1):.1f}"
    o.append(f'<path d="{d} V{bot} Z" fill="{AZUL_SUAVE}" stroke="none"/>')
    d = f"M{XB(0):.1f},{YB(100):.1f}"
    for k in range(10):
        d += f" H{XB(k + 1):.1f} V{YB(100 * (1 - r) ** (k + 1)):.1f}"
    o.append(f'<path d="{d}" fill="none" stroke="{AZUL}" stroke-width="2.25" stroke-linejoin="round"/>')
    for k in range(11):
        c = 100 * (1 - r) ** k
        o.append(f'<circle cx="{XB(k):.1f}" cy="{YB(c):.1f}" r="4.5" fill="{AZUL}" '
                 f'stroke="{FONDO}" stroke-width="2"/>')
        o.append(texto(XB(k) + 4, YB(c) - 9, f"{c:.0f}", 11, TINTA, 600))
        o.append(texto(XB(k), bot + 18, miles(2 ** k), 11, TINTA3, anc="middle"))
    linea(o, bx0, bot, bx1, bot, TINTA3)
    o.append(texto((bx0 + bx1) / 2, bot + 36, "unidades hechas en total", 11.5, TINTA2, anc="middle"))
    k = 6
    xm, ym = (XB(k) + XB(k + 1)) / 2, YB(100 * (1 - r) ** k)
    xa, ya = XB(5.3), top + 6
    linea(o, xm, ym - 4, xm, ya + 40, TINTA)
    o.append(texto(xa, ya, "cada escalón:", 12, TINTA, 700))
    o.append(texto(xa, ya + 15, "el doble de unidades,", 12, TINTA2))
    o.append(texto(xa, ya + 30, f"y la misma bajada: −{r * 100:.0f} %", 12, TINTA2))
    return 320


def fig_piso_del_eje(diagramacion="apaisada", r=0.20):
    b = -math.log2(1 - r)
    costo = lambda n: 100 * n ** (-b)
    L = Lienzo(diagramacion)
    L.cabeza("¿Llegaste al piso, o cambió la escala?",
             f"La misma curva de aprendizaje —el costo baja {r * 100:.0f} % cada vez que se duplica lo hecho "
             "en total— dibujada dos veces.")
    if L.ap:
        _piso_panel_a(L.o, 40, L.y + 14, 380, r, costo)
        _piso_panel_b(L.o, 490, L.y + 14, 370, r)
        L.y += 14 + 320
    else:
        _piso_panel_a(L.o, 40, L.y + 14, L.A, r, costo)
        L.y += 14 + 320 + 34
        _piso_panel_b(L.o, 40, L.y, L.A, r)
        L.y += 320
    L.pie("La curva no se aplanó: cada escalón pide el doble de volumen que el anterior.",
          "De 128 a 256 unidades hacen falta 128 más; de 512 a 1.024, 512 más. Mirada por mes parece un piso; "
          "mirada por duplicación, sigue bajando.",
          f"Ley de Wright con r = {r * 100:.0f} % por duplicación (b = {coma(b, 3)}). La curva no es automática: "
          "baja sólo si en cada duplicación alguien rediseña el proceso.")
    return L.svg("El «piso» de la curva de aprendizaje es muchas veces un efecto del eje",
                 "La misma curva de Wright con 20 % de aprendizaje por duplicación, dibujada con eje común "
                 "(parece aplanarse) y con eje por duplicaciones (es una escalera que sigue bajando 20 % por escalón).")


# ---------------------------------------------------------------------------
# Fig. 9 · F-N4 · El lazo (§3.4)
# ---------------------------------------------------------------------------
def _lazo_circulo(o, cx, cy, R):
    nodos = [(-90, "el costo baja"), (0, "el precio baja"), (90, "la demanda sube"), (180, "el volumen crece")]
    arcos = [(-48, -15, "t", "traslado", "al precio"), (15, 48, "ε", "elasticidad", "de la demanda"),
             (132, 165, "", "se vende", "lo pedido"), (195, 228, "b", "aprendizaje:", "r = 20 % → 0,32")]
    P = lambda a, rr=R: (cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)))
    for a1, a2, letra, l1, l2 in arcos:
        (xa, ya), (xb, yb) = P(a1), P(a2)
        o.append(f'<path d="M{xa:.1f},{ya:.1f} A{R},{R} 0 0 1 {xb:.1f},{yb:.1f}" fill="none" '
                 f'stroke="{AZUL}" stroke-width="2.5" marker-end="url(#fl_az)"/>')
        am = (a1 + a2) / 2
        xt, yt = P(am, R + 16)
        anc = "start" if math.cos(math.radians(am)) > 0 else "end"
        dy = -22 if math.sin(math.radians(am)) < 0 else 4
        if letra:
            o.append(texto(xt, yt + dy + 12, letra, 17, AZUL, 700, anc=anc))
        o.append(texto(xt, yt + dy + 28, l1, 11.5, TINTA2, anc=anc))
        o.append(texto(xt, yt + dy + 42, l2, 11.5, TINTA2, anc=anc))
    for a, s in nodos:
        x, y = P(a)
        w = ancho_txt(s, 12.5, 600) + 18
        caja(o, x - w / 2, y - 16, w, 32, FONDO, AZUL, 1.6, rx=16)
        o.append(texto(x, y + 4.5, s, 12.5, TINTA, 600, anc="middle"))
    o.append(texto(cx, cy - 2, "G = t × ε × b", 15, TINTA, 700, anc="middle"))
    o.append(texto(cx, cy + 17, "la ganancia del lazo", 11.5, TINTA2, anc="middle"))


def _lazo_series(o, x0, y0, w):
    o.append(texto(x0, y0 + 14, "Una baja inicial de 1 termina valiendo", 13.5, TINTA, 700))
    o.append(texto(x0, y0 + 32, "1 + G + G² + G³ + …", 13.5, TINTA, 700))
    y = y0 + 54
    u = min(58.0, (w - 70) / 5.2)
    lim = x0 + w - 30
    for G, total in ((0.5, "→ × 2"), (0.8, "→ × 5"), (1.1, "se desboca")):
        o.append(texto(x0, y + 13, f"G = {coma(G)}", 13, TINTA, 700))
        o.append(texto(x0 + w, y + 13, total, 13, NARANJA if G >= 1 else AZUL, 700, anc="end"))
        y += 20
        x, k = x0, 0
        while x < lim and k < 40:
            seg = u * G ** k
            if seg < 0.8:
                break
            seg = min(seg, lim - x)
            fill = (AZUL if k % 2 == 0 else AZUL_SUAVE) if G < 1 else (NARANJA if k % 2 == 0 else NARANJA_SUAVE)
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{seg:.1f}" height="24" fill="{fill}" '
                     f'stroke="{FONDO}" stroke-width="1"/>')
            x += seg
            k += 1
        if G >= 1:
            linea(o, lim + 2, y + 12, x0 + w, y + 12, NARANJA, 2, "4 3", flecha="fl_na")
        else:
            linea(o, x0 + u / (1 - G), y - 4, x0 + u / (1 - G), y + 28, TINTA, 1.5, "3 2")
        y += 40
    bloque(o, x0, y - 6, w, "Cada tramo es G veces el anterior. Si G < 1, la suma tiene techo: 1 ÷ (1 − G). "
           "Si G ≥ 1, crece hasta que algo lo frena.", 11.5, TINTA2)
    return y + 34 - y0


def fig_lazo(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    L.cabeza("¿El volante gira solo, o hay que empujarlo para siempre?",
             "Costo, precio, demanda y volumen: un número en cada flecha. Su producto, G, decide.")
    if L.ap:
        R = 132
        _lazo_circulo(L.o, L.M + 228, L.y + 24 + R + 10, R)
        h = _lazo_series(L.o, L.M + 490, L.y + 10, L.A - 490)
        L.y += max(2 * R + 70, h)
    else:
        R = 130
        _lazo_circulo(L.o, L.M + L.A / 2, L.y + 24 + R + 10, R)
        L.y += 2 * R + 80
        L.y += _lazo_series(L.o, L.M, L.y, L.A)
    L.pie("El volante es una suma: con G = 0,5 una baja de costo vale el doble; con 0,8, cinco veces; "
          "con G ≥ 1 se desboca hasta que el mercado, la capacidad o la caja lo frenan.",
          "Ejemplo del texto: t = 1, ε = 1,5 y b = 0,32 dan G ≈ 0,48: útil, no milagroso. "
          "Si no se puede poner un número en al menos dos flechas, no es un lazo: es un dibujo.",
          "Modelo simplificado de largo plazo, sin retardos ni saturación. Con r = 20 % (b ≈ 0,32) y t = 1, "
          "G pasa de 1 sólo si ε > 3, cosa que pasa pocas veces y dura poco.")
    return L.svg("El lazo",
                 "Un círculo de cuatro pasos: el costo baja, el precio baja, la demanda sube, el volumen crece, "
                 "con t, ε y b en las flechas. Al lado, la suma 1 + G + G² que converge a 2 con G = 0,5, a 5 con "
                 "G = 0,8 y se desboca con G mayor que 1.")


# ---------------------------------------------------------------------------
# Fig. 10 · F-N5a · El pozo (§3.5)
# ---------------------------------------------------------------------------
PERDIDA0 = 10_000      # US$ por mes al arrancar (ilustrativo)
DUPL, MESES_DUPL = 10, 8
CAJA = 250_000


def fig_pozo(diagramacion="apaisada"):
    T = DUPL * MESES_DUPL
    acum = lambda t: -PERDIDA0 * t + PERDIDA0 * t * t / (2 * T)
    prof = -acum(T)
    # mes en que se acaba la caja: acum(t) = -CAJA
    a, b_, c = PERDIDA0 / (2 * T), -PERDIDA0, CAJA
    t_c = (-b_ - math.sqrt(b_ * b_ - 4 * a * c)) / (2 * a)
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Alcanza la caja para llegar al fondo del pozo?",
             f"Faltan {DUPL} duplicaciones y cada una tarda {MESES_DUPL} meses: {T} meses, casi "
             f"{coma(T / 12, 0)} años, perdiendo dinero cada mes un poco menos.")
    x0, A = L.M, L.A
    top = L.y + 30
    hg = 250 if L.ap else 280
    bot = top + hg
    px0, px1 = x0 + 74, x0 + A - (10 if L.ap else 6)
    tmax, ymin, ymax = 2 * T, -460_000, 40_000
    X = lambda t: px0 + t / tmax * (px1 - px0)
    Y = lambda v: top + (ymax - v) / (ymax - ymin) * (bot - top)
    for v in (0, -100_000, -200_000, -300_000, -400_000):
        linea(o, px0, Y(v), px1, Y(v), TINTA3 if v == 0 else GRILLA, 1.4 if v == 0 else 1)
        o.append(texto(px0 - 8, Y(v) + 4, ("−" if v else "") + miles(abs(v)), 11, TINTA3, anc="end"))
    for t in range(0, tmax + 1, 20):
        o.append(texto(X(t), bot + 18, t, 11, TINTA3, anc="middle"))
    o.append(texto((px0 + px1) / 2, bot + 36, "meses desde el arranque", 11.5, TINTA2, anc="middle"))
    yc = (top + bot) / 2
    o.append(texto(x0 + 4, yc, "dinero acumulado (US$)", 11.5, TINTA2, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 4} {yc})"'))
    pts = [(t / 2, acum(t / 2)) for t in range(0, 2 * tmax + 1)]
    area = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in pts)
    o.append(f'<polygon points="{X(0):.1f},{Y(0):.1f} {area} {X(tmax):.1f},{Y(0):.1f}" fill="{AZUL_SUAVE}" '
             f'fill-opacity="0.6"/>')
    antes = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in pts if t <= t_c)
    despues = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in pts if t >= t_c)
    o.append(f'<polyline points="{antes}" fill="none" stroke="{AZUL}" stroke-width="2.5"/>')
    o.append(f'<polyline points="{despues}" fill="none" stroke="{TINTA3}" stroke-width="2" stroke-dasharray="6 4"/>')
    # caja
    linea(o, px0, Y(-CAJA), px1, Y(-CAJA), NARANJA, 2, "7 4")
    if L.ap:
        o.append(texto(px1, Y(-CAJA) + 18, f"caja disponible: {miles(CAJA)}", 12, NARANJA, 700, anc="end"))
    else:   # en la vertical la curva gris pasa por la punta derecha: el rótulo va junto al punto, arriba
        o.append(texto(X(t_c) + 14, Y(-CAJA) - 8, f"caja: {miles(CAJA)}", 12, NARANJA, 700))
    o.append(f'<circle cx="{X(t_c):.1f}" cy="{Y(-CAJA):.1f}" r="6" fill="{NARANJA}" stroke="{FONDO}" stroke-width="2"/>')
    o.append(texto(X(t_c) - 10, Y(-CAJA) + (22 if L.ap else 15), f"se acaba en el mes {t_c:.0f}",
                   12.5 if L.ap else 12, TINTA, 700, anc="end"))
    # profundidad
    linea(o, X(T), Y(0) + 3, X(T), Y(-prof) - 3, TINTA, 1.3, flecha="fl", inicio=True)
    o.append(texto(X(T) + 8, Y(-prof * 0.8), "profundidad:", 12, TINTA, 700))
    o.append(texto(X(T) + 8, Y(-prof * 0.8) + 15, miles(round(prof)), 12, TINTA, 700))
    # ancho
    ya = Y(0) - 14
    linea(o, X(0) + 2, ya, X(T) - 2, ya, TINTA, 1.3, flecha="fl", inicio=True)
    o.append(texto((X(0) + X(T)) / 2, ya - 7, f"ancho: {T} meses hasta que el mes deja de perder", 12, TINTA, 700,
                   anc="middle"))
    o.append(texto(X(tmax) - 4, Y(0) - 8, "vuelve a cero", 11, TINTA2, anc="end"))
    L.y = bot + 40
    L.pie(f"Si la caja es menos profunda que el pozo, el plan no es un plan: con {miles(CAJA)}, se acaba en el "
          f"mes {t_c:.0f}, cuatro años antes del fondo.",
          "Antes de empezar: profundidad y ancho del pozo contra la caja y los meses de autonomía.",
          f"Ilustrativo: la pérdida arranca en {miles(PERDIDA0)} por mes y baja en línea recta hasta cero en el mes "
          f"{T}; profundidad = {miles(PERDIDA0)} × {T} ÷ 2. La fórmula del texto supone la pérdida constante y da el "
          "doble: es la cota prudente. Con retardos (§3.4) el pozo es más ancho.")
    return L.svg("El pozo",
                 f"Curva J del dinero acumulado: baja hasta {miles(round(prof))} dólares en el mes {T} y vuelve a "
                 f"cero en el mes {tmax}; con una caja de {miles(CAJA)}, el dinero se acaba en el mes {t_c:.0f}.")


# ---------------------------------------------------------------------------
# Fig. 11 · F-N5b · Mil personas, la misma moneda (§3.5 y §8.2)
# ---------------------------------------------------------------------------
P_GANA, FRACCION = 0.6, 0.20
GANADORES = [37, 212, 455, 601, 788, 943]


def _monedas_tabla(o, x0, y0, w):
    n10 = 1000 * P_GANA ** 10
    med10 = (1 + FRACCION) ** 6 * (1 - FRACCION) ** 4
    med100 = (1 + FRACCION) ** 60 * (1 - FRACCION) ** 40
    assert round(n10) == 6 and abs(med100 - 7.5) < 0.1 and abs(med10 - 1.22) < 0.01
    c0 = w * 0.30
    cw = (w - c0) / 2
    filas = [("Apostar todo", NARANJA_SUAVE,
              [f"quedan {n10:.0f}", "cada una × 1.024"], ["no queda nadie", ""]),
             (f"Apostar el {FRACCION * 100:.0f} %", AZUL_SUAVE,
              ["quedan 1.000", f"la típica × {coma(med10, 2)}"], ["quedan 1.000", f"la típica × {coma(med100)}"])]
    o.append(texto(x0 + c0 + cw / 2, y0 + 14, "a las 10 tiradas", 12, TINTA2, 700, anc="middle"))
    o.append(texto(x0 + c0 + 1.5 * cw, y0 + 14, "a las 100 tiradas", 12, TINTA2, 700, anc="middle"))
    y = y0 + 24
    for rot, fill, a, b in filas:
        bloque(o, x0, y + 8, c0 - 8, rot, 13, TINTA, 700)
        for j, cel in enumerate((a, b)):
            xc = x0 + c0 + j * cw
            caja(o, xc + 3, y, cw - 6, 54, fill, rx=4)
            o.append(texto(xc + cw / 2, y + 23, cel[0], 13.5, TINTA, 700, anc="middle"))
            if cel[1]:
                o.append(texto(xc + cw / 2, y + 42, cel[1], 12, TINTA2, anc="middle"))
        y += 60
    return y - y0


def fig_mil_monedas(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("Mil personas, la misma moneda favorable: ¿apostar todo, o el 20 %?",
             "La moneda sale bien el 60 % de las veces y paga 1 a 1. Cada punto es una persona que apostó todo, "
             "diez veces seguidas.")
    x0, A = L.M, L.A
    if L.ap:
        sx, gx0, gy0 = 9.5, x0, L.y + 34
    else:
        sx, gx0, gy0 = 12.5, x0 + (A - 39 * 12.5) / 2, L.y + 34
    o.append(texto(x0, L.y + 12, "Apostar todo, a las 10 tiradas:", 13.5, TINTA, 700))
    o.append(texto(x0 + ancho_txt("Apostar todo, a las 10 tiradas:", 13.5, 700) + 8, L.y + 12,
                   "quedan 6", 13.5, AZUL, 700))
    for i in range(1000):
        f, c = divmod(i, 40)
        cx, cy = gx0 + c * sx, gy0 + f * sx
        if i in GANADORES:
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{sx * 0.42:.1f}" fill="{AZUL}"/>')
        else:
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{sx * 0.3:.1f}" fill="none" stroke="{GRIS}" '
                     f'stroke-width="1"/>')
    gy1 = gy0 + 24 * sx
    ly = gy1 + 22
    o.append(f'<circle cx="{x0 + 5:.1f}" cy="{ly - 4:.1f}" r="4.5" fill="{AZUL}"/>')
    o.append(texto(x0 + 16, ly, "las 6 que ganaron las diez: cada una × 1.024", 12, TINTA))
    o.append(f'<circle cx="{x0 + 5:.1f}" cy="{ly + 14:.1f}" r="3.5" fill="none" stroke="{GRIS}"/>')
    o.append(texto(x0 + 16, ly + 18, "las 994 que quebraron en alguna tirada", 12, TINTA))
    if L.ap:
        h = _monedas_tabla(o, x0 + 420, L.y + 70, A - 420)
        L.y = max(ly + 26, L.y + 70 + h)
    else:
        L.y = ly + 44
        L.y += _monedas_tabla(o, x0, L.y, A)
    L.pie("Las 6 dan entrevistas y escriben libros. De las 994 restantes no hay biografías.",
          "Con el 20 % no quiebra nadie, pero a las 10 tiradas casi no se nota (+22 %): la prudencia "
          "gana a largo plazo y no luce en el corto.",
          "Cálculo: 1.000 × 0,6¹⁰ ≈ 6; 1,2⁶⁰ × 0,8⁴⁰ ≈ 7,5. El 20 % es la fracción de Kelly (1956) para "
          "esta moneda. «La típica» es la mediana. Los puntos azules están puestos al azar.")
    return L.svg("Mil personas, la misma moneda",
                 "Mil puntos: seis azules son las personas que apostaron todo y ganaron diez tiradas seguidas; "
                 "las 994 restantes quebraron. Apostando el 20 % no quiebra nadie y la mediana a las 100 tiradas "
                 "multiplica por 7,5.")


# ---------------------------------------------------------------------------
# Fig. 12 · F-12 · Peldaño, piso y pozo (§3.6)
# ---------------------------------------------------------------------------
CASILLAS = {  # (vende, abarata): rótulo, nota, fill, stroke, dash, color texto
    (True, True): ("PELDAÑO", "se sube por acá", AZUL, AZUL, None, FONDO),
    (True, False): ("PISO", "se vive bien, pero no se sube", AZUL_SUAVE, AZUL, None, TINTA),
    (False, True): ("POZO", "saber cuánto dura (§3.5)", NARANJA_SUAVE, NARANJA, "5 4", TINTA),
    (False, False): ("CORTAR", "no vende ni abarata", GRIS_SUAVE, TINTA3, None, TINTA),
}
ESCALERAS = [
    ("SpaceX", [("Falcon 1", "POZO", "no era un negocio: instaló la posición"),
                ("Falcon 9", "PELDAÑO", "vende y financia el siguiente"),
                ("Starship y Starlink", "PELDAÑO", "Starlink es la carga que justifica la escala")]),
    ("Un taller (ilustrativo)", [("Encargo a pedido", "PISO", "si no deja nada instalado"),
                                 ("El primer molde", "POZO", "no es un producto: es una posición"),
                                 ("El segundo producto", "PELDAÑO", "sale más barato con el mismo molde")]),
]


def _matriz(o, x0, y0, w):
    c0, r0 = 64, 46
    cw, ch = (w - c0) / 2, 74
    o.append(texto(x0 + c0 + cw, y0 + 12, "¿Abarata la etapa siguiente?", 13, TINTA, 700, anc="middle"))
    o.append(texto(x0 + c0 + cw / 2, y0 + 32, "Sí", 12.5, TINTA2, 700, anc="middle"))
    o.append(texto(x0 + c0 + 1.5 * cw, y0 + 32, "No", 12.5, TINTA2, 700, anc="middle"))
    yc = y0 + r0 + ch
    o.append(texto(x0 + 8, yc, "¿Vende algo hoy?", 13, TINTA, 700, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 8} {yc})"'))
    for i, vende in enumerate((True, False)):
        o.append(texto(x0 + c0 - 10, y0 + r0 + i * ch + ch / 2 + 4, "Sí" if vende else "No", 12.5, TINTA2, 700,
                       anc="end"))
        for j, abarata in enumerate((True, False)):
            rot, nota, fill, st, dash, col = CASILLAS[(vende, abarata)]
            x, y = x0 + c0 + j * cw, y0 + r0 + i * ch
            caja(o, x + 3, y + 3, cw - 6, ch - 6, fill, st, 1.6, dash, rx=4)
            o.append(texto(x + cw / 2, y + ch / 2 - 2, rot, 15, col, 700, anc="middle"))
            bloque(o, x + 10, y + ch / 2 + 4, cw - 20, nota, 11.5, col if col == FONDO else TINTA2, anc="middle")
    return r0 + 2 * ch


def _escalera(o, x0, y0, w, nombre, pasos):
    o.append(texto(x0, y0 + 13, nombre, 13.5, TINTA, 700))
    gap, dy = 22, 16
    bw = (w - 2 * gap) / 3
    hmax = 0
    for k, (paso, cat, nota) in enumerate(pasos):
        hmax = max(hmax, 46 + alto(nota, 11.5, bw - 16))
    base = y0 + 24 + 2 * dy
    for k, (paso, cat, nota) in enumerate(pasos):
        x, y = x0 + k * (bw + gap), base - k * dy
        st = {"PELDAÑO": (FONDO, AZUL, None), "POZO": (FONDO, NARANJA, "5 4"), "PISO": (FONDO, TINTA3, None)}[cat]
        caja(o, x, y, bw, hmax, st[0], st[1], 1.8, st[2], rx=4)
        o.append(texto(x + 8, y + 17, paso, 12.5, TINTA, 700))
        col = {"PELDAÑO": AZUL, "POZO": NARANJA, "PISO": TINTA2}[cat]
        o.append(texto(x + 8, y + 33, cat.lower(), 11.5, col, 700))
        bloque(o, x + 8, y + 37, bw - 16, nota, 11.5, TINTA2)
        if k < 2:
            linea(o, x + bw + 3, y + hmax / 2, x + bw + gap - 3, y + hmax / 2 - dy, TINTA, 1.4, flecha="fl")
    return 24 + 2 * dy + hmax


def fig_peldano(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Esta etapa es un peldaño, un piso o un pozo?",
             "Dos preguntas, cuatro casillas. Y dos escaleras: una real y una a escala de taller.")
    x0, A = L.M, L.A
    if L.ap:
        hm = _matriz(o, x0, L.y, 330)
        y = L.y
        for nombre, pasos in ESCALERAS:
            y += _escalera(o, x0 + 370, y, A - 370, nombre, pasos) + 22
        L.y = max(L.y + hm, y - 22)
    else:
        L.y += _matriz(o, x0, L.y, A) + 26
        for nombre, pasos in ESCALERAS:
            L.y += _escalera(o, x0, L.y, A, nombre, pasos) + 22
        L.y -= 22
    L.pie("No se escala un proyecto: se escala una posición, desde la cual el siguiente arranca más barato.",
          "La pregunta de cada etapa: ¿qué queda instalado cuando termine, que haga más barata la siguiente? "
          "«Más clientes» o «más experiencia» no es un peldaño: es un piso.",
          "La escalera de SpaceX resume la Parte 2; la del taller es ilustrativa.")
    return L.svg("Peldaño, piso y pozo",
                 "Matriz de dos por dos: vende hoy y abarata la siguiente es peldaño; sólo vende, piso; sólo abarata, "
                 "pozo; ninguna, cortar. Escaleras: Falcon 1, Falcon 9, Starship y Starlink; y encargo, molde, "
                 "segundo producto en un taller.")


# ---------------------------------------------------------------------------
# Fig. 13 · F-41 · El algoritmo, en los dos órdenes (receta R4)
# ---------------------------------------------------------------------------
SOBRAN = {1, 4, 6, 8}   # índices de los pasos que no deberían existir (ilustrativo)


def fig_algoritmo(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Qué pasa si se automatiza antes de borrar?",
             "Un proceso de diez pasos, de los que cuatro no deberían existir, en los dos órdenes.")
    x0, A = L.M, L.A
    L.par("El orden: 1 cuestionar el requisito → 2 borrar → 3 simplificar → 4 acelerar → 5 automatizar, último.",
          12.5, TINTA2, 600)
    L.y += 16
    gap = 8 if L.ap else 6
    bw = (A - 9 * gap) / 10
    bh = 46
    for fila in ("correcto", "habitual"):
        if fila == "correcto":
            L.par("A · Orden correcto: cuestionar y borrar primero", 14, TINTA, 700)
        else:
            L.par("B · Orden habitual: automatizar lo que existe", 14, TINTA, 700)
        y = L.y + 8
        for i in range(10):
            x = x0 + i * (bw + gap)
            sobra = i in SOBRAN
            if fila == "correcto" and sobra:
                caja(o, x, y, bw, bh, FONDO, TINTA3, 1.2, "4 3", rx=4)
                linea(o, x + bw * 0.3, y + bh * 0.3, x + bw * 0.7, y + bh * 0.7, TINTA3, 1.6)
                linea(o, x + bw * 0.7, y + bh * 0.3, x + bw * 0.3, y + bh * 0.7, TINTA3, 1.6)
            elif fila == "correcto":
                caja(o, x, y, bw, bh, AZUL, rx=4)
            elif sobra:
                o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" '
                         f'fill="url(#rayas)" stroke="{NARANJA}" stroke-width="1.6"/>')
            else:
                caja(o, x, y, bw, bh, NARANJA, rx=4)
            o.append(texto(x + bw / 2, y + bh + 15, i + 1, 11, TINTA3, anc="middle"))
        L.y = y + bh + 24
        nota = ("Quedan 6 pasos, y recién ahí se automatizan. Los 4 borrados (×) ya no cuestan nada."
                if fila == "correcto" else
                "Los 10 automatizados. Los 4 que sobraban (rayados) siguen costando, y ahora nadie los ve.")
        L.par(nota, 12.5, TINTA2)
        L.y += 18
    L.y -= 18
    L.pie("Automatizar lo que había que borrar lo vuelve invisible: el paso sigue costando, pero ya nadie lo mira.",
          "Calibración: si no hace falta volver a agregar al menos el 10 % de lo que se borró, no se borró "
          "suficiente.",
          "Proceso ilustrativo. La regla del 10 % es una heurística de práctica, no un resultado medido.")
    return L.svg("El algoritmo, en los dos órdenes",
                 "Diez pasos: en el orden correcto se borran cuatro y se automatizan seis; en el habitual se "
                 "automatizan los diez, y los cuatro que sobraban quedan escondidos dentro de la automatización.")


# ---------------------------------------------------------------------------
# Fig. 14 · F-32 · El mapa de duplicaciones (§5.1 y §5.2)
# ---------------------------------------------------------------------------
ORDENES = [
    (3, "US$1.000", "trabajo ocasional", "no empezar"),
    (4, "US$10.000", "oficio propio", "el tiempo del dueño"),
    (5, "US$100.000", "negocio chico", "la caja"),
    (6, "US$1 millón", "pequeña empresa", "la calidad delegada"),
    (7, "US$10 millones", "empresa mediana", "el capital de trabajo"),
    (8, "US$100 millones", "empresa grande", "el mercado"),
    (9, "US$1.000 millones", "corporación", "el gobierno interno y la regulación"),
]


def fig_mapa_duplicaciones(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    total = math.log2(10 ** 6)
    L.cabeza("De mil dólares a mil millones por año: ¿cuántas duplicaciones?",
             f"Unas {total:.0f}, no mil: cada orden de magnitud son unas 3,3. Y en cada uno cambia lo que mata.")
    x0, A = L.M, L.A
    if L.ap:
        dmax = 23.9
        X = lambda d: x0 + d / dmax * A
        cw = 3.32 / dmax * A - 6
        dy = 26
        base = L.y + 6 * dy + 120
        # escalera
        d = f"M{X(0):.1f},{base}"
        for k, *_ in ORDENES:
            dd = (k - 3) * math.log2(10)
            yk = base - (k - 3) * dy - 24
            d += f" V{yk:.1f} H{X(min(dd + 3.32, dmax)):.1f}"
        o.append(f'<path d="{d} V{base} Z" fill="{AZUL_SUAVE}" stroke="{AZUL}" stroke-width="1.5"/>')
        for k, fact, que, mata in ORDENES:
            dd = (k - 3) * math.log2(10)
            yk = base - (k - 3) * dy - 24
            xk = X(dd) + 6
            if ancho_txt(f"{pot(k)} · {fact}", 11.5, 700) > X(min(dd + 3.32, dmax)) - xk - 4:
                o.append(texto(xk, yk + 17, f"{pot(k)} ·", 11.5, TINTA, 700))   # escalón angosto: dos renglones
                o.append(texto(xk, yk + 31, fact, 11.5, TINTA, 700))
            else:
                o.append(texto(xk, yk + 17, f"{pot(k)} · {fact}", 11.5, TINTA, 700))
            yt = yk - 8 - alto("mata: " + mata, 11, cw, 600, 1.3) - 15
            o.append(texto(xk, yt, que, 11, TINTA2))
            bloque(o, xk, yt + 4, cw, "mata: " + mata, 11, NARANJA, 600, 1.3)
        linea(o, X(0), base, X(20), base, TINTA3)
        for dd in range(0, 21, 2):
            linea(o, X(dd), base, X(dd), base + 5, TINTA3)
            o.append(texto(X(dd), base + 18, dd, 11, TINTA3, anc="middle"))
        o.append(texto(X(10), base + 36, "duplicaciones desde US$1.000 por año", 11.5, TINTA2, anc="middle"))
        L.y = base + 44
    else:
        y = L.y
        rh = 58
        for k, fact, que, mata in reversed(ORDENES):
            dd = (k - 3) * math.log2(10)
            wbar = 30 + (k - 3) * 9
            caja(o, x0, y + 4, wbar, rh - 12, AZUL_SUAVE, AZUL, 1.2, rx=3)
            o.append(texto(x0 + wbar + 10, y + 18, f"{pot(k)} · {fact} · {que}", 12.5, TINTA, 700))
            o.append(texto(x0 + wbar + 10, y + 35, "mata: " + mata, 12, NARANJA, 600))
            o.append(texto(x0 + wbar + 10, y + 50, f"≈ {coma(dd)} duplicaciones desde la base" if dd else
                           "la base", 11, TINTA3))
            y += rh
        L.y = y
    L.pie(f"Son unas {total:.0f} duplicaciones: es finito y contable. Pero cada una cuesta más que la anterior, "
          "porque en cada orden cambia el cuello de botella.",
          "Quien es excelente en 10⁴ fracasa en 10⁶ haciendo exactamente lo que lo hizo excelente.",
          f"log₂ 10⁶ = {coma(total)}. Lo que mata en cada orden es una heurística [hipótesis]: los modelos de "
          "etapas de crecimiento no tienen confirmación empírica (Levie y Lichtenstein 2010).")
    return L.svg("El mapa de duplicaciones",
                 "Escalera de siete órdenes de magnitud de facturación anual, de mil dólares a mil millones, "
                 "unas veinte duplicaciones en total, con lo que mata al negocio en cada peldaño.")


# ---------------------------------------------------------------------------
# Fig. 15 · F-34 · Una década, dos relojes (§5.3)
# ---------------------------------------------------------------------------
def fig_reloj(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    semanas = 52 * 10
    n_lento, n_rapido = 10 // 3, semanas // 3
    L.cabeza("¿Cuántas veces se puede aprender en una década?",
             "El mismo tiempo y el mismo presupuesto anual, con ciclos de prueba de tres años o de tres semanas.")
    x0, A = L.M, L.A
    lw = 170 if L.ap else 0
    tx0, tx1 = x0 + lw, x0 + A - (110 if L.ap else 0)
    X = lambda anios: tx0 + anios / 10 * (tx1 - tx0)
    y = L.y
    for rot, n, paso, col in (("Ciclo de 3 años", n_lento, 3.0, NARANJA),
                              ("Ciclo de 3 semanas", n_rapido, 3 / 52, AZUL)):
        cuenta = f"{n} pruebas" if n < 10 else f"≈ {round(n, -1):.0f} pruebas"
        if L.ap:
            o.append(texto(x0, y + 26, rot, 14, TINTA, 700))
            o.append(texto(tx1 + 14, y + 26, cuenta, 14, col, 700))
        else:
            o.append(texto(x0, y + 13, rot, 14, TINTA, 700))
            o.append(texto(x0 + A, y + 13, cuenta, 14, col, 700, anc="end"))
            y += 22
        linea(o, tx0, y + 22, tx1, y + 22, GRILLA, 2)
        for i in range(1, n + 1):
            xi = X(i * paso)
            if n < 10:
                o.append(f'<circle cx="{xi:.1f}" cy="{y + 22:.1f}" r="10" fill="{col}" stroke="{FONDO}" stroke-width="2"/>')
            else:
                linea(o, xi, y + 8, xi, y + 36, col, 1.3)
        y += 58
    for a in range(0, 11, 2):
        linea(o, X(a), y - 8, X(a), y - 3, TINTA3)
        o.append(texto(X(a), y + 10, f"año {a}" if a else "0", 11, TINTA3, anc="middle"))
    L.y = y + 18
    L.pie(f"Mismo tiempo: {n_lento} pruebas contra unas {round(n_rapido, -1):.0f}. Romper prototipos baratos es "
          "comprar ciclos.",
          "progreso = aprendizaje por ciclo × ciclos por unidad de tiempo. Subir lo primero suele ser caro; "
          "subir lo segundo suele ser una decisión de diseño, y barata.",
          f"Una década son {semanas} semanas: {semanas} ÷ 3 ≈ {n_rapido}. Supone el mismo aprendizaje por prueba; "
          "un ciclo corto suele enseñar menos cada vez, y por eso hay que medir los dos factores.")
    return L.svg("Una década, dos relojes",
                 "Dos líneas de tiempo de diez años: con ciclos de tres años caben 3 pruebas; con ciclos de tres "
                 "semanas, unas 170.")


# ---------------------------------------------------------------------------
# Fig. 16 · F-35 · La regla del segundo (§5.4)
# ---------------------------------------------------------------------------
def fig_segundos(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    dias = 1e6 / 86400
    anios = 1e9 / (365.25 * 86400)
    L.cabeza("¿Cuánto es un millón de segundos? ¿Y mil millones?",
             "Las dos barras están a la misma escala: la de mil millones ocupa todo el ancho.")
    x0, A = L.M, L.A
    y = L.y
    hb = 30
    o.append(texto(x0, y + 14, "Un millón de segundos", 14, TINTA, 700))
    o.append(texto(x0 + A, y + 14, f"{coma(dias)} días", 14, AZUL, 700, anc="end"))
    y += 24
    w1 = A / 1000
    o.append(barra(x0, y, max(w1, 1.2), hb, "lleno_azul"))
    linea(o, x0 + 6, y + hb / 2, x0 + 40, y + hb / 2, TINTA, 1.2)
    bloque(o, x0 + 46, y + hb / 2 - 9, A - 46,
           "esta rayita: la milésima parte de la barra de abajo", 12.5, TINTA, 600)
    y += hb + 30
    o.append(texto(x0, y + 14, "Mil millones de segundos", 14, TINTA, 700))
    o.append(texto(x0 + A, y + 14, f"{coma(anios)} años", 14, NARANJA, 700, anc="end"))
    y += 24
    o.append(barra(x0, y, A, hb, "lleno"))
    for a in range(0, 31, 5):
        xa = x0 + a / anios * A
        linea(o, xa, y + hb, xa, y + hb + 5, TINTA3)
        o.append(texto(xa, y + hb + 18, f"{a} años" if a in (10, 20, 30) else ("0" if a == 0 else ""), 11, TINTA3,
                       anc="middle"))
    L.y = y + hb + 24
    L.pie("Mismo prefijo, y son once días contra treinta y dos años.",
          "Si un millón de segundos fuera 1 centímetro, mil millones serían 10 metros. Al comparar millones con "
          "miles de millones —presupuestos, patrimonios, deudas— la intuición verbal no sirve.",
          f"10⁶ s ÷ 86.400 s por día = {coma(dias)} días; 10⁹ s ÷ 31.557.600 s por año = {coma(anios)} años.")
    return L.svg("La regla del segundo",
                 "Un millón de segundos son 11,6 días, una rayita casi invisible; mil millones son 31,7 años, "
                 "una barra que ocupa todo el ancho.")


# ---------------------------------------------------------------------------
# Fig. 17 · F-7 · La fortuna es un producto (§8.1 y §8.4)
# ---------------------------------------------------------------------------
FACTORES = [  # nombre, qué hacer (§8.4), depende de la persona, valor A, valor B (ilustrativos)
    ("Habilidad operativa", "se enseña como procedimiento: este libro", True, 0.9, 0.9),
    ("Capital inicial", "no se enseña: fija el punto de partida, no la pendiente", False, 0.6, 0.6),
    ("Apoyo externo al riesgo", "contratos, créditos, compras públicas", True, 0.7, 0.7),
    ("Supervivencia a eventos de todo o nada", "no se enseña; se administra: acotar la apuesta", False, 0.8, 0.0),
    ("El momento del mercado", "no se enseña; no estorbar: no vender en pánico ni apostar todo en un pico",
     False, 0.7, 0.7),
]


def fig_fortuna_producto(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("«Trabajó duro y con inteligencia»: ¿cuánto explica?",
             "El resultado es un producto de cinco factores, no una suma. Tres no dependen de la persona.")
    x0, A = L.M, L.A
    if L.ap:
        nw, bw, gx = 330, 190, 40
        xa, xb = x0 + nw + 30, x0 + nw + 30 + bw + gx
    else:
        nw, bw, gx = A, (A - 60) / 2, 36
        xa, xb = x0 + 24, x0 + 24 + bw + gx
    y = L.y
    o.append(texto(xa, y + 12, "Una trayectoria", 12.5, TINTA2, 700))
    o.append(texto(xb, y + 12, "La misma, con un evento perdido", 12.5, TINTA2, 700))
    y += 24
    pa = pb = 1.0
    for i, (nom, que, dep, va, vb) in enumerate(FACTORES):
        pa *= va
        pb *= vb
        if L.ap:
            hn = 18 + alto(que, 11.5, nw - 30)
            o.append(texto(x0 + 20, y + 14, nom, 13, TINTA, 700))
            bloque(o, x0 + 20, y + 18, nw - 30, que, 11.5, TINTA2 if dep else TINTA3)
            yb_ = y + 4
            hrow = max(hn, 32) + 12
        else:
            o.append(texto(x0 + 24, y + 14, nom, 13, TINTA, 700))
            yq = bloque(o, x0 + 24, y + 18, A - 24, que, 11.5, TINTA2 if dep else TINTA3)
            yb_ = yq + 4
            hrow = yq - y + 32
        if i:
            o.append(texto(x0 + 2, y + 15, "×", 17, TINTA3, 700))
        for xx, v in ((xa, va), (xb, vb)):
            o.append(f'<rect x="{xx:.1f}" y="{yb_:.1f}" width="{bw:.1f}" height="20" fill="none" '
                     f'stroke="{GRILLA}" stroke-width="1"/>')
            if v > 0:
                o.append(barra(xx, yb_, bw * v, 20, "lleno_azul" if dep else "gris"))
            else:
                o.append(texto(xx + 6, yb_ + 15, "0", 13, NARANJA, 700))
        y += hrow
    y += 4
    linea(o, x0, y, x0 + A, y, TINTA3)
    y += 10
    o.append(texto(x0 + 2, y + 16, "=", 17, TINTA, 700))
    o.append(texto(x0 + 24, y + 16, "Resultado", 14, TINTA, 700))
    yr = y + 26 if not L.ap else y + 2
    o.append(barra(xa, yr, bw * pa, 22, "lleno_azul"))
    o.append(texto(xa + bw * pa + 8, yr + 16, coma(pa, 2), 13, TINTA, 700))
    o.append(f'<rect x="{xb:.1f}" y="{yr:.1f}" width="{bw:.1f}" height="22" fill="none" stroke="{NARANJA}" '
             f'stroke-width="1.5" stroke-dasharray="4 3"/>')
    o.append(texto(xb + 8, yr + 16, "0: todo en cero", 12, NARANJA, 700))
    L.y = yr + 30
    L.pie("«Trabajó duro y con inteligencia» describe una barra de cinco y la presenta como la ecuación entera.",
          "Lo que se puede hacer con las grises: no estorbar al momento del mercado y acotar las apuestas "
          "para que ningún evento único deje un factor en cero.",
          "[hipótesis] Marco para pensar, no modelo estimado: los largos de las barras son ilustrativos y "
          "nadie midió cuánto pesa cada factor. Barras rayadas: lo que no depende de la persona.")
    return L.svg("La fortuna es un producto",
                 "Cinco barras que se multiplican: habilidad operativa, capital inicial, apoyo externo, supervivencia "
                 "a eventos de todo o nada y momento del mercado. Con la supervivencia en cero, el resultado es cero.")


# ---------------------------------------------------------------------------
# Fig. 18 · F-7 · Pendiente y magnitud (§8.5)
# ---------------------------------------------------------------------------
BASE_TALLER, BASE_GRANDE = 10_000, 180e6     # US$; el segundo, reportado
DUPLICA_CADA = 2                             # años (ilustrativo)


def fig_pendiente_magnitud(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    anios = 20
    f = 2 ** (anios / DUPLICA_CADA)
    L.cabeza("¿Qué se copia de una gran fortuna, y qué no?",
             "Dos puntos de partida con la misma pendiente, en escala logarítmica: cada marca vale mil veces "
             "la anterior.")
    x0, A = L.M, L.A
    top = L.y + 10
    hg = 280 if L.ap else 320
    bot = top + hg
    px0, px1 = x0 + 92, x0 + A - (150 if L.ap else 70)
    lo, hi = 3, 12
    X = lambda t: px0 + t / anios * (px1 - px0)
    Y = lambda v: bot - (math.log10(v) - lo) / (hi - lo) * (bot - top)
    for k, rot in ((3, "mil"), (6, "un millón"), (9, "mil millones"), (12, "un billón")):
        linea(o, px0, Y(10 ** k), px1, Y(10 ** k), GRILLA)
        o.append(texto(px0 - 8, Y(10 ** k) + 4, rot, 11, TINTA3, anc="end"))
    for t in range(0, anios + 1, 5):
        o.append(texto(X(t), bot + 18, f"año {t}" if t else "0", 11, TINTA3, anc="middle"))
    yc = (top + bot) / 2
    o.append(texto(x0 + 4, yc, "dólares (escala logarítmica)", 11.5, TINTA2, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 4} {yc})"'))
    for base, col, dash in ((BASE_GRANDE, NARANJA, None), (BASE_TALLER, AZUL, None)):
        linea(o, X(0), Y(base), X(anios), Y(base * f), col, 3, dash)
        o.append(f'<circle cx="{X(0):.1f}" cy="{Y(base):.1f}" r="5" fill="{col}"/>')
    o.append(texto(X(0.4), Y(BASE_GRANDE) + 22, "arranca con ≈ US$180 millones", 12, NARANJA, 700))
    o.append(texto(X(0.4), Y(BASE_GRANDE) + 37, "[reportado]", 11, NARANJA))
    o.append(texto(X(0.4), Y(BASE_TALLER) + 22, "arranca con US$10.000", 12, AZUL, 700))
    fin_g = BASE_GRANDE * f
    fin_t = BASE_TALLER * f
    if L.ap:
        o.append(texto(X(anios) + 10, Y(fin_g) + 4, f"≈ {miles(round(fin_g / 1e9))} mil millones", 12, TINTA, 700))
        o.append(texto(X(anios) + 10, Y(fin_t) + 4, f"≈ {round(fin_t / 1e6)} millones", 12, TINTA, 700))
    # distancia vertical
    tm = 12 if L.ap else 14
    linea(o, X(tm), Y(BASE_TALLER * 2 ** (tm / DUPLICA_CADA)) - 4, X(tm),
          Y(BASE_GRANDE * 2 ** (tm / DUPLICA_CADA)) + 4, TINTA, 1.3, flecha="fl", inicio=True)
    ym = (Y(BASE_TALLER * 2 ** (tm / 2)) + Y(BASE_GRANDE * 2 ** (tm / 2))) / 2
    o.append(texto(X(tm) + 10, ym - 6, f"punto de partida: × {miles(round(BASE_GRANDE / BASE_TALLER))}", 12.5,
                   TINTA, 700))
    o.append(texto(X(tm) + 10, ym + 11, "no se copia", 12.5, NARANJA, 700))
    # pendiente
    ts, tsf = 4, 8
    ya, yb = Y(BASE_TALLER * 2 ** (ts / 2)), Y(BASE_TALLER * 2 ** (tsf / 2))
    o.append(f'<path d="M{X(ts):.1f},{ya:.1f} H{X(tsf):.1f} V{yb:.1f}" fill="none" stroke="{TINTA}" '
             f'stroke-width="1.2" stroke-dasharray="3 2"/>')
    o.append(texto(X(tsf) + 8, ya + 30, f"pendiente: × 2 cada {DUPLICA_CADA} años", 12.5, TINTA, 700))
    o.append(texto(X(tsf) + 8, ya + 47, "se copia", 12.5, AZUL, 700))
    L.y = bot + 36
    L.pie("La parte que se puede enseñar no da la magnitud: da la pendiente.",
          "Las dos líneas son paralelas porque crecen igual. La distancia entre ellas es el punto de partida, "
          "y a escala pequeña la pendiente es lo único que cambia una vida.",
          f"Ilustrativa: las dos se duplican cada {DUPLICA_CADA} años. US$180 millones es lo que se reportó que "
          "Musk obtuvo de la venta de su empresa anterior en 2002 [reportado]; US$10.000, un taller que arranca.")
    return L.svg("Pendiente y magnitud",
                 "Dos rectas paralelas en escala logarítmica, una que arranca en 10.000 dólares y otra en 180 "
                 "millones: la pendiente es la misma y se copia; la distancia es el punto de partida y no se copia.")


# ===========================================================================
# Figuras del libro ilustrado (TAR-0187, 22-oct-2026). Mismas reglas: título-pregunta,
# conclusión al pie, datos calculados acá y el estado de cada número en la condición.
# ===========================================================================
def cuadritos(o, x0, y0, n, cols, lado, sep, estilo):
    """n cuadrados en filas de `cols`; estilo(i) -> (relleno, trazo o None). Devuelve el alto."""
    for i in range(n):
        f, c = divmod(i, cols)
        rel, tr = estilo(i)
        t = f' stroke="{tr}" stroke-width="1"' if tr else ""
        o.append(f'<rect x="{x0 + c * (lado + sep):.1f}" y="{y0 + f * (lado + sep):.1f}" width="{lado}" '
                 f'height="{lado}" rx="1.5" fill="{rel}"{t}/>')
    return math.ceil(n / cols) * (lado + sep) - sep


def punto(o, x, y, r=5, color=AZUL):
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="{FONDO}" stroke-width="2"/>')


def polilinea(o, pts, color, ancho=2.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{ancho}" '
             f'stroke-linejoin="round"{d}/>')


# ---------------------------------------------------------------------------
# F-P3_dos_mecanismos · economía de escala contra curva de aprendizaje (§3.3)
# ---------------------------------------------------------------------------
CF_MES = 10_000                          # costo fijo por mes (ilustrativo)
VENTAS_MES = [2000] * 12 + [1000] * 12   # unidades por mes; en el mes 12 caen a la mitad
HECHAS_ANTES, CV_0, R_APR = 2000, 10.0, 0.20


def costos_por_mes():
    """(costo fijo por unidad, costo variable por unidad) de cada mes. El variable sigue la ley de
    Wright sobre la producción acumulada a mitad de mes."""
    b = -math.log2(1 - R_APR)
    acum, filas = HECHAS_ANTES, []
    for q in VENTAS_MES:
        filas.append((CF_MES / q, CV_0 * ((acum + q / 2) / HECHAS_ANTES) ** (-b)))
        acum += q
    return filas


def fig_dos_mecanismos(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    filas = costos_por_mes()
    q1, q2 = VENTAS_MES[0], VENTAS_MES[-1]
    L.cabeza("¿Qué se pierde si las ventas caen a la mitad?",
             f"Las dos partes del costo de cada unidad, mes a mes, en una fábrica que vende {miles(q1)} unidades "
             f"por mes y desde el mes 12 vende {miles(q2)}.")
    x0, A = L.M, L.A
    px0, px1 = x0 + 28, x0 + A
    X = lambda m: px0 + m / 24 * (px1 - px0)
    y = L.y
    o.append(texto(x0, y + 12, "Ventas por mes", 13, TINTA, 700))
    o.append(texto(X(12) + 8, y + 12, "mes 12: las ventas caen a la mitad", 12.5, NARANJA, 700))
    y += 22
    hv = 32
    for i, q in enumerate(VENTAS_MES):
        h = q / q1 * hv
        caja(o, X(i) + 1.5, y + hv - h, X(1) - X(0) - 3, h, GRIS, rx=1)
    o.append(texto(X(6), y + hv / 2 + 4, f"{miles(q1)} por mes", 12, TINTA, 700, anc="middle"))
    o.append(texto(X(18), y + hv * (1 - q2 / q1 / 2) + 4, miles(q2), 11.5, TINTA, 700, anc="middle"))
    linea(o, X(12), y - 4, X(12), y + hv, NARANJA, 1.2, "4 4")
    y += hv + 26
    hp = 120
    paneles = [
        ("Economía de escala: el costo fijo repartido",
         f"{miles(CF_MES)} por mes ÷ unidades vendidas ese mes. Depende de cuánto se vende hoy.", 0),
        ("Curva de aprendizaje: el costo variable",
         "Baja 20 % cada vez que se duplica lo producido desde el primer día. Depende de todo lo hecho.", 1),
    ]
    for tit, sub, k in paneles:
        o.append(texto(x0, y + 14, tit, 14, TINTA, 700))
        y = bloque(o, x0, y + 21, A, sub, 12, TINTA2) + 10
        top, bot = y, y + hp
        Y = lambda c, top=top: top + hp - c / 12 * hp
        linea(o, px0, Y(0), px1, Y(0), TINTA3, 1.2)
        linea(o, px0, Y(10), px1, Y(10), GRILLA)
        for c in (0, 5, 10):
            linea(o, px0 - 4, Y(c), px0, Y(c), TINTA3)
            o.append(texto(px0 - 7, Y(c) + 4, c, 11, TINTA3, anc="end"))
        linea(o, X(12), top, X(12), bot, NARANJA, 1.2, "4 4")
        serie = [f[k] for f in filas]
        if k == 0:
            linea(o, X(0), Y(serie[0]), X(12), Y(serie[0]), AZUL, 2.5)
            linea(o, X(12), Y(serie[0]), X(12), Y(serie[-1]), NARANJA, 2.5)
            linea(o, X(12), Y(serie[-1]), X(24), Y(serie[-1]), NARANJA, 2.5)
            bloque(o, X(12.6), Y(9.3), px1 - X(12.6),
                   f"De {serie[0]:.0f} a {serie[-1]:.0f} por unidad: se pierde el mismo mes", 12.5, NARANJA, 700)
        else:
            polilinea(o, [(X(0), Y(CV_0))] + [(X(i + 0.5), Y(c)) for i, c in enumerate(serie)], AZUL)
            bloque(o, X(12.6), Y(9.3), px1 - X(12.6),
                   f"De {coma(serie[11])} a {coma(serie[-1])}: lo aprendido queda y sigue bajando", 12.5, AZUL, 700)
        y = bot + 16
    for m in (0, 6, 12, 18, 24):
        o.append(texto(X(m), y + 2, f"{m} meses" if m == 24 else m, 11, TINTA3, anc="end" if m == 24 else "middle"))
    L.y = y + 14
    L.pie("La economía de escala se pierde el mes en que caen las ventas; lo aprendido queda y sigue bajando "
          "el costo.",
          "Son dos mecanismos que se confunden: uno reparte el costo fijo entre lo que se vende hoy; el otro "
          "depende de todo lo que se hizo desde el primer día.",
          f"Números ilustrativos: costo fijo de {miles(CF_MES)} por mes; costo variable de {coma(CV_0, 0)} con "
          f"{miles(HECHAS_ANTES)} unidades hechas, que baja 20 % por duplicación (ley de Wright). Lo aprendido "
          "tampoco es eterno: se desgasta si no se usa y se va con la gente que se va (Argote y Epple 1990).")
    return L.svg("Dos mecanismos que bajan el costo",
                 "Dos paneles con el mismo eje de 24 meses: el costo fijo por unidad salta de 5 a 10 cuando las "
                 "ventas caen a la mitad; el costo variable, que sigue la ley de Wright, sigue bajando.")


# ---------------------------------------------------------------------------
# F-P9_curvas_negocio · en qué negocios la escala abarata la unidad (Parte 9)
# ---------------------------------------------------------------------------
NEGOCIOS = [  # nombre, unidad (tabla de la Parte 9), forma orientativa, veredicto
    ("Programas y contenido", "el usuario o la pieza publicada", "cero", "baja casi a cero"),
    ("Manufactura", "la unidad fabricada", "wright", "baja en cada duplicación"),
    ("Oficio → taller", "la pieza o la instalación", "escalones", "baja en cada rediseño"),
    ("Servicio → producto", "el encargo entregado", "aplana",
     "se aplana; sigue bajando sólo si se vuelve producto (punteada)"),
    ("Comercio y reventa", "la transacción", "leve", "baja poco: el margen lo fija el proveedor"),
    ("Inmuebles", "el metro cuadrado alquilado", "plana", "no baja: escala por capital, no por costo"),
]
REDISENOS = (2, 4.5, 7)   # duplicaciones en que el taller invierte (molde, matriz): ilustrativo


def curva_negocio(forma, k):
    """Costo por unidad, en % del de la primera, tras k duplicaciones (formas orientativas)."""
    if forma == "cero":
        return 98 / 2 ** k + 2
    if forma == "wright":
        return 100 * 0.8 ** k
    if forma == "escalones":
        return 100 * 0.98 ** k * 0.7 ** sum(1 for r in REDISENOS if k >= r)
    if forma == "aplana":
        return 100 * 0.8 ** min(k, 3)
    if forma == "leve":
        return 100 * 0.97 ** k
    return 100.0


def fig_curvas_negocio(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿En qué negocios crecer abarata cada unidad?",
             "Costo por unidad contra producción acumulada, en seis tipos de negocio. En cada recuadro, la línea "
             "de puntos de arriba es el costo de la primera unidad, y cada marca del eje es el doble de la anterior.")
    x0, A = L.M, L.A
    cols = 3 if L.ap else 2
    gap = 26
    cw = (A - gap * (cols - 1)) / cols
    hp, paso_fila = 92, 196
    y0 = L.y
    for i, (nom, uni, forma, ver) in enumerate(NEGOCIOS):
        f, c = divmod(i, cols)
        cx, yb = x0 + c * (cw + gap), y0 + f * paso_fila
        abarata = i < 4
        col = AZUL if abarata else NARANJA
        o.append(texto(cx, yb + 14, nom, 14, TINTA, 700))
        o.append(texto(cx, yb + 32, f"unidad: {uni}", 11.5, TINTA2))
        top = yb + 42
        bot = top + hp
        X = lambda k, cx=cx: cx + 4 + k / 10 * (cw - 8)
        Y = lambda v, bot=bot: bot - v / 108 * hp
        linea(o, X(0), Y(100), X(10), Y(100), TINTA3, 1, "2 3")
        linea(o, cx, top, cx, bot, TINTA3)
        linea(o, cx, bot, cx + cw, bot, TINTA3)
        for k in range(11):
            linea(o, X(k), bot, X(k), bot + 4, TINTA3)
        ks = [j / 20 for j in range(201)]
        if forma == "aplana":
            polilinea(o, [(X(k), Y(100 * 0.8 ** k)) for k in ks if k >= 3], AZUL, 1.6, "2 4")
        polilinea(o, [(X(k), Y(curva_negocio(forma, k))) for k in ks], col, 2.6,
                  None if abarata else "7 5")
        bloque(o, cx, bot + 10, cw, ver, 12, col, 700)
    L.y = y0 + math.ceil(len(NEGOCIOS) / cols) * paso_fila - 14
    L.pie("La escala abarata la unidad donde hay algo que aprender o que repartir: fábricas, programas, oficios "
          "que rediseñan. En inmuebles y en reventa no: ahí se crece para acumular activo, o no se crece.",
          "Aplicar la lógica de Ford o de SpaceX a un negocio de curva plana es el error de dominio más caro de "
          "este libro.",
          "Formas orientativas, dibujadas a partir de la tabla de la Parte 9 [hipótesis]; sólo en manufactura la "
          "evidencia es abundante (Argote y Epple 1990). Cada negocio mide su propia curva con la receta R8.")
    return L.svg("La curva según el negocio",
                 "Seis recuadros con la forma orientativa del costo por unidad contra la producción acumulada: baja "
                 "en programas, manufactura y oficios con rediseño; se aplana en servicios; casi no baja en "
                 "comercio; no baja en inmuebles.")


# ---------------------------------------------------------------------------
# F-G2_espera · al 100 % de ocupación la espera explota (Parte 11, G2)
# ---------------------------------------------------------------------------
VARIAB_BAJA = 0.25   # variabilidad relativa con turnos fijos y tiempos parejos (ilustrativa)


def espera(u, v=1.0):
    """Espera promedio en la cola, en tiempos de atención: v × u ÷ (1 − u) (Kingman 1961)."""
    return v * u / (1 - u)


def fig_espera(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Por qué una agenda llena al 100 % no funciona?",
             "Espera promedio en la cola, contada en tiempos de atención, según la parte de la capacidad que "
             "está ocupada.")
    x0, A = L.M, L.A
    top = L.y + 6
    hg = 290 if L.ap else 320
    bot = top + hg
    px0, px1 = x0 + 34, x0 + A - 8
    WMAX = 20
    X = lambda u: px0 + u * (px1 - px0)
    Y = lambda w: bot - w / WMAX * hg
    for w in (0, 5, 10, 15, 20):
        linea(o, px0, Y(w), px1, Y(w), TINTA3 if w == 0 else GRILLA, 1.2 if w == 0 else 1)
        o.append(texto(px0 - 7, Y(w) + 4, w, 11, TINTA3, anc="end"))
    for u in (0, .2, .4, .6, .8, 1):
        o.append(texto(X(u), bot + 18, f"{u * 100:.0f} %", 11, TINTA3, anc="middle"))
    o.append(texto((px0 + px1) / 2, bot + 36, "ocupación: la parte de la capacidad que está ocupada", 11.5,
                   TINTA2, anc="middle"))
    yc = (top + bot) / 2
    o.append(texto(x0 + 6, yc, "espera, en tiempos de atención", 11.5, TINTA2, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 6} {yc})"'))
    u_max = WMAX / (WMAX + 1)
    polilinea(o, [(X(u), Y(espera(u))) for u in (j / 300 * u_max for j in range(301))], AZUL, 2.8)
    u_max_b = WMAX / (WMAX + VARIAB_BAJA)
    polilinea(o, [(X(u), Y(espera(u, VARIAB_BAJA))) for u in (j / 300 * u_max_b for j in range(301))],
              TINTA2, 2, "7 5")
    for u in (0.80, 0.90, 0.95):
        w = espera(u)
        punto(o, X(u), Y(w), 5.5)
        o.append(texto(X(u) - 11, Y(w) + 5, f"{u * 100:.0f} % → {w:.0f}", 13.5, TINTA, 700, anc="end"))
    o.append(texto(px0 + 10, Y(18.6), "— pedidos que llegan al azar", 12.5, AZUL, 700))
    o.append(texto(px0 + 10, Y(18.6) + 19, "- - turnos fijos y tiempos parejos", 12.5, TINTA2, 700))
    yb = bot + 50
    linea(o, X(0.85), yb, X(1), yb, NARANJA, 1.4)
    for u in (0.85, 1):
        linea(o, X(u), yb - 5, X(u), yb + 5, NARANJA, 1.4)
    o.append(texto(px1, yb + 20, "hospitales: desde el 85 % de camas ocupadas, riesgo de no poder internar",
                   11.5, NARANJA, 600, anc="end"))
    L.y = yb + 30
    L.pie("Del 80 % al 90 % de ocupación, la espera pasa de 4 a 9 tiempos de atención; al 95 %, a 19. Hay que "
          "dejar capacidad libre a propósito.",
          "Si atender un pedido lleva un día y la agenda está al 90 %, el pedido espera nueve días antes de que "
          "alguien lo toque.",
          "Curva ocupación ÷ (1 − ocupación), para llegadas y tiempos al azar (Kingman 1961). La fórmula también "
          "multiplica por la variabilidad: con turnos fijos y tiempos parejos se puede trabajar más cerca del "
          "100 % (la línea de trazos usa una variabilidad cuatro veces menor, ilustrativa). Hospitales: Bagust, "
          "Place y Posnett, BMJ 1999 [verificado, secundaria].")
    return L.svg("Al 100 % la espera explota",
                 "Curva de espera contra ocupación: 4 tiempos de atención al 80 %, 9 al 90 % y 19 al 95 %; con "
                 "menos variabilidad la curva sube mucho más tarde.")


# ---------------------------------------------------------------------------
# F-E2_brooks · los canales de coordinación crecen con el cuadrado (Parte 11, E2)
# ---------------------------------------------------------------------------
EQUIPOS = (3, 5, 10, 20)


def fig_brooks(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Por qué sumar gente a un proyecto atrasado lo atrasa más?",
             "Cada punto es una persona, y cada línea, un canal posible de coordinación: con n personas hay "
             "n × (n − 1) ÷ 2 canales.")
    x0, A = L.M, L.A
    cols = 4 if L.ap else 2
    cw = A / cols
    R = 74 if L.ap else 92
    paso = 2 * R + 84
    y = L.y + 8
    for i, n in enumerate(EQUIPOS):
        f, c = divmod(i, cols)
        cx, cy = x0 + cw * (c + 0.5), y + f * paso + R
        pts = [(cx + R * math.sin(2 * math.pi * j / n), cy - R * math.cos(2 * math.pi * j / n))
               for j in range(n)]
        aw = 1.5 if n <= 5 else (1.0 if n <= 10 else 0.55)
        for a in range(n):
            for b in range(a + 1, n):
                linea(o, pts[a][0], pts[a][1], pts[b][0], pts[b][1], TINTA3, aw)
        for px, py in pts:
            punto(o, px, py, 7 if n <= 10 else 5)
        o.append(texto(cx, cy + R + 30, f"{n} personas", 14, TINTA, 700, anc="middle"))
        o.append(texto(cx, cy + R + 50, f"{n * (n - 1) // 2} canales", 14,
                       NARANJA if n == EQUIPOS[-1] else AZUL, 700, anc="middle"))
    L.y = y + math.ceil(len(EQUIPOS) / cols) * paso - 18
    L.pie("Al duplicar el equipo, los canales se multiplican por más de cuatro: de 5 personas a 10, de 10 "
          "canales a 45; con 20, son 190.",
          "Los que llegan tarde tienen que aprender, y cada uno agrega canales. Por eso sumar gente al final de un "
          "proyecto atrasado lo atrasa más (Brooks 1975).",
          "Son canales posibles, no obligatorios: un equipo bien partido usa muchos menos. Brooks la llamó «una "
          "simplificación escandalosa»: al principio, en tareas que se dividen, sumar gente acorta (McConnell 1999).")
    return L.svg("La ley de Brooks",
                 "Cuatro grafos completos: 3 personas tienen 3 canales; 5 tienen 10; 10 tienen 45; 20 tienen 190.")


# ---------------------------------------------------------------------------
# F-D3_proyectos · de cada mil proyectos grandes, cuántos cumplen (Parte 11, D3)
# ---------------------------------------------------------------------------
FLYV_COSTO_PLAZO, FLYV_TRES = 85, 5   # de cada 1.000: 8,5 % y 0,5 % (Flyvbjerg y Gardner 2023)


def fig_proyectos(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("De cada mil proyectos grandes, ¿cuántos cumplen lo que prometieron?",
             "Cada cuadrado es un proyecto, en la proporción de la base de Bent Flyvbjerg, de más de 16.000 "
             "proyectos.")
    x0, A = L.M, L.A
    cols, lado, sep = (50, 13, 3) if L.ap else (40, 10, 3)
    paso = lado + sep
    xc = lambda i: x0 + (i % cols) * paso + lado / 2
    y = L.y
    i80 = 30
    solo_plazo = FLYV_COSTO_PLAZO - FLYV_TRES
    o.append(texto(xc(i80) - 7, y + 13, f"{solo_plazo} cumplen costo y plazo, pero no el beneficio", 12.5, AZUL,
                   700, anc="end"))
    o.append(texto(x0, y + 33, f"{FLYV_TRES} cumplen las tres cosas: costo, plazo y beneficio", 12.5, TINTA, 700))
    gy = y + 48
    linea(o, xc(i80), y + 8, xc(i80), gy - 2, AZUL, 1.2)
    linea(o, xc(2), y + 38, xc(2), gy - 2, TINTA, 1.2)

    def estilo(i):
        if i < FLYV_TRES:
            return AZUL, None
        if i < FLYV_COSTO_PLAZO:
            return AZUL_SUAVE, AZUL
        return GRIS_SUAVE, None
    h = cuadritos(o, x0, gy, 1000, cols, lado, sep, estilo)
    o.append(texto(x0, gy + h + 22, f"Los otros {1000 - FLYV_COSTO_PLAZO} se pasan de costo, de plazo o de los dos",
                   13, TINTA2, 700))
    L.y = gy + h + 30
    L.pie(f"Sólo {FLYV_COSTO_PLAZO} de cada 1.000 cumplen costo y plazo, y sólo {FLYV_TRES} cumplen además el "
          "beneficio prometido.",
          "Por eso se estima mirando cómo terminaron los proyectos parecidos, no desmenuzando el propio.",
          "Flyvbjerg y Gardner 2023: 8,5 % y 0,5 % [verificado, secundaria]. La vista desde afuera es la base, no "
          "el techo: si el proyecto cambia la forma de hacer las cosas, los parecidos lo sobreestiman (la NASA "
          "estimó el Falcon 9 en US$3.977 millones; SpaceX declaró unos 300).")
    return L.svg("De mil proyectos, cinco",
                 "Mil cuadrados: 5 proyectos cumplen costo, plazo y beneficio; 80 más cumplen costo y plazo; los "
                 "otros 915 se pasan de costo, de plazo o de los dos.")


# ---------------------------------------------------------------------------
# F-R11_ciclo_caja · el ciclo de caja multiplica el signo del crecimiento (R11 y §2.4)
# ---------------------------------------------------------------------------
CICLOS = [  # rótulo, eventos (día, texto), tramo con la plata afuera o a favor, días (signo de la caja)
    ("A · Paga al contado, vende a los 30 días y cobra a 30 días", [(0, "paga"), (30, "vende"), (60, "cobra")],
     (0, 60), -60),
    ("B · Cobra en el acto y le paga al proveedor a 45 días", [(0, "compra"), (15, "vende y cobra"), (45, "paga")],
     (15, 45), +30),
]
VENTAS_MAX = 100_000


def fig_ciclo_caja(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Vender más trae caja o se la lleva?",
             "Dos comercios que venden lo mismo: uno paga antes de cobrar y el otro cobra antes de pagar.")
    x0, A = L.M, L.A
    T = lambda d: x0 + d / 60 * A
    y = L.y
    for rot, eventos, (d0, d1), dias in CICLOS:
        col = NARANJA if dias < 0 else AZUL
        y = bloque(o, x0, y, A, rot, 13.5, TINTA, 700) + 18
        linea(o, T(0), y + 8, T(60), y + 8, GRILLA, 2)
        for j, (d, s) in enumerate(eventos):
            anc = "start" if j == 0 else ("end" if d == 60 else "middle")
            o.append(texto(T(d), y - 2, s, 12, TINTA2, 600, anc=anc))
            punto(o, T(d), y + 8, 5, TINTA)
        o.append(barra(T(d0), y + 18, T(d1) - T(d0), 14, "rayado" if dias < 0 else "lleno_azul"))
        etq = (f"{-dias} días con la plata propia afuera" if dias < 0
               else f"{dias} días con la plata del cliente en la caja")
        o.append(texto(T(d0), y + 50, etq, 12.5, col, 700))
        y += 70
    for d in (0, 15, 30, 45, 60):
        linea(o, T(d), y - 6, T(d), y - 1, TINTA3)
        o.append(texto(T(d), y + 12, f"día {d}" if d else "día 0", 11, TINTA3,
                       anc="start" if d == 0 else ("end" if d == 60 else "middle")))
    y += 36
    o.append(texto(x0, y + 4, "La caja según cuánto se vende por mes", 13.5, TINTA, 700))
    top = y + 22
    hg = 200 if L.ap else 220
    bot = top + hg
    px0, px1 = x0 + 64, x0 + A - (205 if L.ap else 6)
    X = lambda v: px0 + v / VENTAS_MAX * (px1 - px0)
    Y = lambda d: top + (100_000 - d) / 300_000 * hg
    for d in (100_000, 0, -100_000, -200_000):
        linea(o, px0, Y(d), px1, Y(d), TINTA3 if d == 0 else GRILLA, 1.2 if d == 0 else 1)
        s = ("+" if d > 0 else ("−" if d < 0 else "")) + miles(abs(d))
        o.append(texto(px0 - 7, Y(d) + 4, s, 11, TINTA3, anc="end"))
    for v in (0, 25_000, 50_000, 75_000, 100_000):
        o.append(texto(X(v), bot + 18, miles(v), 11, TINTA3, anc="middle"))
    o.append(texto((px0 + px1) / 2, bot + 36, "ventas por mes", 11.5, TINTA2, anc="middle"))
    yc = (top + bot) / 2
    o.append(texto(x0 + 6, yc, "caja a favor (+) o atrapada (−)", 11.5, TINTA2, anc="middle",
                   extra=f'transform="rotate(-90 {x0 + 6} {yc})"'))
    finales = {}
    for rot, _, _, dias in CICLOS:
        fin = VENTAS_MAX * dias / 30
        finales[dias > 0] = fin
        linea(o, X(0), Y(0), X(VENTAS_MAX), Y(fin), AZUL if dias > 0 else NARANJA, 2.6,
              None if dias > 0 else "8 5")
    b, a = finales[True], finales[False]
    if L.ap:
        o.append(texto(px1 + 12, Y(b) + 5, "B: cada venta de más trae caja", 12.5, AZUL, 700))
        o.append(texto(px1 + 12, Y(b) + 22, f"+{miles(int(b))} con {miles(VENTAS_MAX)} al mes", 11.5, TINTA2))
        o.append(texto(px1 + 12, Y(a) - 38, "A: cada venta de más", 12.5, NARANJA, 700))
        o.append(texto(px1 + 12, Y(a) - 21, "atrapa caja", 12.5, NARANJA, 700))
        o.append(texto(px1 + 12, Y(a) - 4, f"−{miles(int(-a))} con {miles(VENTAS_MAX)} al mes", 11.5, TINTA2))
    else:   # rótulos abajo a la izquierda, donde no pasa ninguna recta
        o.append(texto(px0 + 8, Y(-128_000), f"— B: cobra antes de pagar: +{miles(int(b))}", 12.5, AZUL, 700))
        o.append(texto(px0 + 8, Y(-128_000) + 18, f"- - A: paga antes de cobrar: −{miles(int(-a))}", 12.5,
                       NARANJA, 700))
        o.append(texto(px0 + 8, Y(-128_000) + 36, f"con ventas de {miles(VENTAS_MAX)} al mes", 11.5, TINTA2))
    L.y = bot + 46
    L.pie("Con ciclo de caja positivo, cada venta de más atrapa dinero; con ciclo negativo, cada venta de más lo "
          "trae. Cobrar antes de pagar financia el crecimiento sin pedir prestado.",
          "Es lo que hace Amazon: el cliente paga al comprar y el proveedor cobra semanas después.",
          "Números ilustrativos. Caja atrapada ≈ ventas por día × días entre pagarle al proveedor y cobrarle al "
          "cliente; si se cobra antes de pagar, el signo se invierte. Se ignora el margen.")
    return L.svg("El ciclo de caja",
                 "Arriba, dos líneas de tiempo: A tiene la plata afuera 60 días; B tiene la del cliente 30 días. "
                 "Abajo, la caja contra las ventas: A atrapa 200.000 con ventas de 100.000 al mes; B junta 100.000.")


# ---------------------------------------------------------------------------
# F-P1_suma_producto · las seis funciones se multiplican, no se suman (§1.1)
# ---------------------------------------------------------------------------
FUNCIONES = [  # función (tabla de §1.1), puntaje de A, puntaje de B: de 0 a 10, ilustrativos
    ("Entender al cliente", 10, 6),
    ("Definir el producto", 10, 6),
    ("Producir con calidad", 10, 6),
    ("Vender y distribuir", 0, 6),
    ("Financiar y sobrevivir", 10, 6),
    ("Organizar y aprender", 10, 6),
]


def fig_suma_producto(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Gana la empresa brillante con un hueco o la pareja?",
             "Seis funciones puntuadas de 0 a 10. En una suma, lo que sobra de una compensa lo que falta de otra; "
             "en un producto, no.")
    x0, A = L.M, L.A
    if L.ap:
        bw, gx, xa = 200, 70, x0 + 270
    else:
        gx = 40
        bw = (A - 24 - gx - 30) / 2      # 30: lugar para el número después de la barra
        xa = x0 + 24
    xb = xa + bw + gx
    y = L.y
    o.append(texto(xa, y + 13, "A · diez en cinco, cero en una", 13, TINTA, 700))
    o.append(texto(xb, y + 13, "B · seis en las seis", 13, TINTA, 700))
    y += 28
    suma, prod = [0, 0], [1, 1]
    for i, (nom, va, vb) in enumerate(FUNCIONES):
        if L.ap:
            o.append(texto(x0 + 22, y + 15, nom, 13, TINTA, 600))
            yb_, hrow = y, 32
        else:
            o.append(texto(x0 + 24, y + 13, nom, 12.5, TINTA, 600))
            yb_, hrow = y + 19, 47
        if i:
            o.append(texto(x0 + 2, y + 16, "×", 17, TINTA3, 700))
        for j, (xx, v) in enumerate(((xa, va), (xb, vb))):
            suma[j] += v
            prod[j] *= v
            o.append(f'<rect x="{xx:.1f}" y="{yb_:.1f}" width="{bw:.1f}" height="20" fill="none" '
                     f'stroke="{GRILLA}" stroke-width="1"/>')
            if v > 0:
                o.append(barra(xx, yb_, bw * v / 10, 20, "lleno_azul"))
                o.append(texto(xx + bw * v / 10 + 6, yb_ + 15, v, 12.5, TINTA2, 700))
            else:
                o.append(texto(xx + 6, yb_ + 15, "0", 13, NARANJA, 700))
        y += hrow
    y += 4
    linea(o, x0, y, x0 + A, y, TINTA3)
    y += 10
    filas = [("Sumadas", (f"{suma[0]} · gana", TINTA2), (f"{suma[1]}", TINTA2)),
             ("Multiplicadas", ("0 · todo en cero", NARANJA), (f"{miles(prod[1])} · gana", AZUL))]
    for rot, (sa, ca), (sb, cb) in filas:
        if L.ap:
            o.append(texto(x0 + 22, y + 19, rot, 14, TINTA, 700))
            yv = y + 20
        else:
            o.append(texto(x0 + 24, y + 15, rot, 13.5, TINTA, 700))
            yv = y + 40
        o.append(texto(xa, yv, sa, 17, ca, 700))
        o.append(texto(xb, yv, sb, 17, cb, 700))
        y = yv + 14
    assert prod[0] == 0 and prod[1] > 0 and suma[0] > suma[1]
    L.y = y
    L.pie(f"Sumadas, gana la brillante: {suma[0]} contra {suma[1]}. Multiplicadas, gana la pareja: un solo cero "
          "deja todo en cero.",
          "Por eso la pregunta útil no es quién tuvo más mérito, sino qué función está en cero en este negocio y "
          "quién la va a cubrir.",
          "Puntajes ilustrativos. Las seis funciones son una agrupación didáctica [hipótesis], y que el resultado "
          "sea un producto es un supuesto de modelo, con antecedentes: Kremer (1993), la producción en la que una "
          "sola tarea mal hecha arruina el conjunto.")
    return L.svg("Un producto, no una suma",
                 "Seis funciones: A tiene 10 en cinco y 0 en vender; B tiene 6 en las seis. Sumadas gana A, 50 a 36; "
                 "multiplicadas gana B, 46.656 a 0.")


# ---------------------------------------------------------------------------
# F-P2_ford_linea · la línea de montaje móvil (§2.1, Ford)
# ---------------------------------------------------------------------------
FORD_MIN_ANTES, FORD_MIN_LINEA = 750, 93    # armado del chasis, en minutos (Hounshell 1984)
FORD_PRECIO = [("1908", 850), ("1924-25, la versión más barata", 260)]   # US$ de cada año


def fig_ford_linea(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Cuánto rindió la línea de montaje móvil de Ford?",
             "Arriba, las mismas 12 horas y media de trabajo, antes y después de la línea (1913). Abajo, el precio "
             "del Modelo T.")
    x0, A = L.M, L.A
    T = lambda m: x0 + m / FORD_MIN_ANTES * A
    n = FORD_MIN_ANTES // FORD_MIN_LINEA
    y = L.y
    o.append(texto(x0, y + 13, "Antes de la línea: 1 chasis en 12 horas y media", 13.5, TINTA, 700))
    y += 22
    o.append(barra(x0, y, A, 26, "gris"))
    y += 52
    o.append(texto(x0, y + 13, f"Con la línea móvil: {n} chasis, de {FORD_MIN_LINEA} minutos cada uno", 13.5,
                   AZUL, 700))
    y += 22
    for k in range(n):
        xa, xb = T(k * FORD_MIN_LINEA), T((k + 1) * FORD_MIN_LINEA)
        o.append(barra(xa + 1, y, xb - xa - 2, 26, "lleno_azul"))
        o.append(texto((xa + xb) / 2, y + 18, k + 1, 13, FONDO, 700, anc="middle"))
    y += 26
    for h in range(0, 11, 2):
        linea(o, T(h * 60), y + 4, T(h * 60), y + 9, TINTA3)
        o.append(texto(T(h * 60), y + 22, f"{h} h", 11, TINTA3, anc="start" if h == 0 else "middle"))
    linea(o, T(FORD_MIN_ANTES), y + 4, T(FORD_MIN_ANTES), y + 9, TINTA3)
    o.append(texto(T(FORD_MIN_ANTES), y + 22, "12 h 30", 11, TINTA3, anc="end"))
    y += 52
    o.append(texto(x0, y + 4, "Precio del Modelo T, en dólares de cada año", 13.5, TINTA, 700))
    y += 16
    pw = A - (190 if L.ap else 150)
    p0 = FORD_PRECIO[0][1]
    for (rot, p), trazo in zip(FORD_PRECIO, ("gris", "lleno_azul")):
        o.append(texto(x0, y + 12, rot, 12, TINTA2, 600))
        y += 18
        o.append(barra(x0, y, pw * p / p0, 22, trazo))
        etq = f"US${miles(p)}" + ("" if p == p0 else " · menos de un tercio")
        o.append(texto(x0 + pw * p / p0 + 8, y + 16, etq, 13.5, TINTA if p == p0 else AZUL, 700))
        y += 34
    assert n == 8 and FORD_PRECIO[1][1] * 3 < p0
    L.y = y
    L.pie(f"En las 12 horas y media que llevaba armar un chasis, la línea móvil armaba {n}; el Modelo T bajó de "
          f"US${miles(p0)} a US${miles(FORD_PRECIO[1][1])}.",
          "Se fabricaron unos 15 millones de Modelos T.",
          f"Armado del chasis: de 12 h 30 a {FORD_MIN_LINEA} minutos (Hounshell 1984) [reportado]. Precio de la "
          "versión más barata, en dólares de cada año, sin ajustar por inflación [reportado]. Los ocho chasis de "
          f"{FORD_MIN_LINEA} minutos suman {n * FORD_MIN_LINEA} de los {FORD_MIN_ANTES} minutos.")
    return L.svg("La línea de Ford",
                 "Arriba, una barra de 12 h 30 con un chasis antes de la línea y ocho bloques de 93 minutos con la "
                 "línea. Abajo, el precio del Modelo T: US$850 en 1908 y US$260 en 1924-25.")


# ---------------------------------------------------------------------------
# F-P2_nummi · misma gente, otro sistema (§2.2, NUMMI)
# ---------------------------------------------------------------------------
def persona(o, cx, y, s, fill, stroke="none", dash=None):
    """Figura de una persona de alto s; cx es el centro."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    sw = 1.4 if stroke != "none" else 0
    o.append(f'<circle cx="{cx:.1f}" cy="{y + 0.17 * s:.1f}" r="{0.15 * s:.1f}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="{sw}"{d}/>')
    o.append(f'<rect x="{cx - 0.28 * s:.1f}" y="{y + 0.38 * s:.1f}" width="{0.56 * s:.1f}" '
             f'height="{0.6 * s:.1f}" rx="{0.22 * s:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


NUMMI = [  # panel, faltan de cada 100 (mínimo, máximo), color de los presentes, renglones
    ("Fremont (General Motors), 1982", (20, 25), GRIS,
     [("faltan 20 a 25 de cada 100", NARANJA, 700), ("más de 700 reclamos gremiales pendientes", TINTA2, 400),
      ("calidad: de las peores de GM", TINTA2, 400)]),
    ("NUMMI (GM con Toyota), al año de reabrir", (2, 2), AZUL,
     [("faltan 2 de cada 100", AZUL, 700), ("85 de cada 100 venían de Fremont", TINTA2, 400),
      ("calidad: de las mejores de GM", TINTA2, 400)]),
]


def fig_nummi(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Qué cambia si se cambia el sistema y no la gente?",
             "La planta de General Motors en Fremont (California), antes y después de reabrir con Toyota. Cada "
             "figura es 1 de cada 100 trabajadores; las huecas, los que faltan.")
    x0, A = L.M, L.A
    cw, ch, s = (26, 31, 26) if L.ap else (24, 28, 24)
    gw = 10 * cw
    y = L.y
    ybajo = y
    for p, (rot, (fmin, fmax), col, renglones) in enumerate(NUMMI):
        if L.ap:
            px, py, pw = x0 + p * (A / 2 + 20), y, A / 2 - 20
        else:
            px, py, pw = x0, ybajo, A
        gy = bloque(o, px, py, pw, rot, 13.5, TINTA, 700) + 8
        for i in range(100):
            r, c = divmod(i, 10)
            cx, yy = px + c * cw + cw / 2, gy + r * ch
            if i >= 100 - fmin:
                persona(o, cx, yy, s, FONDO, NARANJA)
            elif i >= 100 - fmax:
                persona(o, cx, yy, s, FONDO, NARANJA, "2 2")
            else:
                persona(o, cx, yy, s, col)
        if L.ap:
            ty = gy + 10 * ch + 6
            for t, c_, peso in renglones:
                ty = bloque(o, px, ty, pw, t, 12.5, c_, peso) + 2
            ybajo = max(ybajo, ty)
        else:
            ty = gy + 4
            for t, c_, peso in renglones:
                ty = bloque(o, px + gw + 18, ty, A - gw - 18, t, 12.5, c_, peso) + 6
            ybajo = max(ty, gy + 10 * ch) + 22
    L.y = ybajo + (4 if L.ap else -14)
    L.pie("Con 85 de cada 100 trabajadores de antes y el sistema de Toyota, el ausentismo bajó de 20-25 % a 2 % "
          "en un año.",
          "General Motors tuvo ese ejemplo adentro 25 años y no logró copiarlo en sus otras plantas: transmitir un "
          "método puede fallar incluso dentro de una misma empresa.",
          "[reportado — Lean Enterprise Institute; Adler 1993; Krafcik 1988; Shook 2010]. Antes, el ausentismo es "
          "un rango: las 5 figuras de trazos marcan la diferencia entre 20 y 25. La planta cerró en 2010 y ese "
          "año la compró Tesla.")
    return L.svg("Misma gente, otro sistema",
                 "Dos grillas de 100 trabajadores: en Fremont, 1982, faltan entre 20 y 25; en NUMMI, al año de "
                 "reabrir con el 85 % de la misma gente, faltan 2.")


# ---------------------------------------------------------------------------
# F-B4_contenedor · cambiar la unidad que se manipula (Parte 11, B4)
# ---------------------------------------------------------------------------
CARGA_SUELTA, CARGA_CAJA = 5.83, 0.158    # US$ por tonelada cargada, 1956 (Levinson 2006)


def tonelada_suelta(o, x, y, s):
    """Una tonelada de carga suelta: bultos de varios tamaños."""
    for a, b, w, h in ((0, .45, .5, .55), (.52, .55, .48, .45), (.08, 0, .4, .43), (.5, .12, .36, .4)):
        o.append(f'<rect x="{x + a * s:.1f}" y="{y + b * s:.1f}" width="{w * s:.1f}" height="{h * s:.1f}" rx="2" '
                 f'fill="{GRIS_SUAVE}" stroke="{TINTA3}" stroke-width="1.2"/>')


def tonelada_caja(o, x, y, s):
    """Una tonelada en caja: el contenedor visto de costado."""
    o.append(f'<rect x="{x:.1f}" y="{y + .22 * s:.1f}" width="{s:.1f}" height="{.56 * s:.1f}" rx="2" '
             f'fill="{AZUL}"/>')
    for k in range(1, 5):
        linea(o, x + k * s / 5, y + .3 * s, x + k * s / 5, y + .7 * s, AZUL_SUAVE, 1)


def fig_contenedor(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Cuánto abarató el contenedor la carga de un barco?",
             f"Lo que se podía cargar con US${coma(CARGA_SUELTA, 2)} en 1956: suelto, o en las cajas del Ideal X "
             "de Malcom McLean. Cada bloque es una tonelada.")
    x0, A = L.M, L.A
    cols = 20 if L.ap else 12
    paso = A / cols
    s = paso - 7
    n = round(CARGA_SUELTA / CARGA_CAJA)
    y = L.y
    o.append(texto(x0, y + 13, f"Carga suelta: US${coma(CARGA_SUELTA, 2)} por tonelada", 13.5, TINTA, 700))
    y += 24
    tonelada_suelta(o, x0, y, s)
    o.append(texto(x0 + paso + 4, y + s / 2 + 5, "1 tonelada", 13, TINTA2, 700))
    y += s + 28
    o.append(texto(x0, y + 13, f"En cajas, en el Ideal X: {coma(CARGA_CAJA * 100, 1)} centavos por tonelada",
                   13.5, AZUL, 700))
    y += 24
    for i in range(n):
        r, c = divmod(i, cols)
        tonelada_caja(o, x0 + c * paso, y + r * paso, s)
    filas = math.ceil(n / cols)
    ult = n - (filas - 1) * cols
    o.append(texto(x0 + ult * paso + 4, y + (filas - 1) * paso + s / 2 + 5, f"{n} toneladas", 13, AZUL, 700))
    assert n == 37
    L.y = y + filas * paso
    L.pie(f"Con lo que costaba cargar una tonelada suelta, el Ideal X cargó {n}. McLean no inventó una máquina: "
          "cambió la unidad que se manipula.",
          "Cuando el costo está en manipular la carga y no en transportarla, no se optimiza la manipulación: se "
          "cambia la unidad.",
          f"Costo de cargar, 1956, en dólares de ese año: US${coma(CARGA_SUELTA, 2)} por tonelada suelta en un "
          f"barco mediano; {coma(CARGA_CAJA * 100, 1)} centavos en el Ideal X, según los contadores de McLean "
          f"(Levinson 2006) [verificado, secundaria]. {coma(CARGA_SUELTA, 2)} ÷ {coma(CARGA_CAJA, 3)} ≈ {n}.")
    return L.svg("El contenedor: 37 veces menos",
                 "Con US$5,83 se cargaba una tonelada suelta o 37 toneladas en las cajas del Ideal X (1956).")


# ---------------------------------------------------------------------------
# F-G1_little · cuánto trabajo abierto conviene (Parte 11, G1)
# ---------------------------------------------------------------------------
HS_MAQ, HS_HORAS = 4, 2     # Hopp y Spearman: cuatro máquinas en serie, de dos horas cada una
HS_MAX = 12                 # piezas en proceso que se muestran


def fig_little(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Cuántos trabajos conviene tener abiertos a la vez?",
             f"Una línea de {HS_MAQ} máquinas en serie, de {HS_HORAS} horas cada una (el ejemplo de Hopp y "
             "Spearman), en el caso ideal, sin variabilidad.")
    x0, A = L.M, L.A
    ritmo = lambda w: min(w / HS_MAQ, 1.0)            # fracción de la capacidad
    tiempo = lambda w: w / (ritmo(w) / HS_HORAS)      # ley de Little: trabajo abierto ÷ ritmo de salida
    px0, px1 = x0 + 50, x0 + A - 10
    X = lambda w: px0 + w / HS_MAX * (px1 - px0)
    hg = 130 if L.ap else 150
    ws = range(1, HS_MAX + 1)
    y = L.y
    o.append(texto(x0, y + 4, "Ritmo de salida, en % de la capacidad", 13.5, TINTA, 700))
    top = y + 20
    Y1 = lambda f: top + (1 - f) * hg
    for f in (0, .25, .5, .75, 1):
        linea(o, px0, Y1(f), px1, Y1(f), TINTA3 if f == 0 else GRILLA, 1.2 if f == 0 else 1)
        o.append(texto(px0 - 7, Y1(f) + 4, f"{f * 100:.0f} %", 11, TINTA3, anc="end"))
    linea(o, X(HS_MAQ), top - 4, X(HS_MAQ), top + hg, AZUL, 1.3, "4 3")
    polilinea(o, [(X(w), Y1(ritmo(w))) for w in ws], AZUL, 2.6)
    for w in ws:
        punto(o, X(w), Y1(ritmo(w)), 4.5)
    o.append(texto(X(1) + 8, Y1(ritmo(1)) + 18, f"1 pieza: {ritmo(1) * 100:.0f} %", 12.5, TINTA, 700))
    o.append(texto(X(HS_MAQ) + 10, Y1(1) + 20, f"{HS_MAQ} piezas: 100 %; con más, el ritmo ya no sube", 12.5,
                   TINTA, 700))
    y2 = top + hg + 34
    o.append(texto(x0, y2 + 4, "Tiempo de entrega de cada pieza, en horas", 13.5, TINTA, 700))
    top2 = y2 + 20
    tmax = tiempo(HS_MAX)
    Y2 = lambda t: top2 + (1 - t / tmax) * hg
    t0 = tiempo(1)
    for t in (0, t0, 2 * t0, 3 * t0):
        linea(o, px0, Y2(t), px1, Y2(t), TINTA3 if t == 0 else GRILLA, 1.2 if t == 0 else 1)
        o.append(texto(px0 - 7, Y2(t) + 4, f"{t:.0f} h", 11, TINTA3, anc="end"))
    linea(o, X(HS_MAQ), top2, X(HS_MAQ), top2 + hg, AZUL, 1.3, "4 3")
    polilinea(o, [(X(w), Y2(tiempo(w))) for w in ws if w <= HS_MAQ], AZUL, 2.6)
    polilinea(o, [(X(w), Y2(tiempo(w))) for w in ws if w >= HS_MAQ], NARANJA, 2.6, "7 4")
    for w in ws:
        punto(o, X(w), Y2(tiempo(w)), 4.5, AZUL if w <= HS_MAQ else NARANJA)
    o.append(texto(X(1), Y2(t0) + 20, f"{t0:.0f} h: el mínimo", 12.5, TINTA, 700))
    o.append(texto(X(1), Y2(t0) + 36, f"{HS_MAQ} máquinas × {HS_HORAS} h", 11.5, TINTA2))
    fin = (f"{HS_MAX} piezas: {tmax:.0f} horas, el triple" if L.ap else f"{HS_MAX} piezas: {tmax:.0f} h, el triple")
    o.append(texto(X(HS_MAX) - 12, top2 - 9, fin, 12.5, NARANJA, 700, anc="end"))
    bot2 = top2 + hg
    for w in ws:
        o.append(texto(X(w), bot2 + 18, w, 11, TINTA3, anc="middle"))
    o.append(texto((px0 + px1) / 2, bot2 + 36, "piezas en proceso: el trabajo abierto a la vez", 11.5, TINTA2,
                   anc="middle"))
    assert t0 == 8 and tmax == 3 * t0 and ritmo(1) == 0.25
    L.y = bot2 + 44
    L.pie(f"Con menos de {HS_MAQ} piezas en proceso hay máquinas paradas; con más de {HS_MAQ}, el ritmo no sube y "
          f"cada pieza espera más: con {HS_MAX}, tarda el triple.",
          "Ley de Little: tiempo de entrega = trabajo abierto ÷ ritmo de salida. Con el mismo ritmo, más trabajo "
          "abierto es sólo más espera.",
          "Hopp y Spearman, Factory Physics, 1996 [verificado, secundaria]: 25 % de la capacidad con una pieza en "
          "proceso, 100 % con cuatro. Los tiempos son un cálculo con la ley de Little para el caso ideal "
          "[cálculo]; con variabilidad, una línea real rinde menos y espera más.")
    return L.svg("La ley de Little",
                 "Arriba, el ritmo sube 25 % por pieza hasta 4 piezas y después queda en 100 %. Abajo, el tiempo de "
                 "entrega queda en 8 horas hasta 4 piezas y sube 2 horas por pieza: 24 horas con 12.")


# ---------------------------------------------------------------------------
# F-G3_amdahl · lo que no se acelera pone el techo (Parte 11, G3)
# ---------------------------------------------------------------------------
AMDAHL_SERIE = 0.40     # parte que se hace paso por paso (Amdahl 1967)
AMDAHL_K = [(1, "como hoy"), (2, "la otra parte, 2 veces más rápida"), (4, "4 veces más rápida"),
            (10, "10 veces más rápida"), (100, "100 veces más rápida"), (math.inf, "infinitamente rápida")]


def fig_amdahl(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    s = AMDAHL_SERIE
    L.cabeza("¿Por qué acelerar una parte no acelera el todo?",
             f"Tiempo total de un trabajo en el que el {s * 100:.0f} % no se puede acelerar, a medida que el otro "
             f"{(1 - s) * 100:.0f} % se hace más rápido.")
    x0, A = L.M, L.A
    rw, vw = (250, 120) if L.ap else (0, 96)
    bx0, bw = x0 + rw, A - rw - vw
    y = L.y
    o.append(texto(bx0, y + 26, f"no se acelera: {s * 100:.0f} %", 12, NARANJA, 700))
    o.append(texto(bx0 + bw * s + 6, y + 26, f"se acelera: {(1 - s) * 100:.0f} %", 12, AZUL, 700))
    o.append(texto(x0 + A, y + 12, "el todo va", 11.5, TINTA2, 700, anc="end"))
    o.append(texto(x0 + A, y + 26, "… veces más rápido", 11.5, TINTA2, 700, anc="end"))
    y += 36
    for k, rot in AMDAHL_K:
        t = s + (1 - s) / k
        if L.ap:
            o.append(texto(bx0 - 10, y + 17, rot, 12.5, TINTA, 600, anc="end"))
        else:
            o.append(texto(x0, y + 12, rot, 12.5, TINTA, 600))
            y += 18
        o.append(barra(bx0, y, bw * s, 24, "rayado"))
        if t > s:
            o.append(barra(bx0 + bw * s, y, bw * (t - s), 24, "lleno_azul"))
        # el piso, por tramos: en la vertical los rótulos van entre las barras
        linea(o, bx0 + bw * s, y - 4, bx0 + bw * s, y + 28, NARANJA, 1.4, "5 4")
        tope = k == math.inf
        o.append(texto(x0 + A, y + 18, coma(1 / t, 2), 15, NARANJA if tope else TINTA, 700, anc="end"))
        y += 24 + 14
    o.append(texto(bx0 + bw * s, y + 8, f"el todo nunca tarda menos que el {s * 100:.0f} %: techo de "
                   f"{coma(1 / s, 1)} veces", 12.5, NARANJA, 700, anc="middle"))
    assert abs(1 / s - 2.5) < 1e-9
    L.y = y + 16
    L.pie(f"Aunque el {(1 - s) * 100:.0f} % se haga infinitamente rápido, el todo nunca va más de "
          f"{coma(1 / s, 1)} veces más rápido: queda el {s * 100:.0f} % que no se aceleró.",
          "Antes de acelerar una parte, conviene medir cuánto pesa en el total: lo que no se toca pone el techo.",
          "Amdahl 1967: el 40 % de las instrucciones eran tareas que se hacen paso por paso [verificado, "
          "secundaria]. Techo = 1 ÷ 0,40 = 2,5 [cálculo]. La ley supone que el problema no crece: si con más "
          "capacidad se atiende un problema más grande, el límite se corre (Gustafson 1988).")
    return L.svg("La ley de Amdahl",
                 "Seis barras apiladas: el 40 % rayado no cambia y el 60 % azul se achica; el todo va 1,43, 1,82, "
                 "2,17, 2,46 y como máximo 2,50 veces más rápido.")


# ---------------------------------------------------------------------------
# Lote 3 (22-oct-2026): helpers comunes
# ---------------------------------------------------------------------------
def fila_cuadritos(o, x, y, v, lado, sep, rel, tr=None):
    """v cuadritos en fila; si v no es entero, el último va parcial, con el contorno de trazos.
    Devuelve el x del borde derecho."""
    t = f' stroke="{tr}" stroke-width="1"' if tr else ""
    n = int(v)
    for i in range(n):
        o.append(f'<rect x="{x + i * (lado + sep):.1f}" y="{y:.1f}" width="{lado}" height="{lado}" rx="1.5" '
                 f'fill="{rel}"{t}/>')
    xf = x + n * (lado + sep)
    if v - n > 1e-9:
        o.append(f'<rect x="{xf:.1f}" y="{y:.1f}" width="{(v - n) * lado:.1f}" height="{lado}" rx="1.5" '
                 f'fill="{rel}"/>')
        o.append(f'<rect x="{xf:.1f}" y="{y:.1f}" width="{lado}" height="{lado}" rx="1.5" fill="none" '
                 f'stroke="{tr or rel}" stroke-width="1" stroke-dasharray="3 2"/>')
        xf += lado + sep
    return xf - sep


def corchete(o, x0, x1, y, color=AZUL):
    """Corchete horizontal abierto hacia abajo, de x0 a x1."""
    o.append(f'<path d="M{x0:.1f},{y + 6:.1f} V{y:.1f} H{x1:.1f} V{y + 6:.1f}" fill="none" stroke="{color}" '
             f'stroke-width="1.5"/>')


# ---------------------------------------------------------------------------
# F-P2_casi_muerte · a un evento de no existir (§2.5, SpaceX y Tesla)
# ---------------------------------------------------------------------------
CASI_MUERTE = [  # cuándo, qué, tipo
    ("2006", "Falcon 1, vuelo 1: falla.", "falla"),
    ("2007", "Falcon 1, vuelo 2: falla.", "falla"),
    ("agosto de 2008", "Falcon 1, vuelo 3: falla.", "falla"),
    ("28 de septiembre de 2008", "Falcon 1, vuelo 4: funciona. Era el último para el que alcanzaba el dinero.",
     "exito"),
    ("23 de diciembre de 2008", "La NASA contrata a SpaceX 12 vuelos a la Estación Espacial, por unos US$1.600 "
     "millones.", "rescate"),
    ("24 de diciembre de 2008", "Tesla cierra una ronda de unos US$40 millones en deuda convertible.", "rescate"),
]
CONTROL = [  # el grupo de control (§2.5)
    ("Kistler Aerospace", "buscaba un cohete reutilizable y había reunido unos US$900 millones", "quiebra en 2003"),
    ("Fisker", "autos", "quiebra en 2013"),
    ("Better Place", "autos", "quiebra en 2013"),
]


def marca(o, cx, cy, tipo, r=9):
    """Marca de un evento: falla (cruz naranja), quiebra (cruz gris), exito (tilde) o rescate (punto)."""
    if tipo in ("falla", "quiebra"):
        col = NARANJA if tipo == "falla" else TINTA3
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{FONDO}" stroke="{col}" stroke-width="2"/>')
        d = r * 0.42
        linea(o, cx - d, cy - d, cx + d, cy + d, col, 2)
        linea(o, cx - d, cy + d, cx + d, cy - d, col, 2)
    elif tipo == "exito":
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{AZUL}"/>')
        polilinea(o, [(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .38), (cx + r * .48, cy - r * .36)],
                  FONDO, 2.2)
    else:
        punto(o, cx, cy, 6)


def fig_casi_muerte(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿A cuánto estuvieron SpaceX y Tesla de no existir?",
             "Lo que pasó de 2006 a la Navidad de 2008, en orden y sin escala de tiempo. "
             + ("A la derecha" if L.ap else "Abajo") + ", el grupo de control.")
    x0, A = L.M, L.A
    pw = A * 0.56 if L.ap else A
    y = L.y
    o.append(texto(x0, y + 13, "SpaceX y Tesla", 13.5, TINTA, 700))
    y += 34
    xm, tx = x0 + 10, x0 + 30
    marcas = []
    for cuando, que, tipo in CASI_MUERTE:
        o.append(texto(tx, y + 5, cuando, 11.5, TINTA2, 600))
        col, peso = {"falla": (TINTA, 400), "exito": (AZUL, 700), "rescate": (AZUL, 400)}[tipo]
        marcas.append((y + 1, tipo))
        y = bloque(o, tx, y + 9, pw - 30, que, 12.5, col, peso) + 16
    linea(o, xm, marcas[0][0], xm, marcas[-1][0], GRILLA, 2)
    for ym, tipo in marcas:
        marca(o, xm, ym, tipo)
    if L.ap:
        cx0, cw = x0 + pw + 34, A - pw - 34
        yc = L.y
    else:
        cx0, cw = x0, A
        yc = y + 6
    o.append(texto(cx0, yc + 13, "El grupo de control", 13.5, TINTA, 700))
    yc = bloque(o, cx0, yc + 20, cw, "apuestas parecidas que terminaron en quiebra", 12, TINTA2) + 18
    for nombre, que, fin in CONTROL:
        marca(o, cx0 + 10, yc + 1, "quiebra")
        o.append(texto(cx0 + 30, yc + 5, nombre, 12.5, TINTA, 700))
        yb = bloque(o, cx0 + 30, yc + 9, cw - 30, que, 11.5, TINTA2)
        o.append(texto(cx0 + 30, yb + 14, fin, 12, NARANJA, 700))
        yc = yb + 36
    assert [t for _, _, t in CASI_MUERTE].count("falla") == 3
    L.y = (max(y, yc) if L.ap else yc) - 14
    L.pie("Las dos empresas estuvieron a un evento de todo o nada de no existir: el cuarto vuelo era el último "
          "para el que alcanzaba el dinero.",
          "Contada sin el grupo de control, la historia parece una receta. Lo que no se copia es la apuesta total.",
          "Fechas y montos [reportado] (§2.5). Los pasos van en orden, sin escala de tiempo: del cuarto vuelo al "
          "contrato de la NASA pasaron menos de tres meses.")
    return L.svg("A un evento de no existir",
                 "Tres vuelos fallidos del Falcon 1 (2006, 2007, agosto de 2008), el cuarto exitoso el 28 de "
                 "septiembre de 2008, el contrato de la NASA el 23 de diciembre y la ronda de Tesla el 24. Grupo de "
                 "control: Kistler Aerospace (quiebra en 2003), Fisker y Better Place (2013).")


# ---------------------------------------------------------------------------
# F-P3_baterias · el caso grande de la ley de Wright (§3.3)
# ---------------------------------------------------------------------------
BAT_PRECIO = [(2010, 1100), (2025, 108)]   # US$/kWh, paquete de ion-litio (BloombergNEF); 2010: «más de»
BAT_KWH = 60                               # tamaño del paquete (ilustrativo)


def fig_baterias(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    (a0, p0), (a1, p1) = BAT_PRECIO
    c0, c1 = BAT_KWH * p0, BAT_KWH * p1
    L.cabeza("¿Cuánto bajó en quince años una batería de ion-litio?",
             f"Lo que costaría un paquete de {BAT_KWH} kWh (tamaño ilustrativo, del orden del de un auto eléctrico) "
             "al precio promedio de cada año. Cada cuadrito es US$1.000.")
    x0, A = L.M, L.A
    cols, sep = (22, 4) if L.ap else (11, 4)
    lado = min(int((A - (cols - 1) * sep) / cols), 30)
    y = L.y
    y = bloque(o, x0, y, A, f"{a0}: más de US${miles(p0)} por kWh → más de US${miles(c0)} el paquete", 13.5,
               TINTA, 700) + 8
    y += cuadritos(o, x0, y, c0 // 1000, cols, lado, sep, lambda i: (GRIS_SUAVE, TINTA3)) + 30
    y = bloque(o, x0, y, A, f"{a1}: US${p1} por kWh → unos US${miles(c1)} el paquete", 13.5, AZUL, 700) + 8
    xf = fila_cuadritos(o, x0, y, c1 / 1000, lado, sep, AZUL)
    o.append(texto(xf + 14, y + lado / 2 + 5, f"más de {p0 // p1} veces menos", 14, AZUL, 700))
    assert c0 == 66_000 and c1 == 6_480 and p0 // p1 == 10
    L.y = y + lado
    L.pie(f"El mismo paquete de {BAT_KWH} kWh pasó de más de US${miles(c0)} a unos US${miles(c1)}: más de diez "
          "veces menos en quince años.",
          "En esos años la producción acumulada creció enormemente, como predice la ley de Wright. Pero con "
          "producción exponencial, una simple tendencia contra el tiempo predice casi igual de bien (Nagy et al. "
          "2013).",
          f"Precio promedio del paquete de ion-litio, BloombergNEF: {a0}, más de US${miles(p0)}/kWh [reportado; la "
          f"serie se reexpresa cada año en dólares constantes]; {a1}, US${p1}/kWh [verificado, primaria — encuesta "
          f"de diciembre de {a1}]. El tamaño de {BAT_KWH} kWh es ilustrativo: {BAT_KWH} × {miles(p0)} = "
          f"{miles(c0)}; {BAT_KWH} × {p1} = {miles(c1)} [cálculo].")
    return L.svg("Baterías: más de diez veces menos",
                 f"Un paquete de {BAT_KWH} kWh en cuadritos de US$1.000: 66 en {a0} y 6,5 en {a1}.")


# ---------------------------------------------------------------------------
# F-C5_theranos · «mínimo» no es «sin validar» (Parte 11, C5)
# ---------------------------------------------------------------------------
THERANOS = (240, 15)   # análisis ofrecidos («más de 240») y hechos en su propio equipo («unos 15»), dic-2014


def fig_theranos(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    total, propios = THERANOS
    L.cabeza("¿Cuántos de sus análisis hacía Theranos con su propio equipo?",
             "Los análisis de sangre que ofrecía en diciembre de 2014. Cada cuadrito es un análisis.")
    x0, A = L.M, L.A
    cols, sep = (30, 4) if L.ap else (20, 4)
    lado = int((A - (cols - 1) * sep) / cols)
    y = L.y
    o.append(texto(x0, y + 13, f"unos {propios} en su propio equipo", 13.5, AZUL, 700))
    y += 22
    corchete(o, x0, x0 + propios * (lado + sep) - sep, y)
    y += 10
    y += cuadritos(o, x0, y, total, cols, lado, sep,
                   lambda i: (AZUL, None) if i < propios else (NARANJA_SUAVE, NARANJA)) + 24
    o.append(texto(x0, y, f"el resto, unos {total - propios}, en máquinas comerciales, sin decirlo", 13.5,
                   NARANJA, 700))
    assert propios <= cols
    L.y = y + 4
    L.pie(f"De más de {total} análisis que ofrecía, Theranos hacía unos {propios} en su propio equipo; el resto, "
          "en máquinas comerciales, sin decirlo.",
          "Donde el producto puede dañar a alguien, «mínimo» no puede querer decir «sin validar».",
          f"Diciembre de 2014 [verificado, primaria — The Wall Street Journal, 15-oct-2015]. Se dibujan {total} "
          f"por «más de {total}» y {propios} por «unos {propios}».")
    return L.svg("Theranos: 15 de 240",
                 f"{total} cuadritos, uno por análisis ofrecido: {propios} azules, hechos en su propio equipo; "
                 f"{total - propios} naranjas, en máquinas comerciales.")


# ---------------------------------------------------------------------------
# F-D4_concorde · la falacia del costo hundido (Parte 11, D4)
# ---------------------------------------------------------------------------
CONCORDE_COSTO = (70, 1500, 2100)   # £ millones: estimado en 1962; gastado hasta 1976 (rango)
CONCORDE_AVIONES = (350, 20)        # esperados, construidos


def fig_concorde(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    est, lo, hi = CONCORDE_COSTO
    esp, hechos = CONCORDE_AVIONES
    L.cabeza("¿Cuánto se gastó en el Concorde y cuánto se obtuvo?",
             "Arriba, el costo de desarrollo, en millones de libras. Abajo, los aviones: cada cuadrito es uno.")
    x0, A = L.M, L.A
    X = lambda v: x0 + v / hi * A
    y = L.y
    y = bloque(o, x0, y, A, f"Estimado en 1962: £{est} millones", 13.5, TINTA, 700) + 6
    o.append(barra(x0, y, X(est) - x0, 26, "suave"))
    y += 26 + 24
    y = bloque(o, x0, y, A, f"Gastado hasta 1976: entre £{miles(lo)} y £{miles(hi)} millones, de {lo // est} a "
               f"{hi // est} veces lo estimado", 13.5, NARANJA, 700) + 6
    o.append(barra(x0, y, X(lo) - x0, 26, "lleno"))
    o.append(barra(X(lo), y, X(hi) - X(lo), 26, "rayado"))
    y += 26
    for v in (0, 500, 1000, 1500, 2000):
        linea(o, X(v), y + 4, X(v), y + 9, TINTA3)
        o.append(texto(X(v), y + 22, miles(v), 11, TINTA3, anc="start" if v == 0 else "middle"))
    o.append(texto(x0 + A, y + 38, "millones de libras", 11, TINTA3, anc="end"))
    y += 60
    o.append(texto(x0, y + 13, f"Aviones: se esperaban {esp}", 13.5, TINTA, 700))
    y += 22
    cols, sep = (35, 4) if L.ap else (25, 4)
    lado = int((A - (cols - 1) * sep) / cols)
    o.append(texto(x0, y + 13, f"se construyeron {hechos}", 13, AZUL, 700))
    y += 22
    corchete(o, x0, x0 + hechos * (lado + sep) - sep, y)
    y += 10
    y += cuadritos(o, x0, y, esp, cols, lado, sep, lambda i: (AZUL, None) if i < hechos else (FONDO, GRIS))
    assert lo // est == 21 and hi // est == 30 and hechos <= cols
    L.y = y
    L.pie(f"El Concorde costó de {lo // est} a {hi // est} veces lo estimado, y se construyeron {hechos} de los "
          f"{esp} aviones esperados.",
          "Por eso la regla mira adelante: seguir sólo si lo que falta gastar compra lo que se va a obtener. Lo ya "
          "gastado no vuelve, se siga o no.",
          f"Estimado de 1962, costo hasta 1976 y aviones [verificado, secundaria — Wikipedia, con fuentes], en "
          f"libras tal como los da la fuente: parte de la diferencia puede ser inflación. {miles(lo)} ÷ {est} ≈ "
          f"{lo // est}; {miles(hi)} ÷ {est} = {hi // est} [cálculo]. Dawkins y Carlisle bautizaron la falacia con "
          "su nombre en 1976.")
    return L.svg("La falacia del Concorde",
                 f"Costo de desarrollo: £{est} millones estimados en 1962 contra £{miles(lo)} a {miles(hi)} millones "
                 f"gastados hasta 1976. Aviones: {esp} cuadritos, {hechos} construidos.")


# ---------------------------------------------------------------------------
# F-F1_lista · la lista funciona si se usa (Parte 11, F1)
# ---------------------------------------------------------------------------
LISTA = [  # estudio, muertes por cada 1.000 operaciones (antes, con la lista), lectura, ¿diferencia significativa?
    ("OMS, 2009: la lista aplicada en ocho hospitales de ocho países", (15, 8), "7 muertes menos de cada 1.000",
     True),
    ("Ontario, 2014: la lista obligatoria por norma en 101 hospitales", (7.1, 6.5), "diferencia no significativa",
     False),
]


def fig_lista(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Alcanza con tener una lista de verificación?",
             "La lista de verificación quirúrgica en dos estudios. Cada cuadrito es una muerte por cada 1.000 "
             "operaciones.")
    x0, A = L.M, L.A
    rw, lado, sep = (120, 24, 5) if L.ap else (100, 20, 4)
    y = L.y
    for estudio, (antes, despues), lectura, sig in LISTA:
        y = bloque(o, x0, y, A, estudio, 13.5, TINTA, 700) + 8
        for rot, v, rel, tr in (("antes", antes, GRIS_SUAVE, TINTA3),
                                ("con la lista", despues, AZUL if sig else GRIS_SUAVE, None if sig else TINTA3)):
            o.append(texto(x0 + rw - 10, y + lado / 2 + 4, rot, 12, TINTA2, 600, anc="end"))
            xf = fila_cuadritos(o, x0 + rw, y, v, lado, sep, rel, tr)
            o.append(texto(xf + 10, y + lado / 2 + 5, coma(v, 0 if v == int(v) else 1), 13.5,
                           AZUL if rel == AZUL else TINTA, 700))
            y += lado + 8
        o.append(texto(x0 + rw, y + 12, lectura, 12.5, AZUL if sig else TINTA2, 700))
        y += 42
    (_, (a0, d0), _, _), _ = LISTA
    assert a0 - d0 == 7
    L.y = y - 18
    L.pie("Donde se aplicó, la lista bajó la mortalidad de 15 a 8 por cada 1.000 operaciones; donde se impuso por "
          "norma, no la movió.",
          "La lista funciona cuando el equipo la usa de verdad, no cuando se firma. En el estudio de la OMS, además, "
          "las complicaciones bajaron de 11 a 7 de cada 100.",
          "Muertes por cada 1.000 operaciones = mortalidad en % × 10. OMS: Haynes y otros, NEJM 2009, antes y "
          "después, 7.688 pacientes, de 1,5 % a 0,8 % [verificado, primaria]. Ontario: Urbach y otros, NEJM 2014, "
          "de 0,71 % a 0,65 % [verificado, primaria]. Son poblaciones distintas: se compara el cambio dentro de cada "
          "estudio, no los niveles.")
    return L.svg("La lista de verificación",
                 "OMS 2009: 15 muertes por cada 1.000 operaciones antes y 8 con la lista. Ontario 2014, lista "
                 "obligatoria: 7,1 y 6,5, diferencia no significativa.")


# ---------------------------------------------------------------------------
# F-P2_ford_rotacion · el mito del jornal de cinco dólares (§2.1, Ford)
# ---------------------------------------------------------------------------
FORD_PLANTILLA, FORD_CONTRATADOS = 13_623, 50_448   # 1913 (Raff y Summers 1987; archivo de The Henry Ford)
FORD_JORNAL = (2.34, 5.0)                           # US$ por día: antes y desde enero de 1914


def persona_parcial(o, cx, y, s, fill, frac, uid):
    """Persona con sólo una fracción del ancho rellena; el contorno de trazos marca la persona entera."""
    o.append(f'<clipPath id="{uid}"><rect x="{cx - 0.28 * s:.1f}" y="{y:.1f}" width="{0.56 * s * frac:.1f}" '
             f'height="{s:.1f}"/></clipPath>')
    persona(o, cx, y, s, FONDO, fill, "2 2")
    o.append(f'<g clip-path="url(#{uid})">')
    persona(o, cx, y, s, fill)
    o.append('</g>')


def fig_ford_rotacion(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    j0, j1 = FORD_JORNAL
    rot = FORD_CONTRATADOS / FORD_PLANTILLA
    L.cabeza("¿Por qué Ford pagó cinco dólares por día?",
             "Ford en 1913, el año de la línea móvil: la plantilla media y la gente que hubo que contratar para "
             "sostenerla. Cada figura son 1.000 personas.")
    x0, A = L.M, L.A
    cols = 25 if L.ap else 17
    paso = A / cols
    s = paso * 0.86
    alto_f = s * 1.12
    y = L.y
    for n, rotulo, col_t, fill, uid in (
            (FORD_PLANTILLA, f"Plantilla media: {miles(FORD_PLANTILLA)} personas", TINTA, GRIS, "pl"),
            (FORD_CONTRATADOS, f"Contratadas en el año: {miles(FORD_CONTRATADOS)} personas", NARANJA, NARANJA,
             "co")):
        y = bloque(o, x0, y, A, rotulo, 13.5, col_t, 700) + 8
        v = n / 1000
        for i in range(int(v) + 1):
            r, c = divmod(i, cols)
            cx, yy = x0 + c * paso + paso / 2, y + r * alto_f
            if i < int(v):
                persona(o, cx, yy, s, fill)
            else:
                persona_parcial(o, cx, yy, s, fill, v - int(v), f"pp_{uid}_{'ap' if L.ap else 've'}")
        y += math.ceil(v / cols) * alto_f + 14
    y = bloque(o, x0, y, A, f"{coma(rot, 1)} contrataciones por cada puesto: una rotación de alrededor del 370 %",
               13.5, NARANJA, 700) + 22
    o.append(texto(x0, y + 13, "Jornal básico por día, en dólares de cada año", 13.5, TINTA, 700))
    y += 24
    jw = A - (220 if L.ap else 170)
    for rotulo, j, trazo, col in (("antes de enero de 1914", j0, "gris", TINTA),
                                  ("desde enero de 1914", j1, "lleno_azul", AZUL)):
        o.append(texto(x0, y + 12, rotulo, 12, TINTA2, 600))
        y += 18
        o.append(barra(x0, y, jw * j / j1, 22, trazo))
        etq = f"US${coma(j, 2)}" + (" · más del doble" if j == j1 else "")
        o.append(texto(x0 + jw * j / j1 + 8, y + 16, etq, 13.5, col, 700))
        y += 34
    assert 3.6 < rot < 3.8 and j1 / j0 > 2
    L.y = y - 10
    L.pie(f"Para sostener {miles(FORD_PLANTILLA)} puestos, Ford contrató a {miles(FORD_CONTRATADOS)} personas en un "
          f"año: {coma(rot, 1)} por puesto. El jornal de cinco dólares fue el precio de retener gente en un trabajo "
          "muy duro.",
          "Una compensación mide el costo de lo que compensa; no prueba que fuera bueno.",
          f"[reportado — Raff y Summers 1987; archivo de The Henry Ford]. {miles(FORD_CONTRATADOS)} ÷ "
          f"{miles(FORD_PLANTILLA)} ≈ {coma(rot, 1)}: una rotación de alrededor del 370 % [cálculo]. La última figura "
          "de cada grupo es parcial. Jornal en dólares de cada año, sin ajustar por inflación.")
    return L.svg("El jornal de cinco dólares",
                 "Plantilla media de 1913: 13,6 figuras de 1.000 personas; contratadas en el año: 50,4. Jornal: "
                 "US$2,34 antes y US$5 desde enero de 1914.")


# ---------------------------------------------------------------------------
# F-P2_apple · borrar el 70 % y ordenar el resto (§2.3, Apple)
# ---------------------------------------------------------------------------
APPLE_BORRADO = 0.70                                                    # «alrededor de un 70 %» (Isaacson 2011)
APPLE_RESULTADO = [("1997", -1045), ("1998", 309)]                      # US$ millones, por ejercicio
APPLE_CUADRICULA = (("consumidor", "profesional"), ("escritorio", "portátil"))


def icono_compu(o, cx, cy, portatil, col):
    """Escritorio (pantalla con pie) o portátil (pantalla y base)."""
    if portatil:
        caja(o, cx - 16, cy - 14, 32, 21, FONDO, col, 1.6, rx=2)
        o.append(f'<path d="M{cx - 22:.1f},{cy + 9:.1f} H{cx + 22:.1f} L{cx + 18:.1f},{cy + 14:.1f} '
                 f'H{cx - 18:.1f} Z" fill="{col}"/>')
    else:
        caja(o, cx - 18, cy - 19, 36, 26, FONDO, col, 1.6, rx=2)
        linea(o, cx, cy + 7, cx, cy + 13, col, 2.2)
        linea(o, cx - 10, cy + 14, cx + 10, cy + 14, col, 2.2)


def fig_apple(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    (e0, r0), (e1, r1) = APPLE_RESULTADO
    filas, cols = APPLE_CUADRICULA
    L.cabeza("¿Qué hizo Apple con su línea de productos en 1997?",
             "Al volver Jobs: primero borró la mayor parte de la línea; después ordenó lo que quedó en cuatro "
             "casillas. Al final, el resultado de los dos ejercicios.")
    x0, A = L.M, L.A
    y = L.y
    o.append(texto(x0, y + 13, "1 · La línea de productos", 13.5, TINTA, 700))
    y += 22
    xb = x0 + A * APPLE_BORRADO
    o.append(barra(x0, y, xb - x0, 30, "rayado"))
    o.append(barra(xb, y, x0 + A - xb, 30, "lleno_azul"))
    o.append(texto(x0, y + 50, f"se borró alrededor del {APPLE_BORRADO * 100:.0f} %", 12.5, NARANJA, 700))
    o.append(texto(xb + 4, y + 50, f"quedó el {(1 - APPLE_BORRADO) * 100:.0f} %", 12.5, AZUL, 700))
    y += 84
    if L.ap:
        gx, gw, rx_, rw_ = x0, 400, x0 + 470, A - 470
    else:
        gx, gw, rx_, rw_ = x0, min(A, 420), x0, A
    yg = y
    o.append(texto(gx, yg + 13, "2 · Lo que quedó, en una cuadrícula de cuatro", 13.5, TINTA, 700))
    yg += 26
    rwl = 100
    cw, ch = (gw - rwl) / 2, 72
    for j, c in enumerate(cols):
        o.append(texto(gx + rwl + cw * (j + .5), yg + 12, c, 12.5, TINTA2, 600, anc="middle"))
    yg += 20
    for i, f in enumerate(filas):
        o.append(texto(gx + rwl - 10, yg + i * ch + ch / 2 + 4, f, 12.5, TINTA2, 600, anc="end"))
        for j in range(2):
            caja(o, gx + rwl + j * cw + 3, yg + i * ch + 3, cw - 6, ch - 6, AZUL_SUAVE, AZUL, 1.2, rx=4)
            icono_compu(o, gx + rwl + cw * (j + .5), yg + i * ch + ch / 2, j == 1, AZUL)
    yg += 2 * ch
    yr = y if L.ap else yg + 34
    yr = bloque(o, rx_, yr, rw_, "3 · Resultado del ejercicio, en millones de US$", 13.5, TINTA, 700) + 12
    k = 150 / -r0                       # px por millón
    y0 = yr + 26 + r1 * k               # línea de cero
    bw = 74
    xs = (rx_ + 50, rx_ + 50 + bw + 70)
    linea(o, rx_ + 30, y0, xs[1] + bw + 30, y0, TINTA3, 1.2)
    o.append(texto(rx_ + 24, y0 + 4, "0", 11, TINTA3, anc="end"))
    for (e, r), xbar in zip(APPLE_RESULTADO, xs):
        if r < 0:
            o.append(barra(xbar, y0, bw, -r * k, "lleno"))
            o.append(texto(xbar + bw / 2, y0 - r * k + 20, f"−{miles(-r)}", 15, NARANJA, 700, anc="middle"))
            o.append(texto(xbar + bw / 2, y0 - 8, e, 12.5, TINTA2, 600, anc="middle"))
        else:
            o.append(barra(xbar, y0 - r * k, bw, r * k, "lleno_azul"))
            o.append(texto(xbar + bw / 2, y0 - r * k - 8, f"+{miles(r)}", 15, AZUL, 700, anc="middle"))
            o.append(texto(xbar + bw / 2, y0 + 18, e, 12.5, TINTA2, 600, anc="middle"))
    yr = y0 - r0 * k + 26
    assert APPLE_BORRADO == 0.70 and r0 < 0 < r1
    L.y = max(yg, yr) if L.ap else yr
    L.pie(f"Apple borró alrededor del {APPLE_BORRADO * 100:.0f} % de su línea y ordenó el resto en cuatro casillas; "
          f"en el ejercicio siguiente pasó de perder US${miles(-r0)} millones a ganar US${miles(r1)} millones.",
          "Simplificar es trabajo —se trata de sacar—, no ausencia de trabajo.",
          "Línea reducida alrededor de un 70 % y cuadrícula de cuatro [reportado — Isaacson 2011]; resultados de los "
          "ejercicios 1997 y 1998 [reportado — informes anuales de Apple]. La figura junta los dos hechos; no mide "
          "cuánto del cambio se debe al foco [interpretación]. La barra de la línea es una proporción: no cuenta "
          "productos.")
    return L.svg("Apple: borrar y ordenar",
                 "Una barra de la línea de productos con el 70 % borrado; la cuadrícula de cuatro (consumidor o "
                 "profesional, escritorio o portátil); resultado: −1.045 millones en 1997 y +309 en 1998.")


# ---------------------------------------------------------------------------
# F-R6_flujo · tiempo que agrega valor contra tiempo total (receta R6) — ilustrativa
# ---------------------------------------------------------------------------
FLUJO = [  # paso, horas, ¿agrega valor?  (ejemplo ilustrativo: un pedido en un taller)
    ("en cola", 72, False), ("corte", 0.75, True), ("espera", 24, False), ("soldadura", 1, True),
    ("espera pintura", 48, False), ("pintura", 0.5, True), ("espera retiro", 24, False),
]


def dur(h):
    """0.75 -> '45 min'; 1 -> '1 h'; 72 -> '3 días'."""
    if h < 1:
        return f"{h * 60:.0f} min"
    if h < 24:
        return f"{h:.0f} h"
    return f"{h / 24:.0f} día" + ("s" if h != 24 else "")


def fig_flujo(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    total = sum(h for _, h, _ in FLUJO)
    va = sum(h for _, h, v in FLUJO if v)
    L.cabeza("¿Dónde se va el tiempo de un pedido?",
             "Un pedido en un taller, desde que entra hasta que se retira (ejemplo ilustrativo). Azul: los pasos que "
             "cambian algo que el cliente pagaría. Gris: espera.")
    x0, A = L.M, L.A
    X = lambda t: x0 + t / total * A
    o.append(texto(x0, L.y + 13, "El recorrido, a escala: el ancho de cada tramo es su duración", 13.5, TINTA, 700))
    y = L.y + 66
    t, k = 0, 0
    for paso, h, v in FLUJO:
        if v:
            xm = X(t + h / 2)
            o.append(barra(X(t), y, max(X(t + h) - X(t), 3), 34, "lleno_azul"))
            alto_r = 16 + 18 * (k % 2)          # rótulos escalonados: en la vertical quedan cerca
            linea(o, xm, y - 3, xm, y - alto_r + 4, AZUL, 1.2)
            o.append(texto(xm, y - alto_r, f"{paso} · {dur(h)}", 11.5, AZUL, 700, anc="middle"))
            k += 1
        else:
            o.append(barra(X(t), y, X(t + h) - X(t), 34, "gris"))
            xm = (X(t) + X(t + h)) / 2
            o.append(texto(xm, y + 52, paso, 11.5, TINTA2, 600, anc="middle"))
            o.append(texto(xm, y + 67, dur(h), 11.5, TINTA2, anc="middle"))
        t += h
    y += 100
    o.append(texto(x0, y + 13, "Lo que se suele medir: la fabricación", 13.5, TINTA, 700))
    y += 22
    o.append(barra(x0, y, max(X(va) - x0, 3), 24, "lleno_azul"))
    o.append(texto(X(va) + 10, y + 17, f"{int(va)} h {round(va % 1 * 60)} min", 13.5, AZUL, 700))
    y += 44
    o.append(texto(x0, y + 13, "Lo que espera el cliente", 13.5, TINTA, 700))
    y += 22
    o.append(barra(x0, y, A, 24, "gris"))
    y += 24
    o.append(texto(x0 + A, y + 20, f"unos {total / 24:.0f} días", 13.5, TINTA, 700, anc="end"))
    y += 30
    y = bloque(o, x0, y, A, f"tiempo que agrega valor ÷ tiempo total = {coma(va / total * 100, 1)} %", 14, AZUL, 700)
    assert va == 2.25 and round(total / 24) == 7 and round(va / total * 100, 1) == 1.3
    L.y = y
    L.pie(f"De unos {total / 24:.0f} días, el pedido pasa 2 horas y cuarto en pasos que agregan valor: el "
          f"{coma(va / total * 100, 1)} % del tiempo. El resto es espera.",
          "Medir sólo la fabricación esconde lo principal: en la mayoría de los procesos, la espera es la mayor "
          "parte.",
          "Ejemplo ilustrativo, no un dato medido: los tiempos están elegidos para mostrar la receta R6. Con datos "
          "reales, el cociente se calcula igual: tiempo que agrega valor ÷ tiempo total.")
    return L.svg("Medir el flujo",
                 "Un pedido de unos 7 días en una barra: tres franjas azules finas (corte, soldadura, pintura; 2 h 15 "
                 "min en total) entre esperas grises. Cociente: 1,3 %.")


# ---------------------------------------------------------------------------
# F-P6_controles · los cinco controles como diagrama de decisión (Parte 6)
# ---------------------------------------------------------------------------
CONTROLES = [  # código, nombre, condición (§6.3)
    ("G0", "Unidad", "la unidad que se repite está nombrada y su costo real, medido"),
    ("G1", "Margen", "m > 0 con la hora propia al costo, medido en al menos 10 unidades reales"),
    ("G2", "Curva", "el costo por unidad ya bajó al menos una vez al duplicar, con datos propios"),
    ("G3", "Activo", "la etapa dejó instalado un activo nombrable"),
    ("G4", "Caja", "la autonomía supera el ancho del pozo de la etapa siguiente, con 30 % de margen"),
]
SALIDAS = ["matar el proyecto (fin)", "repetir la etapa con alcance reducido (vuelve arriba)",
           "cambiar a otra cosa (fin de este proyecto)"]


def hexagono(o, x, y, w, h, fill, stroke, sw=1.5):
    d = h / 2.6
    o.append(f'<path d="M{x:.1f},{y + h / 2:.1f} L{x + d:.1f},{y:.1f} H{x + w - d:.1f} L{x + w:.1f},{y + h / 2:.1f} '
             f'L{x + w - d:.1f},{y + h:.1f} H{x + d:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def fig_controles(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Qué se revisa antes de gastar en la etapa siguiente?",
             "Los cinco controles de una escalera, en orden. Cada uno se responde con sí o no, con un número y una "
             "fecha; qué hacer ante un «no» se elige antes de empezar la etapa.")
    x0, A = L.M, L.A
    hw = 500 if L.ap else 400
    cx = x0 + hw / 2
    bus = x0 + hw + 36
    y = L.y
    caja(o, x0 + 40, y, hw - 80, 32, GRIS_SUAVE, TINTA3, 1.2)
    o.append(texto(cx, y + 21, "Antes de gastar en la etapa siguiente", 13, TINTA, 700, anc="middle"))
    y_ini, x_ini = y + 16, x0 + hw - 40
    y += 32
    ycs = []
    for i, (cod, nom, cond) in enumerate(CONTROLES):
        linea(o, cx, y, cx, y + 24, TINTA3, 1.3, flecha="fl")
        if i:
            o.append(texto(cx + 8, y + 16, "sí", 12, TINTA2, 700))
        y += 24
        tw = hw - 56
        h = 23 + alto(cond, 12, tw) + 9
        hexagono(o, x0, y, hw, h, FONDO, TINTA, 1.5)
        o.append(texto(cx, y + 19, f"{cod} · {nom}", 13, TINTA, 700, anc="middle"))
        bloque(o, x0 + 28, y + 23, tw, cond, 12, TINTA2, anc="middle")
        ycs.append(y + h / 2)
        linea(o, x0 + hw, y + h / 2, bus, y + h / 2, NARANJA, 1.5)
        o.append(texto(x0 + hw + 6, y + h / 2 - 6, "no", 12, NARANJA, 700))
        y += h
    linea(o, cx, y, cx, y + 28, AZUL, 1.6, flecha="fl_az")
    o.append(texto(cx + 8, y + 18, "sí, a los cinco", 12, AZUL, 700))
    y += 28
    caja(o, x0 + 40, y, hw - 80, 34, AZUL_SUAVE, AZUL, 1.5)
    o.append(texto(cx, y + 22, "Se gasta en la etapa siguiente", 13.5, AZUL, 700, anc="middle"))
    y += 34

    def caja_no(xb, yb, wb):
        """La caja del «no», con las tres salidas; devuelve su alto."""
        t = []
        yy = bloque(t, xb + 12, yb + 8, wb - 24, "A la fecha no se cumple: se ejecuta lo que se eligió al "
                    "escribir el control", 12.5, TINTA, 700) + 4
        for s_ in SALIDAS:
            yy = bloque(t, xb + 12, yy, wb - 24, "· " + s_, 12, TINTA2) + 1
        yy = bloque(t, xb + 12, yy + 4, wb - 24, "prohibido: «vemos cómo viene»", 12, NARANJA, 700) + 10
        caja(o, xb, yb, wb, yy - yb, FONDO, NARANJA, 1.5)
        o.extend(t)
        return yy - yb

    if L.ap:
        xb, yb = bus + 26, ycs[1] - 10
        wb = x0 + A - 18 - xb
        hb = caja_no(xb, yb, wb)
        ym = yb + hb / 2
        assert ycs[0] <= ym <= ycs[-1]
        linea(o, bus, ycs[0], bus, ycs[-1], NARANJA, 1.5)
        linea(o, bus, ym, xb - 2, ym, NARANJA, 1.5, flecha="fl_na")
        xr = xb + wb / 2
        o.append(f'<path d="M{xr:.1f},{yb:.1f} V{y_ini:.1f} H{x_ini + 2:.1f}" fill="none" stroke="{NARANJA}" '
                 f'stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#fl_na)"/>')
        L.y = max(y, yb + hb)
    else:
        yb = y + 30
        linea(o, bus, ycs[0], bus, yb - 2, NARANJA, 1.5, flecha="fl_na")
        wb = A - 24
        hb = caja_no(x0, yb, wb)
        xr = x0 + A - 8
        o.append(f'<path d="M{x0 + wb:.1f},{yb + hb / 2:.1f} H{xr:.1f} V{y_ini:.1f} H{x_ini + 2:.1f}" fill="none" '
                 f'stroke="{NARANJA}" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#fl_na)"/>')
        L.y = yb + hb
    o.append(texto(x_ini + 10, y_ini - 6, "repetir", 12, NARANJA, 700))
    L.pie("Cinco preguntas en orden, cada una con su «no» decidido antes de empezar: sólo se gasta en la etapa "
          "siguiente si las cinco dan «sí».",
          "Los controles no se saltean ni se reordenan. G2 sin G1 es la forma más común de quebrar creciendo, porque "
          "se siente como éxito hasta el último mes.",
          "Condiciones de §6.3 y salidas de la plantilla de §6.2. Es un diagrama de decisión: no tiene escala ni "
          "datos.")
    return L.svg("Los cinco controles",
                 "Diagrama de decisión: G0 unidad, G1 margen, G2 curva, G3 activo y G4 caja, en orden. Cada «no» va a "
                 "la salida elegida antes (matar, repetir con menos alcance o cambiar); cinco «sí» llevan a gastar en "
                 "la etapa siguiente.")


# ---------------------------------------------------------------------------
# F-A1_ncr · la mejor pieza es la que no existe (Parte 11, A1)
# ---------------------------------------------------------------------------
NCR = [("piezas", 15), ("tiempo de armado", 25), ("herramientas de armado", 0), ("proveedores", 35)]  # antes = 100


def fig_ncr(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Qué se gana preguntando si cada pieza tiene que existir?",
             "La terminal de punto de venta NCR 2760, rediseñada con esa pregunta. Cada fila compara contra su "
             "propio antes, que vale 100.")
    x0, A = L.M, L.A
    rw = 200 if L.ap else 0
    bw = A - rw - 120
    y = L.y
    for i, (rot, d) in enumerate(NCR):
        if L.ap:
            o.append(texto(x0 + rw - 14, y + 24, rot, 13, TINTA, 600, anc="end"))
        else:
            o.append(texto(x0, y + 12, rot, 13, TINTA, 600))
            y += 20
        o.append(barra(x0 + rw, y, bw, 16, "gris"))
        o.append(texto(x0 + rw + bw + 8, y + 13, "antes · 100" if i == 0 else "100", 12, TINTA3, 700))
        y += 20
        if d:
            o.append(barra(x0 + rw, y, bw * d / 100, 16, "lleno_azul"))
        etq = (f"después · {d}" if i == 0 else str(d)) if d else "ninguna"
        o.append(texto(x0 + rw + bw * d / 100 + 8, y + 13, etq, 13, AZUL, 700))
        y += 16 + 24
    assert [d for _, d in NCR] == [15, 25, 0, 35]
    L.y = y - 14
    L.pie("Con esa pregunta, la NCR 2760 quedó con 85 % menos piezas, 75 % menos tiempo de armado, ninguna "
          "herramienta de armado y 65 % menos proveedores.",
          "Se estimó que sacar un solo tornillo ahorraba hasta US$12.500 en la vida del producto.",
          "Boothroyd, Dewhurst y Knight 2002, §1.5.4 [verificado, primaria]. Cada fila compara contra su propio "
          "antes; las filas no se comparan entre sí.")
    return L.svg("NCR 2760: la pieza que no existe",
                 "Cuatro pares de barras, antes = 100: piezas 15, tiempo de armado 25, herramientas 0, proveedores 35.")


# ---------------------------------------------------------------------------
# F-P1_apple_funciones · las seis funciones contra las tres personas (§1.2, Apple 1976-1977)
# ---------------------------------------------------------------------------
APPLE_PERSONAS = [("Wozniak", "el producto técnico"), ("Jobs", "la definición del producto y la venta"),
                  ("Markkula", "el capital y el método comercial")]
APPLE_FUNCIONES = ["Entender al cliente", "Definir el producto", "Producir con calidad", "Vender y distribuir",
                   "Financiar y sobrevivir", "Organizar y aprender"]
APPLE_CUBRE = {  # (función 1-6, persona 0-2): el dato del caso que lo sostiene (§1.2)
    (1, 2): "«empatía»: entender al cliente mejor que nadie",
    (2, 0): "ocho ranuras de expansión",
    (2, 1): "una máquina terminada, con gabinete",
    (2, 2): "«foco»: sacar lo que no importa",
    (3, 0): "diseño con muy pocos componentes",
    (4, 1): "vendió cincuenta Apple I a una tienda",
    (4, 2): "«imputar»: la presentación comunica la calidad",
    (5, 2): "US$250.000 por un tercio de la empresa",
}


def y_lista(xs):
    """['1', '4', '5'] -> '1, 4 y 5'."""
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def fig_apple_funciones(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Quién cubría cada función en Apple, en 1976 y 1977?",
             "Las seis funciones de §1.1 contra las tres personas que hicieron funcionar la empresa. Cada punto "
             "lleva el dato del caso que lo sostiene.")
    x0, A = L.M, L.A
    lab_w = 205 if L.ap else 150
    cw = (A - lab_w) / 3
    tc = 11.5 if L.ap else 11
    xc = lambda j: x0 + lab_w + j * cw
    y = L.y
    fondo = y
    for j, (nom, rol) in enumerate(APPLE_PERSONAS):
        o.append(texto(xc(j) + cw / 2, y + 15, nom, 15, TINTA, 700, anc="middle"))
        fondo = max(fondo, bloque(o, xc(j) + 8, y + 22, cw - 16, rol, 12, TINTA2, anc="middle"))
    y = fondo + 10
    linea(o, x0, y, x0 + A, y, TINTA3)
    for i, fun in enumerate(APPLE_FUNCIONES, 1):
        rot = f"{i} · {fun}"
        marcas = [j for j in range(3) if (i, j) in APPLE_CUBRE]
        hl = alto(rot, 13, lab_w - 12, 700)
        h = max([hl] + [alto(APPLE_CUBRE[i, j], tc, cw - 32) for j in marcas]) + 20
        ym = y + h / 2
        bloque(o, x0, ym - hl / 2, lab_w - 12, rot, 13, TINTA, 700)
        for j in marcas:
            punto(o, xc(j) + 14, ym, 6, AZUL)
            ht = alto(APPLE_CUBRE[i, j], tc, cw - 32)
            bloque(o, xc(j) + 26, ym - ht / 2, cw - 32, APPLE_CUBRE[i, j], tc, TINTA)
        if not marcas:
            o.append(texto(xc(0) + 1.5 * cw, ym + 4, "el caso no lo cuenta", 12, TINTA3, anc="middle"))
        y += h
        linea(o, x0, y, x0 + A, y, GRILLA)
    y += 8
    fondo = y
    for j in range(3):
        vacias = [str(i) for i in range(1, 6) if (i, j) not in APPLE_CUBRE]
        etq = f"solo: fila {vacias[0]} vacía" if len(vacias) == 1 else f"solo: filas {y_lista(vacias)} vacías"
        fondo = max(fondo, bloque(o, xc(j) + 4, y, cw - 8, etq, 12, NARANJA, 700, anc="middle"))
    assert all(any((i, j) in APPLE_CUBRE for j in range(3)) for i in range(1, 6))       # juntos: filas 1-5 llenas
    assert all(any((i, j) not in APPLE_CUBRE for i in range(1, 6)) for j in range(3))   # solo: ninguna columna llena
    L.y = fondo
    L.pie("Juntos, los tres llenaban las cinco filas de las que el caso da datos; solo, a cada uno le quedaba al menos "
          "una fila vacía. Contar puntos por columna es sumar, y una empresa es un producto: lo que decide es que "
          "ninguna fila quede en cero.",
          "La pregunta útil no es quién tuvo más mérito, sino qué función está en cero en este negocio y quién la va "
          "a cubrir.",
          "[reportado — Isaacson 2011; Wozniak 2006; documento en el archivo de Steve Jobs]. A qué función corresponde "
          "cada dato es una lectura del caso [interpretación]: el texto dice «el producto técnico», «la definición del "
          "producto y la venta» y «el capital y el método comercial». Que la fila 6 no tenga puntos no dice que nadie "
          "la cubriera: el caso no lo cuenta.")
    return L.svg("Apple 1976-1977: seis funciones, tres personas",
                 "Matriz de seis funciones por tres personas (Wozniak, Jobs y Markkula), con un punto y el dato del "
                 "caso donde cada uno cubría la función; la fila 6, sin datos.")


# ---------------------------------------------------------------------------
# F-P2_amazon_colchon · el colchón de 2000 y el grupo de control (§2.4, Amazon)
# ---------------------------------------------------------------------------
AMAZON_EVENTOS = [  # marca, cuándo, qué (§2.4; en orden, sin escala de tiempo)
    ("rescate", "febrero de 2000", "coloca bonos convertibles por unos US$680 millones"),
    ("falla", "semanas después", "estalla la burbuja de internet: entre fines de 1999 y 2001, la acción cae más del 90 %"),
    ("exito", "2003", "primera ganancia anual completa: US$35 millones"),
]
AMAZON_CONTROL = [("Pets.com", "cierra en 2000"),
                  ("Webvan", "construyó depósitos antes de tener la demanda; quiebra en 2001")]
AMAZON_CAIDA = 90   # «más del 90 %»: queda menos de 10 de cada 100


def fig_amazon_colchon(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Qué hizo sobrevivir a Amazon cuando la acción cayó más del 90 %?",
             "Amazon y el grupo de control entre 1999 y 2003, en orden y sin escala de tiempo: la misma época y la "
             "misma tesis, «comercio por internet», con colchón y sin colchón.")
    x0, A = L.M, L.A
    pw = A * 0.6 if L.ap else A

    def lista(y, titulo, filas):
        y = bloque(o, x0, y, pw, titulo, 14, TINTA, 700) + 10
        for tipo, cuando, que in filas:
            marca(o, x0 + 10, y + 9, tipo)
            o.append(texto(x0 + 30, y + 14, cuando, 13, TINTA, 700))
            y = bloque(o, x0 + 30, y + 19, pw - 40, que, 12.5, TINTA2) + 14
        return y

    y = lista(L.y, "Amazon", AMAZON_EVENTOS)
    y = lista(y + 8, "Grupo de control: la misma tesis, sin colchón o con margen por unidad negativo",
              [("quiebra", n, q) for n, q in AMAZON_CONTROL])
    xb, yb = (x0 + pw + 40, L.y) if L.ap else (x0, y + 16)
    wb = x0 + A - xb
    yb = bloque(o, xb, yb, wb, "La acción (fines de 1999 = 100)", 13.5, TINTA, 700) + 30
    hb, bw = 190, 80
    base = yb + hb
    for k, (rot, v, trazo) in enumerate((("fines de 1999", 100, "gris"), ("2001", 100 - AMAZON_CAIDA, "lleno"))):
        xx = xb + 20 + k * (bw + 60)
        o.append(barra(xx, base - hb * v / 100, bw, hb * v / 100, trazo))
        o.append(texto(xx + bw / 2, base - hb * v / 100 - 8, "100" if v == 100 else f"menos de {v}", 13.5,
                       TINTA if v == 100 else NARANJA, 700, anc="middle"))
        o.append(texto(xx + bw / 2, base + 18, rot, 12.5, TINTA2, 600, anc="middle"))
    linea(o, xb + 10, base, xb + 20 + 2 * bw + 70, base, TINTA3, 1.2)
    o.append(texto(xb + 20 + bw + 60 + bw / 2, base - hb * 0.1 - 30, f"más del {AMAZON_CAIDA} % menos", 13, NARANJA,
                   700, anc="middle"))
    assert AMAZON_CAIDA == 90 and len(AMAZON_CONTROL) == 2
    L.y = max(y, base + 30) if L.ap else base + 30
    L.pie("Amazon colocó unos US$680 millones semanas antes del estallido. Con la acción en menos de un décimo, ese "
          "colchón le dio tiempo hasta su primera ganancia anual, en 2003; Webvan y Pets.com, con la misma tesis, "
          "cerraron.",
          "«Ese dinero fue el colchón que permitió sobrevivir»: es el nivel 5 (§3.5) en acción. Lo que no se copia: "
          "años de pérdidas sin colchón; Amazon tenía acceso a un mercado de capitales excepcional.",
          "Bonos: informe anual de Amazon, 2000 (690 millones de euros, unos US$680 millones de entonces). La caída "
          "de la acción, la ganancia de 2003 y el grupo de control: [reportado]. «Más del 90 %» quiere decir menos de "
          "10 de cada 100: la barra de 2001 marca ese techo. Que el colchón explique la supervivencia es la lectura "
          "del libro [interpretación]; el grupo de control no prueba que sea la única causa.")
    return L.svg("Amazon: el colchón de 2000",
                 "Amazon coloca unos US$680 millones en febrero de 2000; la acción cae más del 90 % hasta 2001; "
                 "primera ganancia anual en 2003. Pets.com cierra en 2000 y Webvan quiebra en 2001.")


# ---------------------------------------------------------------------------
# F-P7_errores · dónde se comete cada uno de los doce errores (Parte 7)
# ---------------------------------------------------------------------------
ERRORES = {  # n: nombre, antídoto (textos de la Parte 7)
    1: ("El volante dibujado", "un número en dos flechas, o admitirlo como hipótesis"),
    2: ("La escala como tapa del margen", "medir el margen (G1) antes de buscar la curva (G2)"),
    3: ("Automatizar el paso que había que borrar", "la receta R4, el algoritmo de cinco pasos"),
    4: ("La plataforma sin cliente", "el control G0 y la prueba del peldaño"),
    5: ("El sueño sin promesa con fecha", "una promesa chica, con fecha, que pueda resultar falsa en 90 días"),
    6: ("La dependencia disfrazada de margen", "calcular el margen sin ese renglón"),
    7: ("Confundir capital con clientes", "si mañana aparecieran diez clientes, ¿se los podría atender? (§3.5)"),
    8: ("Copiar el rasgo en vez del mecanismo", "copiar el mecanismo, que es barato"),
    9: ("El sesgo de supervivencia como plan", "por cada éxito, buscar dos parecidos que desaparecieron"),
    10: ("El genio solo", "la prueba de las seis funciones (§1.3)"),
    11: ("Casarse con la curva", "cada cierto número de duplicaciones, preguntar qué cambió en el cliente"),
    12: ("Crecer más rápido que la calidad", "que el control de calidad escale antes que el volumen"),
}
# Nivel donde apunta el antídoto: el 1 lo nombra la Parte 7; el 2, 4 y 7, por el control o la
# sección que citan (G1, G0, §3.5); el 6 y el 11, por lo que mide el antídoto [interpretación].
ERRORES_NIVEL = {5: [7], 4: [1], 3: [11], 2: [2, 6], 1: [4]}
ERRORES_FUERA = [3, 5, 8, 9, 10, 12]
ERROR_COMUN = 2   # §6.3: «G2 sin G1 es la forma más común de quebrar creciendo»
assert sorted(sum(ERRORES_NIVEL.values(), []) + ERRORES_FUERA) == list(ERRORES)


def _error_item(o, x, y, w, n, tam, fuera=False):
    """Número en círculo, nombre y antídoto del error n; y = borde superior. Devuelve el inferior."""
    nombre, antidoto = ERRORES[n]
    r = 11
    if n == ERROR_COMUN:
        fill, st, num = NARANJA, NARANJA, FONDO
    elif fuera:
        fill, st, num = FONDO, TINTA2, TINTA
    else:
        fill, st, num = AZUL, AZUL, FONDO
    o.append(f'<circle cx="{x + r:.1f}" cy="{y + r + 1:.1f}" r="{r}" fill="{fill}" '
             f'stroke="{st}" stroke-width="1.6"/>')
    if n == ERROR_COMUN:   # anillo de más: se distingue también en blanco y negro
        o.append(f'<circle cx="{x + r:.1f}" cy="{y + r + 1:.1f}" r="{r + 3.5}" fill="none" '
                 f'stroke="{NARANJA}" stroke-width="1.4"/>')
    o.append(texto(x + r, y + r + 5.5, str(n), 12, num, 700, anc="middle"))
    xt, wt = x + 2 * r + 9, w - 2 * r - 9
    yy = bloque(o, xt, y + 1, wt, nombre, tam + 1, TINTA, 700, 1.25)
    yy = bloque(o, xt, yy + 1, wt, "Antídoto: " + antidoto, tam, TINTA2, 400, 1.3)
    if n == ERROR_COMUN:
        yy = bloque(o, xt, yy + 1, wt, "la forma más común de quebrar creciendo (§6.3)", tam, NARANJA, 700, 1.3)
    return max(yy, y + 2 * r + 2)


def _errores_escalera(o, x0, y, A, tam):
    tag_w = 128
    o.append(texto(x0, y + 14, "Sobre la escalera: se frenan midiendo ese nivel", 14, TINTA, 700))
    y += 26
    for k in (5, 4, 3, 2, 1):
        nombre = NIVELES[k - 1][1]
        y0, yy = y + 10, y + 10
        for n in ERRORES_NIVEL[k]:
            yy = _error_item(o, x0 + tag_w + 14, yy, A - tag_w - 14, n, tam) + 8
        ht = 12 + 18 + alto(nombre, 12.5, tag_w - 20, 700, 1.22)
        h = max(yy - y0 - 8, ht) + 2
        caja(o, x0, y0, tag_w, h, AZUL_SUAVE if k < 3 else FONDO, AZUL, 1.4, None if k < 3 else "6 4", rx=5)
        o.append(texto(x0 + 10, y0 + 18, f"Nivel {k}", 12, AZUL, 700))
        bloque(o, x0 + 10, y0 + 22, tag_w - 20, nombre, 12.5, TINTA, 700, 1.22)
        y = y0 + h
    return y


def _errores_fuera(o, x0, y, A, tam):
    y = bloque(o, x0, y, A, "Fuera de la escalera: no aparecen en ninguna cuenta", 14, TINTA, 700, 1.25) + 18
    for n in ERRORES_FUERA:
        y = _error_item(o, x0, y, A, n, tam, fuera=True) + 10
    return y - 10


def fig_errores(diagramacion="apaisada"):
    L = Lienzo(diagramacion)
    o = L.o
    L.cabeza("¿Dónde se comete cada uno de los doce errores?",
             "Cada error de la Parte 7 va donde apunta su antídoto: a uno de los cinco niveles, o a una "
             "receta o una prueba que no está en ninguna cuenta.")
    x0, A, y = L.M, L.A, L.y
    if L.ap:
        wl = 0.57 * A
        gap = 30
        yl = _errores_escalera(o, x0, y, wl, 12)
        xr = x0 + wl + gap
        linea(o, xr - gap / 2, y, xr - gap / 2, yl, GRILLA)
        yr = _errores_fuera(o, xr, y, A - wl - gap, 12)
        L.y = max(yl, yr)
    else:
        y = _errores_escalera(o, x0, y, A, 12)
        L.y = _errores_fuera(o, x0, y + 24, A, 12)
    L.pie("Seis de los doce errores se cometen sobre la escalera, y se frenan midiendo el nivel donde ocurren; "
          "los otros seis no aparecen en ninguna cuenta y se frenan con una receta, una prueba o una pregunta.",
          "El error 2, escalar antes de tener margen, se siente como éxito hasta el último mes.",
          "[interpretación] La Parte 7 nombra el nivel sólo en el error 1; en los errores 2, 4 y 7 se deduce del "
          "control o la sección que cita el antídoto (G1, G0, §3.5), y en los errores 6 y 11, de lo que mide el "
          "antídoto (el margen, las duplicaciones). Que el error 2 sea el más común lo afirma el libro (§6.3); "
          "nadie lo midió.")
    return L.svg("Los doce errores, en su lugar",
                 "Los doce errores de la Parte 7 ubicados por su antídoto: seis sobre los cinco niveles (el 4 en el "
                 "nivel 1; el 2 y el 6 en el 2; el 11 en el 3; el 1 en el 4; el 7 en el 5) y seis fuera de la "
                 "escalera (3, 5, 8, 9, 10 y 12).")


FIGURAS = {   # archivo -> función; por orden de aparición en el libro
    "F-00_cinco_niveles": fig_cinco_niveles,
    "F-P1_suma_producto": fig_suma_producto,
    "F-P1_apple_funciones": fig_apple_funciones,
    "F-P2_ford_linea": fig_ford_linea,
    "F-P2_ford_rotacion": fig_ford_rotacion,
    "F-P2_nummi": fig_nummi,
    "F-P2_apple": fig_apple,
    "F-P2_amazon_colchon": fig_amazon_colchon,
    "F-13_marte": fig_marte,
    "F-33_costo_kilo": fig_costo_kilo,
    "F-R9_mismo_cohete": fig_mismo_cohete,
    "F-P2_casi_muerte": fig_casi_muerte,
    "F-N1_avion": fig_avion,
    "F-N2_signo": fig_signo,
    "F-P3_dos_mecanismos": fig_dos_mecanismos,
    "F-N3b_88_contra_millones": fig_88_contra_millones,
    "F-P3_baterias": fig_baterias,
    "F-N3a_piso_del_eje": fig_piso_del_eje,
    "F-N4_lazo": fig_lazo,
    "F-N5a_pozo": fig_pozo,
    "F-N5b_mil_monedas": fig_mil_monedas,
    "F-12_peldano_piso_pozo": fig_peldano,
    "F-41_algoritmo": fig_algoritmo,
    "F-R6_flujo": fig_flujo,
    "F-R11_ciclo_caja": fig_ciclo_caja,
    "F-32_mapa_duplicaciones": fig_mapa_duplicaciones,
    "F-34_reloj": fig_reloj,
    "F-35_segundos": fig_segundos,
    "F-P6_controles": fig_controles,
    "F-P7_errores": fig_errores,
    "F-7_fortuna_producto": fig_fortuna_producto,
    "F-7_pendiente_magnitud": fig_pendiente_magnitud,
    "F-P9_curvas_negocio": fig_curvas_negocio,
    "F-A1_ncr": fig_ncr,
    "F-B4_contenedor": fig_contenedor,
    "F-C5_theranos": fig_theranos,
    "F-D3_proyectos": fig_proyectos,
    "F-D4_concorde": fig_concorde,
    "F-E2_brooks": fig_brooks,
    "F-F1_lista": fig_lista,
    "F-G1_little": fig_little,
    "F-G2_espera": fig_espera,
    "F-G3_amdahl": fig_amdahl,
}

if __name__ == "__main__":
    import sys
    pedidas = sys.argv[1:] or list(FIGURAS)
    for nombre in pedidas:
        f = FIGURAS[nombre]
        for dia, suf in (("apaisada", ""), ("vertical", "_vertical")):
            (AQUI / f"{nombre}{suf}.svg").write_text(f(dia), encoding="utf-8")
        print("escrita", nombre)
