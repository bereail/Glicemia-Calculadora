from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import timedelta
from io import BytesIO
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .forms import PasoInicialForm, GlucemiaForm
from .models import MedicionGlucemia
from .services import resolver_flujo_glucemia
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from .forms import PasoInicialForm, GlucemiaForm
from .models import MedicionGlucemia
from .services import resolver_flujo_glucemia


# Objetivo glucémico general usado en el flujo guiado
OBJ_MIN = Decimal("140")
OBJ_MAX = Decimal("200")


def control_glicemia_view(request):
    """
    Vista simple:
    - recibe glucemia actual
    - recibe si el paciente está insulinizado
    - recibe glucemia previa opcional
    - delega la lógica clínica al service resolver_flujo_glucemia
    """
    resultado = None

    if request.method == "POST":
        form = GlucemiaForm(request.POST)
        if form.is_valid():
            actual = form.cleaned_data["glicemia_actual"]
            insulinizado = form.cleaned_data["paciente_insulinizado"]
            previa = form.cleaned_data.get("glicemia_previa")

            # OJO:
            # La función del service espera actual / insulinizado / previa
            resultado = resolver_flujo_glucemia(
                actual=actual,
                insulinizado=insulinizado,
                previa=previa,
            )
    else:
        form = GlucemiaForm()

    return render(
        request,
        "calculadora/control_glicemia.html",
        {
            "form": form,
            "resultado": resultado,
        },
    )


def evaluar_flujo_guiado(
    glicemia_actual,
    glicemia_previa,
    infusion_actual=None,
    mayor_200=None,
    hgp=None,
):
    """
    Evalúa el flujo guiado manual en pasos.

    Este flujo NO reemplaza la lógica del service principal.
    Sirve para mostrar bloques visuales / decisiones guiadas
    según las respuestas del usuario.
    """
    actual = Decimal(str(glicemia_actual))
    previa = Decimal(str(glicemia_previa))

    resultado = {
        "paso": "inicial",
        "bloque_principal": None,
        "bloque_secundario": None,
        "mostrar_infusion_actual": False,
        "mostrar_mayor_200": False,
        "mostrar_hgp": False,
        "finalizado": False,
    }

    # 1) PRIORIDAD ABSOLUTA:
    # Si actual y previa son >= 180, hay hiperglucemia sostenida
    if actual >= Decimal("180") and previa >= Decimal("180"):
        resultado["bloque_principal"] = {
            "titulo": "Hiperglucemia sostenida",
            "mensaje": [
                "Glicemia actual y previa ≥ 180 mg/dL",
                "Evaluar inicio de infusión EV",
                "Pasar a infusión inicial",
            ],
            "rojo": True,
        }
        resultado["mostrar_infusion_actual"] = True
        return continuar_flujo(resultado, infusion_actual, mayor_200, hgp)

    # 2) Recién después evaluar si está en objetivo
    if OBJ_MIN <= actual <= OBJ_MAX:
        resultado["bloque_principal"] = {
            "titulo": "En objetivo",
            "mensaje": [
                "Dentro del rango objetivo",
                "Continuar monitoreo glucémico",
            ],
            "rojo": False,
        }
        resultado["finalizado"] = True
        return resultado

    # 3) Todo lo demás queda como fuera de objetivo
    resultado["bloque_principal"] = {
        "titulo": "Fuera de objetivo",
        "mensaje": [
            "Continuar evaluación clínica",
        ],
        "rojo": False,
    }
    resultado["finalizado"] = True
    return resultado


