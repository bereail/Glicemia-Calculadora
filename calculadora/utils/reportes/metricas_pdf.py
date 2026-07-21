"""Genera el PDF de métricas replicando el diseño del panel web (tarjetas + gráficos)."""
import math
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas

# ---- Paleta: la misma que usa el panel web (historial.html) ----
FONDO = colors.HexColor("#0a1830")
PANEL = colors.HexColor("#0f2547")
PANEL_BORDE = colors.HexColor("#1c3d68")
BLANCO = colors.white
TEXTO_SUB = colors.HexColor("#9db3cc")
TEXTO_LABEL = colors.HexColor("#8ea3c2")
GRILLA = colors.HexColor("#1a3a63")

AZUL = colors.HexColor("#60a5fa")
VERDE = colors.HexColor("#34d399")
ROJO = colors.HexColor("#f87171")
AMARILLO = colors.HexColor("#fbbf24")
NARANJA = colors.HexColor("#f97316")
INDIGO = colors.HexColor("#818cf8")
GRIS_DOT = colors.HexColor("#9db3cc")
ROJO_OSCURO = colors.HexColor("#991b1b")

MARGEN = 14 * mm


def generar_pdf_metricas(metricas: dict, filtros: dict) -> bytes:
    buffer = BytesIO()
    c = pdfcanvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4
    cw = ancho - 2 * MARGEN  # ancho útil de contenido

    c.setFillColor(FONDO)
    c.rect(0, 0, ancho, alto, stroke=0, fill=1)

    y = alto - MARGEN
    y = _dibujar_encabezado(c, MARGEN, y, cw, filtros)
    y -= 7 * mm

    if metricas["total"] == 0:
        _dibujar_sin_datos(c, MARGEN, y, cw)
    else:
        y = _dibujar_kpis(c, MARGEN, y, cw, metricas)
        y -= 6 * mm
        y = _dibujar_donuts(c, MARGEN, y, cw, metricas, alto_card=52 * mm)
        y -= 6 * mm
        y = _dibujar_evolucion_y_rangos(c, MARGEN, y, cw, metricas, alto_card=56 * mm)
        y -= 6 * mm
        _dibujar_diagnosticos(c, MARGEN, y, cw, metricas)

    _dibujar_pie_pagina(c, ancho)
    c.showPage()
    c.save()
    return buffer.getvalue()


# =========================================================
# BLOQUES
# =========================================================

def _dibujar_encabezado(c, x, y_top, w, filtros):
    c.setFillColor(BLANCO)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(x, y_top - 7 * mm, "METANUTRIC · GLUCIHEEP")

    c.setFont("Helvetica", 10)
    c.setFillColor(AZUL)
    c.drawRightString(x + w, y_top - 7 * mm, "Reporte de métricas")

    y_regla = y_top - 11 * mm
    c.setStrokeColor(PANEL_BORDE)
    c.setLineWidth(0.8)
    c.line(x, y_regla, x + w, y_regla)

    partes = [f"Período: {filtros['periodo_texto']}"]
    if filtros.get("turno_texto"):
        partes.append(f"Turno: {filtros['turno_texto']}")
    if filtros.get("usuario"):
        partes.append(f"Usuario: {filtros['usuario']}")
    if filtros.get("estado"):
        partes.append(f"Estado: {filtros['estado']}")
    partes.append(f"Generado: {filtros['generado']}")

    c.setFont("Helvetica", 8.5)
    c.setFillColor(TEXTO_SUB)
    c.drawString(x, y_regla - 5.5 * mm, "   ·   ".join(partes))

    return y_regla - 5.5 * mm


def _dibujar_sin_datos(c, x, y_top, w):
    alto_card = 40 * mm
    y0 = y_top - alto_card
    c.setFillColor(PANEL)
    c.setStrokeColor(PANEL_BORDE)
    c.roundRect(x, y0, w, alto_card, 4 * mm, stroke=1, fill=1)

    c.setFillColor(TEXTO_SUB)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + w / 2, y0 + alto_card / 2 + 3 * mm, "No se encontraron mediciones")
    c.setFont("Helvetica", 9.5)
    c.drawCentredString(
        x + w / 2, y0 + alto_card / 2 - 4 * mm,
        "No hay mediciones que coincidan con los filtros aplicados.",
    )


