"""Genera el PDF de exportación del registro de mediciones (tabla filtrada)."""
from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AZUL_HEADER = colors.HexColor("#0f2547")
BORDE = colors.HexColor("#c7d3e0")
FILA_PAR = colors.HexColor("#eef3fa")
GRIS_TEXTO = colors.HexColor("#4b5563")

COLOR_HIPO = colors.HexColor("#dc2626")
COLOR_HIPER = colors.HexColor("#d97706")
COLOR_OK = colors.HexColor("#059669")
COLOR_NEUTRO = colors.HexColor("#6b7280")

COLOR_POR_CLASE = {
    "hipoglucemia": COLOR_HIPO,
    "post_hipoglucemia": COLOR_HIPER,
    "hiperglucemia": COLOR_HIPER,
    "en_rango": COLOR_OK,
}

ESTILO_CONDUCTA = ParagraphStyle("conducta", fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=colors.HexColor("#1f2937"))
ESTILO_CELDA = ParagraphStyle("celda", fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#1f2937"))

_ESTILOS_ESTADO_POR_CLASE = {
    nombre_clase: ParagraphStyle(f"estado_{nombre_clase}", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=color)
    for nombre_clase, color in COLOR_POR_CLASE.items()
}
_ESTILO_ESTADO_NEUTRO = ParagraphStyle("estado_neutro", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=COLOR_NEUTRO)


def _estilo_estado(clase):
    return _ESTILOS_ESTADO_POR_CLASE.get(clase, _ESTILO_ESTADO_NEUTRO)


def _resumen_filtros(filtros: dict) -> str:
    partes = [f"Período: {filtros['periodo_texto']}"]
    if filtros.get("turno_texto"):
        partes.append(f"Turno: {filtros['turno_texto']}")
    if filtros.get("usuario"):
        partes.append(f"Usuario: {filtros['usuario']}")
    if filtros.get("estado"):
        partes.append(f"Estado: {filtros['estado']}")
    if filtros.get("clase"):
        partes.append(f"Clase: {filtros['clase']}")
    partes.append(f"Generado: {filtros['generado']}")
    return "   ·   ".join(partes)


def generar_pdf_registro(mediciones, filtros: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    elementos = []

    elementos.append(Paragraph(
        "METANUTRIC · GLUCIHEEP — Reporte de mediciones",
        ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=15, textColor=AZUL_HEADER),
    ))
    elementos.append(Spacer(1, 3 * mm))
    elementos.append(Paragraph(
        _resumen_filtros(filtros),
        ParagraphStyle("filtros", fontName="Helvetica", fontSize=8.5, textColor=GRIS_TEXTO),
    ))
    elementos.append(Spacer(1, 5 * mm))

    encabezados = ["Fecha", "Usuario", "Actual", "Previa", "Infusión", "Estado", "Conducta"]
    filas = [encabezados]
    clases_fila = []

    for m in mediciones:
        clases_fila.append(m.clase)
        filas.append([
            timezone.localtime(m.fecha_hora).strftime("%d/%m/%Y %H:%M"),
            Paragraph(m.usuario.username if m.usuario else "—", ESTILO_CELDA),
            f"{m.glicemia_actual}",
            f"{m.glicemia_previa}" if m.glicemia_previa is not None else "—",
            "Sí" if m.infusion_activa else "No",
            Paragraph(m.estado or "—", _estilo_estado(m.clase)),
            Paragraph((m.conducta or "—").replace("<br>", "<br/>"), ESTILO_CONDUCTA),
        ])

    col_widths = [26 * mm, 30 * mm, 15 * mm, 15 * mm, 15 * mm, 50 * mm, 126 * mm]
    tabla = Table(filas, colWidths=col_widths, repeatRows=1)

    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("ALIGN", (2, 0), (4, -1), "CENTER"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 1), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (4, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, AZUL_HEADER),
    ]

    for i, clase in enumerate(clases_fila, start=1):
        if i % 2 == 0:
            estilos.append(("BACKGROUND", (0, i), (-1, i), FILA_PAR))
        color_acento = COLOR_POR_CLASE.get(clase)
        if color_acento:
            estilos.append(("LINEBEFORE", (0, i), (0, i), 2.4, color_acento))

    tabla.setStyle(TableStyle(estilos))
    elementos.append(tabla)
    doc.build(elementos)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