def continuar_flujo(resultado, infusion_actual, mayor_200, hgp):
    """
    Continúa el flujo guiado una vez detectada hiperglucemia sostenida.
    """

    # Todavía no respondieron si hay infusión actual
    if infusion_actual is None:
        return resultado

    # Si NO hay infusión actual
    if infusion_actual == "no":
        resultado["bloque_secundario"] = {
            "titulo": "Conducta",
            "mensaje": [
                "Seguir algoritmo 1",
                "Definir próximo control",
                "Sugerir monitoreo glucémico",
            ],
            "rojo": False,
        }
        resultado["finalizado"] = True
        return resultado

    # Si sí hay infusión actual, preguntar si sigue > 200
    resultado["mostrar_mayor_200"] = True

    if mayor_200 is None:
        return resultado

    # Si NO es mayor a 200
    if mayor_200 == "no":
        resultado["bloque_secundario"] = {
            "titulo": "Conducta",
            "mensaje": [
                "Seguir algoritmo 1",
                "Definir próximo control",
                "Sugerir monitoreo glucémico",
            ],
            "rojo": False,
        }
        resultado["finalizado"] = True
        return resultado

    # Si sí es > 200, preguntar si cumple HGP
    resultado["mostrar_hgp"] = True

    if hgp is None:
        return resultado

    if hgp == "si":
        resultado["bloque_secundario"] = {
            "titulo": "Dar aviso a médico de guardia",
            "mensaje": [
                "Pasar a algoritmo 2",
            ],
            "rojo": True,
        }
    else:
        resultado["bloque_secundario"] = {
            "titulo": "Conducta",
            "mensaje": [
                "Continuar algoritmo 1",
                "Monitoreo glucémico",
            ],
            "rojo": False,
        }

    resultado["finalizado"] = True
    return resultado


# Tablas de algoritmos
ALG1 = [
    (None, 119, None),
    (120, 149, 0.5),
    (150, 179, 1),
    (180, 209, 1.5),
    (210, 239, 2),
    (240, 269, 2.5),
    (270, 299, 3),
    (300, 329, 3.5),
    (330, 359, 4),
    (360, None, 5),
]

ALG2 = [
    (None, 119, None),
    (120, 149, 1),
    (150, 179, 1.5),
    (180, 209, 2.5),
    (210, 239, 3),
    (240, 269, 3.5),
    (270, 299, 4),
    (300, 329, 5),
    (330, 359, 6),
    (360, None, 8),
]


def calculadora_guiada(request):
    """
    Vista principal guiada.

    Corrige el error que había en el archivo:
    - se llamaba a resolver_flujo_glicemia (mal)
    - se enviaban parámetros glicemia_actual / glicemia_previa (mal)
    """
    resultado = None

    if request.method == "POST":
        form = PasoInicialForm(request.POST)
        if form.is_valid():
            glicemia_actual = form.cleaned_data["glicemia_actual"]
            insulinizado = form.cleaned_data["insulinizado"]
            glicemia_previa = form.cleaned_data.get("glicemia_previa")

            # La función correcta es resolver_flujo_glucemia
            # y espera actual / insulinizado / previa
            resultado = resolver_flujo_glucemia(
                actual=glicemia_actual,
                insulinizado=insulinizado,
                previa=glicemia_previa,
            )
    else:
        form = PasoInicialForm()

    return render(
        request,
        "calculadora/home.html",
        {
            "form": form,
            "resultado": resultado,
        },
    )


def obtener_escalon(glucemia, tabla):
    """
    Devuelve el índice del escalón y la tasa correspondiente
    según la glucemia y la tabla recibida.
    """
    for i, (minimo, maximo, tasa) in enumerate(tabla):
        ok_min = minimo is None or glucemia >= minimo
        ok_max = maximo is None or glucemia <= maximo
        if ok_min and ok_max:
            return i, tasa
    return None, None


def es_hgp_algoritmo_1(
    g1,
    g2,
    ultimo_escalon=False,
    subio_ultimas_2=False,
    mismo_escalon_3=False,
):
    """
    HGP en algoritmo 1:
    - glucemia actual > 200
    - glucemia previa > 200
    - y además se cumple alguno de estos criterios:
      - último escalón
      - subió escalón en últimas 2
      - mismo escalón en 3 controles
    """
    return (
        g1 > 200
        and g2 > 200
        and (ultimo_escalon or subio_ultimas_2 or mismo_escalon_3)
    )


def es_hgr_algoritmo_2(g1, g2, ultimo_escalon=False):
    """
    HGR en algoritmo 2:
    - glucemia actual > 360
    - glucemia previa > 360
    - y estar en último escalón del algoritmo 2
    """
    return g1 > 360 and g2 > 360 and ultimo_escalon