def _tarjeta(c, x, y_top, w, h, radio=3.5 * mm):
    y0 = y_top - h
    c.setFillColor(PANEL)
    c.setStrokeColor(PANEL_BORDE)
    c.setLineWidth(0.7)
    c.roundRect(x, y0, w, h, radio, stroke=1, fill=1)
    return y0


def _dibujar_kpis(c, x, y_top, w, m, alto_card=29 * mm):
    tarjetas = [
        ("TOTAL", m["total"], "Mediciones encontradas", AZUL, None),
        ("HIPOGLUCEMIAS", m["hipoglucemias"], "Valores críticos bajos", ROJO, m["pct_hipo"]),
        ("EN OBJETIVO", m["en_objetivo"], "Dentro del rango esperado", VERDE, m["pct_ok"]),
        ("HIPERGLUCEMIAS", m["hiperglucemias"], "Valores por encima del objetivo", AMARILLO, m["pct_hiper"]),
    ]
    gap = 4 * mm
    ancho_card = (w - 3 * gap) / 4
    y0 = y_top - alto_card

    for i, (label, valor, desc, color, pct) in enumerate(tarjetas):
        cx = x + i * (ancho_card + gap)
        _tarjeta(c, cx, y_top, ancho_card, alto_card)

        c.setFillColor(color)
        c.rect(cx, y_top - 1.6 * mm, ancho_card, 1.6 * mm, stroke=0, fill=1)

        pad = 4.5 * mm
        c.setFillColor(TEXTO_LABEL)
        c.setFont("Helvetica-Bold", 7.3)
        c.drawString(cx + pad, y_top - 8 * mm, label)

        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 21)
        c.drawString(cx + pad, y_top - 17 * mm, str(valor))

        c.setFillColor(TEXTO_SUB)
        c.setFont("Helvetica", 6.8)
        c.drawString(cx + pad, y_top - 21.5 * mm, desc)
        if pct is not None:
            c.setFont("Helvetica-Bold", 6.6)
            c.setFillColor(colors.Color(1, 1, 1, alpha=0.45))
            c.drawString(cx + pad, y_top - 25 * mm, f"{pct}% del total")

    return y0


def _titulo_card(c, x, y_top, titulo, subtitulo):
    pad = 5 * mm
    c.setFillColor(TEXTO_LABEL)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + pad, y_top - 6.5 * mm, titulo.upper())
    c.setFillColor(TEXTO_SUB)
    c.setFont("Helvetica", 7.6)
    c.drawString(x + pad, y_top - 10.5 * mm, subtitulo)


def _dibujar_donut(c, cx, cy, r_out, r_in, segmentos):
    """Dibuja cada porción como una torta sólida y perfora el centro con el color
    de fondo de la tarjeta: es más robusto que Wedge(annular=True) de reportlab,
    que deforma los arcos cuando una porción abarca un ángulo grande."""
    total = sum(v for v, _ in segmentos) or 1
    acumulado = 0
    for valor, color in segmentos:
        if valor <= 0:
            continue
        t0 = acumulado / total
        acumulado += valor
        t1 = acumulado / total
        inicio = 90 - t1 * 360
        extent = max((t1 - t0) * 360, 0.3)
        c.setFillColor(color)
        c.setStrokeColor(PANEL)
        c.setLineWidth(1.2)
        c.wedge(cx - r_out, cy - r_out, cx + r_out, cy + r_out, inicio, extent, stroke=1, fill=1)

    c.setFillColor(PANEL)
    c.circle(cx, cy, r_in, stroke=0, fill=1)