def tiene_acceso_home(user):
    """
    Permite acceso solo a:
    - superusuarios
    - grupo Enfermeria
    - grupo Medicos
    """
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name="Enfermeria").exists()
        or user.groups.filter(name="Medicos").exists()
    )


def _get_mode_label(modo: str) -> str:
    """
    Etiqueta legible para el modo de cálculo.
    """
    labels = {
        "inicio": "Inicio / Reinicio (Algoritmo 1)",
        "alg2": "Seguimiento - Algoritmo 2",
    }
    return labels.get(modo, "No definido")


def _in_range(g, lo, hi):
    """
    Evalúa si un valor está dentro de un rango.
    Soporta extremos None.
    """
    if lo is None and hi is None:
        return True
    if lo is None:
        return g <= hi
    if hi is None:
        return g >= lo
    return lo <= g <= hi


def _monitoring_text(g: int) -> str:
    """
    Devuelve el texto de monitoreo glucémico según el valor.
    """
    if g > 400:
        return "Cada 1 hora"
    if 300 <= g <= 400:
        return "Cada 2 horas"
    if 200 <= g < 300:
        return "Cada 4 horas (primeras 24 h) y luego cada 6 h si estable"
    return "Cada 6 horas si permanece estable"


def _rate_from_table(g, table):
    """
    Busca la tasa correspondiente a una glucemia dentro de una tabla.
    """
    for lo, hi, rate in table:
        if _in_range(g, lo, hi):
            return rate
    return None


def _round_to_half(x: Decimal) -> Decimal:
    """
    Redondea al 0.5 más cercano.
    """
    return (x * 2).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 2


def _safe_decimal_text(value):
    """
    Devuelve un texto amigable para mostrar una tasa.
    """
    if value is None:
        return "—"
    return f"{value} UI/h"


def _normalizar_infusion_activa(value):
    """
    Convierte el valor del formulario a bool de forma segura.
    Sirve si el campo devuelve bool real o choices tipo
    'si'/'no', '1'/'0', etc.
    """
    if isinstance(value, bool):
        return value

    if value in (None, "", 0, "0", "false", "False", "no", "No"):
        return False

    if value in (1, "1", "true", "True", "si", "sí", "Si", "Sí", "activa", "Activa"):
        return True

    return False


def _filtrar_mediciones_desde_request(request):
    """
    Filtra mediciones por:
    - usuario
    - estado
    - periodo (semanal / mensual)
    """
    usuario = request.GET.get("usuario", "").strip()
    estado = request.GET.get("estado", "").strip()
    periodo = request.GET.get("periodo", "").strip().lower()

    mediciones = (
        MedicionGlucemia.objects
        .select_related("usuario")
        .all()
        .order_by("-fecha_hora")
    )

    if usuario:
        mediciones = mediciones.filter(usuario__username=usuario)

    if estado:
        mediciones = mediciones.filter(estado=estado)

    ahora = timezone.now()

    if periodo == "semanal":
        desde = ahora - timedelta(days=7)
        mediciones = mediciones.filter(fecha_hora__gte=desde)
    elif periodo == "mensual":
        desde = ahora - timedelta(days=30)
        mediciones = mediciones.filter(fecha_hora__gte=desde)

    return mediciones, usuario, estado, periodo

####################################################################################################

@login_required
@user_passes_test(tiene_acceso_home, login_url="/login/")
def historial(request):
    mediciones_qs, usuario_seleccionado, estado_seleccionado, periodo = _filtrar_mediciones_desde_request(request)

    total = mediciones_qs.count()
    hipoglucemias = mediciones_qs.filter(estado="Hipoglucemia").count()
    en_objetivo = mediciones_qs.filter(estado="En objetivo").count()
    hiperglucemias = mediciones_qs.filter(estado="Hiperglucemia").count()

    mediciones = mediciones_qs[:50]

    usuarios = (
        MedicionGlucemia.objects.values_list("usuario__username", flat=True)
        .distinct()
        .order_by("usuario__username")
    )

    estados = (
        MedicionGlucemia.objects.values_list("estado", flat=True)
        .distinct()
        .order_by("estado")
    )

    return render(
        request,
        "calculadora/historial.html",
        {
            "mediciones": mediciones,
            "usuarios": usuarios,
            "estados": estados,
            "usuario_seleccionado": usuario_seleccionado,
            "estado_seleccionado": estado_seleccionado,
            "periodo_seleccionado": periodo,
            "total": total,
            "hipoglucemias": hipoglucemias,
            "en_objetivo": en_objetivo,
            "hiperglucemias": hiperglucemias,
        },
    )


@login_required
@user_passes_test(tiene_acceso_home, login_url="/login/")
def exportar_historial_excel(request):
    mediciones, usuario, estado, periodo = _filtrar_mediciones_desde_request(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Historial"

    titulo = f"Reporte de mediciones - {periodo or 'completo'}"
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=14)

    ws["A2"] = f"Usuario: {usuario or 'Todos'}"
    ws["B2"] = f"Estado: {estado or 'Todos'}"
    ws["C2"] = f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}"

    headers = ["Fecha", "Usuario", "Glucemia", "Modo", "Estado", "Conducta", "Tendencia"]
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    fila_header = 4
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=fila_header, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    fila = 5
    for m in mediciones:
        ws.cell(row=fila, column=1, value=timezone.localtime(m.fecha_hora).strftime("%d/%m/%Y %H:%M"))
        ws.cell(row=fila, column=2, value=m.usuario.username if m.usuario else "")
        ws.cell(row=fila, column=3, value=f"{m.glucemia} mg/dL")
        ws.cell(row=fila, column=4, value=m.get_modo_display())
        ws.cell(row=fila, column=5, value=m.estado)
        ws.cell(row=fila, column=6, value=m.conducta)
        ws.cell(row=fila, column=7, value=m.tendencia or "")
        fila += 1

    widths = {
        "A": 18,
        "B": 18,
        "C": 14,
        "D": 28,
        "E": 18,
        "F": 30,
        "G": 18,
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    nombre = f"historial_{periodo or 'completo'}.xlsx"
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return response


@login_required
@user_passes_test(tiene_acceso_home, login_url="/login/")
def exportar_historial_pdf(request):
    mediciones, usuario, estado, periodo = _filtrar_mediciones_desde_request(request)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Reporte de mediciones - {periodo or 'completo'}", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Usuario: {usuario or 'Todos'}", styles["Normal"]))
    elements.append(Paragraph(f"Estado: {estado or 'Todos'}", styles["Normal"]))
    elements.append(Paragraph(f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [[
        "Fecha",
        "Usuario",
        "Glucemia",
        "Modo",
        "Estado",
        "Conducta",
        "Tendencia",
    ]]

    for m in mediciones:
        data.append([
            timezone.localtime(m.fecha_hora).strftime("%d/%m/%Y %H:%M"),
            m.usuario.username if m.usuario else "",
            f"{m.glucemia} mg/dL",
            m.get_modo_display(),
            m.estado,
            m.conducta,
            m.tendencia or "",
        ])

    table = Table(
        data,
        colWidths=[30 * mm, 28 * mm, 22 * mm, 45 * mm, 28 * mm, 55 * mm, 25 * mm]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D3E0")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    nombre = f"historial_{periodo or 'completo'}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return response


@login_required
@user_passes_test(tiene_acceso_home, login_url="/login/")
def home(request):
    resultado = None

    if request.method == "POST":
        form = PasoInicialForm(request.POST)
        if form.is_valid():
            glicemia_actual = form.cleaned_data["glicemia_actual"]
            insulinizado = form.cleaned_data["insulinizado"]
            glicemia_previa = form.cleaned_data.get("glicemia_previa")

            resultado = resolver_flujo_glicemia(
                glicemia_actual=glicemia_actual,
                insulinizado=insulinizado,
                glicemia_previa=glicemia_previa,
            )
    else:
        form = PasoInicialForm()

    return render(
        request,
        "calculadora/home.html",
        {
            "form": form,
            "resultado": resultado,
        },
    )