def _leyenda_donut(c, x, y_top, w, items):
    c.setFont("Helvetica", 7.6)
    fila_h = 4.6 * mm
    y = y_top
    for label, valor, color in items:
        if not valor:
            continue
        c.setFillColor(color)
        c.circle(x + 1.4 * mm, y - 1.4 * mm, 1.4 * mm, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#d8e5f8"))
        c.drawString(x + 4.5 * mm, y - 2.5 * mm, label)
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawRightString(x + w, y - 2.5 * mm, str(valor))
        c.setFont("Helvetica", 7.6)
        y -= fila_h
    return y


def _dibujar_donuts(c, x, y_top, w, m, alto_card=56 * mm):
    gap = 5 * mm
    ancho_card = (w - 2 * gap) / 3
    y0 = y_top - alto_card

    graficos = [
        (
            "Uso por rol", "Distribución según rol del usuario",
            [
                ("Médicos", m["uso_medicos"], AZUL),
                ("Enfermería", m["uso_enfermeria"], VERDE),
                ("Sin rol", m["uso_sin_grupo"], GRIS_DOT),
            ],
        ),
        (
            "Distribución de estados", "Hipoglucemia / En objetivo / Hiperglucemia",
            [
                ("Hipoglucemias", m["hipoglucemias"], ROJO),
                ("En objetivo", m["en_objetivo"], VERDE),
                ("Hiperglucemias", m["hiperglucemias"], AMARILLO),
            ],
        ),
        (
            "Distribución por turno", "Mañana / Tarde / Noche / Madrugada",
            [
                ("Mañana (06–12)", m["turno_manana"], AMARILLO),
                ("Tarde (12–18)", m["turno_tarde"], NARANJA),
                ("Noche (18–24)", m["turno_noche"], INDIGO),
                ("Madrugada (00–06)", m["turno_madrugada"], AZUL),
            ],
        ),
    ]

    for i, (titulo, sub, items) in enumerate(graficos):
        cx = x + i * (ancho_card + gap)
        _tarjeta(c, cx, y_top, ancho_card, alto_card)
        _titulo_card(c, cx, y_top, titulo, sub)

        valores_colores = [(v, col) for _, v, col in items]
        if sum(v for v, _ in valores_colores) > 0:
            centro_x = cx + 15 * mm
            centro_y = y0 + alto_card - 25 * mm
            _dibujar_donut(c, centro_x, centro_y, 10 * mm, 6.2 * mm, valores_colores)
        else:
            c.setFillColor(TEXTO_SUB)
            c.setFont("Helvetica", 7.6)
            c.drawCentredString(cx + ancho_card / 2, y0 + alto_card - 25 * mm, "Sin datos")

        _leyenda_donut(c, cx + 5 * mm, y0 + 15 * mm, ancho_card - 10 * mm, items)

    return y0


def _dibujar_evolucion_y_rangos(c, x, y_top, w, m, alto_card=62 * mm):
    gap = 5 * mm
    ancho_card = (w - gap) / 2
    y0 = y_top - alto_card

    _dibujar_evolucion(c, x, y_top, ancho_card, alto_card, m)
    _dibujar_rangos(c, x + ancho_card + gap, y_top, ancho_card, alto_card, m)
    return y0


def _dibujar_evolucion(c, x, y_top, w, h, m):
    _tarjeta(c, x, y_top, w, h)
    _titulo_card(c, x, y_top, "Evolución de resultados", "% en objetivo, hipo e hiperglucemia por semana")

    labels = m["lt_labels"]
    series = [
        ("En objetivo (%)", VERDE, m["lt_objetivo"]),
        ("Hiperglucemias (%)", AMARILLO, m["lt_hiper"]),
        ("Hipoglucemias (%)", ROJO, m["lt_hipo"]),
    ]

    leg_y = y_top - 15 * mm
    leg_x = x + 5 * mm
    c.setFont("Helvetica", 6.6)
    for label, color, _ in series:
        c.setFillColor(color)
        c.rect(leg_x, leg_y - 1.6 * mm, 2.6 * mm, 2.6 * mm, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#d8e5f8"))
        c.drawString(leg_x + 4 * mm, leg_y - 1.2 * mm, label)
        leg_x += 4 * mm + c.stringWidth(label, "Helvetica", 6.6) + 6 * mm

    if not labels:
        c.setFillColor(TEXTO_SUB)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + w / 2, y_top - h / 2, "Sin datos suficientes")
        return

    pad_izq, pad_der, pad_abajo, pad_arriba = 11 * mm, 4 * mm, 9 * mm, 20 * mm
    plot_x0 = x + pad_izq
    plot_x1 = x + w - pad_der
    plot_y0 = y_top - h + pad_abajo
    plot_y1 = y_top - pad_arriba
    plot_w = plot_x1 - plot_x0
    plot_h = plot_y1 - plot_y0

    c.setStrokeColor(GRILLA)
    c.setLineWidth(0.4)
    c.setFont("Helvetica", 6.2)
    c.setFillColor(TEXTO_SUB)
    for pct in (0, 25, 50, 75, 100):
        gy = plot_y0 + plot_h * pct / 100
        c.line(plot_x0, gy, plot_x1, gy)
        c.drawRightString(plot_x0 - 1.5 * mm, gy - 1.6 * mm, f"{pct}%")

    n = len(labels)
    paso = max(1, math.ceil(n / 7))
    for i, lbl in enumerate(labels):
        if i % paso != 0 and i != n - 1:
            continue
        px = plot_x0 if n == 1 else plot_x0 + plot_w * i / (n - 1)
        c.drawCentredString(px, plot_y0 - 5 * mm, lbl)

    for _, color, valores in series:
        puntos = [
            (
                plot_x0 if n == 1 else plot_x0 + plot_w * i / (n - 1),
                plot_y0 + plot_h * (v / 100),
            )
            for i, v in enumerate(valores)
        ]
        c.setStrokeColor(color)
        c.setLineWidth(1.4)
        for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
            c.line(x1, y1, x2, y2)
        c.setFillColor(color)
        for px, py in puntos:
            c.circle(px, py, 1.1 * mm, stroke=0, fill=1)


def _dibujar_rangos(c, x, y_top, w, h, m):
    _tarjeta(c, x, y_top, w, h)
    _titulo_card(c, x, y_top, "Distribución por rango de glucemia", "Cantidad de mediciones por rango en mg/dL")

    labels = m["rango_labels"]
    valores = m["rango_datos"]
    colores = [ROJO, VERDE, AZUL, AMARILLO, NARANJA, ROJO_OSCURO]
    maximo = max(valores) or 1

    pad_izq, pad_der = 20 * mm, 12 * mm
    plot_x0 = x + pad_izq
    plot_x1 = x + w - pad_der
    plot_w = plot_x1 - plot_x0

    n = len(labels)
    area_top = y_top - 14 * mm
    area_bottom = y_top - h + 5 * mm
    fila_h = (area_top - area_bottom) / n

    for i, (lbl, val, color) in enumerate(zip(labels, valores, colores)):
        fila_y = area_top - i * fila_h
        centro_y = fila_y - fila_h / 2

        c.setFillColor(colors.HexColor("#d8e5f8"))
        c.setFont("Helvetica-Bold", 7.6)
        c.drawRightString(plot_x0 - 3 * mm, centro_y - 1 * mm, lbl)

        largo = plot_w * (val / maximo)
        alto_barra = min(fila_h * 0.5, 6 * mm)
        if val > 0:
            c.setFillColor(color)
            c.roundRect(plot_x0, centro_y - alto_barra / 2, max(largo, 2 * mm), alto_barra, 1.2 * mm, stroke=0, fill=1)

        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 7.4)
        c.drawString(plot_x0 + largo + 2.5 * mm, centro_y - 1 * mm, str(val))


def _dibujar_diagnosticos(c, x, y_top, w, m, alto_card=64 * mm):
    _tarjeta(c, x, y_top, w, alto_card)
    _titulo_card(
        c, x, y_top,
        "Diagnósticos del control glicémico",
        "Clasificación clínica según protocolo UCI-HEEP (pacientes con TNM sin CAD/EHH)",
    )

    labels = m["dg_labels"]
    valores = m["dg_valores"]
    porcentajes = m["dg_porcentajes"]
    total = m["dg_total"]
    colores = [ROJO, AMARILLO, NARANJA, colors.HexColor("#c2410c"), colors.HexColor("#991b1b")]

    if total == 0:
        c.setFillColor(TEXTO_SUB)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + w / 2, y_top - alto_card / 2, "Sin diagnósticos registrados en este período")
        return

    pad_izq, pad_der = 46 * mm, 12 * mm
    plot_x0 = x + pad_izq
    plot_x1 = x + w - pad_der
    plot_w = plot_x1 - plot_x0
    maximo = max(valores) or 1

    n = len(labels)
    area_top = y_top - 14 * mm
    area_bottom = y_top - 33 * mm
    fila_h = (area_top - area_bottom) / n

    for i, (lbl, val, color) in enumerate(zip(labels, valores, colores)):
        fila_y = area_top - i * fila_h
        centro_y = fila_y - fila_h / 2

        c.setFillColor(colors.HexColor("#d8e5f8"))
        c.setFont("Helvetica-Bold", 7.4)
        c.drawRightString(plot_x0 - 3 * mm, centro_y - 1 * mm, lbl)

        largo = plot_w * (val / maximo)
        alto_barra = min(fila_h * 0.55, 5.5 * mm)
        if val > 0:
            c.setFillColor(color)
            c.roundRect(plot_x0, centro_y - alto_barra / 2, max(largo, 2 * mm), alto_barra, 1 * mm, stroke=0, fill=1)

        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(plot_x0 + largo + 2.5 * mm, centro_y - 1 * mm, str(val))

    # ---- Mini tabla: Porcentaje / Cantidad de veces por diagnóstico ----
    tabla_y_top = y_top - alto_card + 20 * mm
    pad_tabla = 5 * mm
    tabla_x0 = x + pad_tabla
    tabla_w = w - 2 * pad_tabla
    n_cols = len(labels) + 2  # etiqueta de fila + diagnósticos + total
    col_w = tabla_w / n_cols
    fila_alto = 5.6 * mm

    encabezados = [""] + labels + ["Total"]
    fila_pct = ["Porcentaje"] + [f"{p}%" for p in porcentajes] + ["100%"]
    fila_cant = ["Cantidad de veces"] + [str(v) for v in valores] + [str(total)]

    for fila_idx, contenido in enumerate([encabezados, fila_pct, fila_cant]):
        fila_y = tabla_y_top - fila_idx * fila_alto
        es_header = fila_idx == 0
        c.setFillColor(colors.HexColor("#132a4a") if es_header else PANEL)
        c.rect(tabla_x0, fila_y - fila_alto, tabla_w, fila_alto, stroke=0, fill=1)
        c.setStrokeColor(PANEL_BORDE)
        c.setLineWidth(0.4)
        c.line(tabla_x0, fila_y - fila_alto, tabla_x0 + tabla_w, fila_y - fila_alto)

        for col_idx, texto in enumerate(contenido):
            centro_x = tabla_x0 + col_idx * col_w + col_w / 2
            centro_y_txt = fila_y - fila_alto / 2 - 1 * mm
            if col_idx == 0:
                c.setFillColor(TEXTO_SUB)
                c.setFont("Helvetica-Bold", 6.8)
                c.drawString(tabla_x0 + 2 * mm, centro_y_txt, texto)
                continue
            if es_header:
                c.setFillColor(TEXTO_LABEL)
                c.setFont("Helvetica-Bold", 6.2)
            elif col_idx == n_cols - 1:
                c.setFillColor(BLANCO)
                c.setFont("Helvetica-Bold", 6.8)
            else:
                c.setFillColor(colors.HexColor("#d8e5f8"))
                c.setFont("Helvetica", 6.8)
            c.drawCentredString(centro_x, centro_y_txt, texto)


def _dibujar_pie_pagina(c, ancho):
    c.setFillColor(TEXTO_SUB)
    c.setFont("Helvetica", 7)
    c.drawCentredString(ancho / 2, 9 * mm, "METANUTRIC · GLUCIHEEP — Reporte de uso clínico interno")
