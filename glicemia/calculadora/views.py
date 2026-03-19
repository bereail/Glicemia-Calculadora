from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import timedelta
from io import BytesIO
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.shortcuts import render
from .forms import GlucemiaGuiadaForm, CalculadoraGuiadaPaso1Form
from .models import MedicionGlucemia
from .forms import GlucemiaForm
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views import View
from .forms import (
    PasoInicialForm,
    InfusionActivaForm,
    AlgoritmoActualForm,
    CriteriosHGPForm,
    UltimoEscalonAlg2Form,
)
from .services import (
    evaluar_paso_inicial,
    evaluar_infusion_activa,
    evaluar_algoritmo_1,
    evaluar_algoritmo_2,
)

OBJ_MIN = 140
OBJ_MAX = 200

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


def obtener_escalon(glucemia, tabla):
    for i, (minimo, maximo, tasa) in enumerate(tabla):
        ok_min = minimo is None or glucemia >= minimo
        ok_max = maximo is None or glucemia <= maximo
        if ok_min and ok_max:
            return i, tasa
    return None, None


def es_hgp_algoritmo_1(g1, g2, ultimo_escalon=False, subio_ultimas_2=False, mismo_escalon_3=False):
    """
    HGP:
    - glicemia actual > 200
    - glicemia previa > 200
    - y además se cumple alguno de estos criterios:
      - último escalón
      - subió escalón en últimas 2
      - mismo escalón en 3 controles
    """
    return (
        g1 > 200 and
        g2 > 200 and
        (ultimo_escalon or subio_ultimas_2 or mismo_escalon_3)
    )


def es_hgr_algoritmo_2(g1, g2, ultimo_escalon=False):
    """
    HGR:
    - glicemia actual > 360
    - glicemia previa > 360
    - y estar en último escalón del algoritmo 2
    """
    return g1 > 360 and g2 > 360 and ultimo_escalon


def calculadora_guiada(request):
    contexto = {
        "glucemia_actual": "",
        "glucemia_previa": "",
        "infusion_activa": "",
        "algoritmo": "",
        "ultimo_escalon_hgp": "",
        "subio_ultimas_2": "",
        "mismo_escalon_3": "",
        "ultimo_escalon_alg2": "",
        "resultado": None,
        "error_general": None,
        "mostrar_infusion_activa": False,
        "mostrar_algoritmo": False,
        "mostrar_hgp": False,
        "mostrar_hgr": False,
        "titulo_resultado": "",
        "mensaje_resultado": "",
    }

    if request.method == "POST":
        glucemia_actual = request.POST.get("glucemia_actual", "").strip()
        glucemia_previa = request.POST.get("glucemia_previa", "").strip()
        infusion_activa = request.POST.get("infusion_activa", "").strip()
        algoritmo = request.POST.get("algoritmo", "").strip()

        ultimo_escalon_hgp = request.POST.get("ultimo_escalon_hgp", "").strip()
        subio_ultimas_2 = request.POST.get("subio_ultimas_2", "").strip()
        mismo_escalon_3 = request.POST.get("mismo_escalon_3", "").strip()
        ultimo_escalon_alg2 = request.POST.get("ultimo_escalon_alg2", "").strip()

        contexto["glucemia_actual"] = glucemia_actual
        contexto["glucemia_previa"] = glucemia_previa
        contexto["infusion_activa"] = infusion_activa
        contexto["algoritmo"] = algoritmo
        contexto["ultimo_escalon_hgp"] = ultimo_escalon_hgp
        contexto["subio_ultimas_2"] = subio_ultimas_2
        contexto["mismo_escalon_3"] = mismo_escalon_3
        contexto["ultimo_escalon_alg2"] = ultimo_escalon_alg2

        try:
            ga = int(glucemia_actual) if glucemia_actual else None
            gp = int(glucemia_previa) if glucemia_previa else None
        except ValueError:
            contexto["error_general"] = "Los valores de glicemia deben ser numéricos."
            return render(request, "calculadora/guiada.html", contexto)

        if ga is None or gp is None:
            contexto["error_general"] = "Debés ingresar la glicemia actual y la previa."
            return render(request, "calculadora/guiada.html", contexto)

        # Paso 1: evaluación inicial
        if ga < 70:
            contexto["resultado"] = True
            contexto["titulo_resultado"] = "Hipoglucemia"
            contexto["mensaje_resultado"] = "La glicemia actual es menor a 70 mg/dL."
            return render(request, "calculadora/guiada.html", contexto)

        if 70 <= ga <= 119:
            contexto["resultado"] = True
            contexto["titulo_resultado"] = "Suspender infusión"
            contexto["mensaje_resultado"] = "La glicemia actual está entre 70 y 119 mg/dL. Corresponde suspender infusión."
            return render(request, "calculadora/guiada.html", contexto)

        # Si llegó hasta acá, mostrar siguiente pregunta
        contexto["mostrar_infusion_activa"] = True

        # Si todavía no respondió infusión activa, volver mostrando esa pregunta
        if infusion_activa not in ["si", "no"]:
            return render(request, "calculadora/guiada.html", contexto)

        # Paso 2: hiperglucemia sostenida
        if not (ga >= 180 and gp >= 180):
            contexto["resultado"] = True
            contexto["titulo_resultado"] = "Sin hiperglucemia sostenida"
            contexto["mensaje_resultado"] = "No cumple criterio de hiperglucemia sostenida. Continuar control."
            return render(request, "calculadora/guiada.html", contexto)

        # Paso 3: infusión activa
        if infusion_activa == "no":
            contexto["resultado"] = True
            contexto["titulo_resultado"] = "Iniciar manejo"
            contexto["mensaje_resultado"] = "No hay infusión activa. Iniciar bolo inicial, comenzar Algoritmo 1 y realizar monitoreo."
            return render(request, "calculadora/guiada.html", contexto)

        # Si hay infusión activa, mostrar algoritmo
        contexto["mostrar_algoritmo"] = True

        if algoritmo not in ["alg1", "alg2"]:
            return render(request, "calculadora/guiada.html", contexto)

        # Paso 4A: Algoritmo 1
        if algoritmo == "alg1":
            contexto["mostrar_hgp"] = True

            if ga <= 200 or gp <= 200:
                contexto["resultado"] = True
                contexto["titulo_resultado"] = "Continuar Algoritmo 1"
                contexto["mensaje_resultado"] = "No cumple criterio base de HGP. Ajustar tasa y recontrol."
                return render(request, "calculadora/guiada.html", contexto)

            # Esperar a que responda criterios HGP
            if (
                ultimo_escalon_hgp not in ["si", "no"] or
                subio_ultimas_2 not in ["si", "no"] or
                mismo_escalon_3 not in ["si", "no"]
            ):
                return render(request, "calculadora/guiada.html", contexto)

            hgp = es_hgp_algoritmo_1(
                ga,
                gp,
                ultimo_escalon=(ultimo_escalon_hgp == "si"),
                subio_ultimas_2=(subio_ultimas_2 == "si"),
                mismo_escalon_3=(mismo_escalon_3 == "si"),
            )

            contexto["resultado"] = True
            if hgp:
                contexto["titulo_resultado"] = "HGP"
                contexto["mensaje_resultado"] = "Cumple criterios de hiperglucemia persistente. Corresponde pasar a Algoritmo 2."
            else:
                contexto["titulo_resultado"] = "Continuar Algoritmo 1"
                contexto["mensaje_resultado"] = "No cumple criterios de HGP. Ajustar tasa y recontrol."

            return render(request, "calculadora/guiada.html", contexto)

        # Paso 4B: Algoritmo 2
        if algoritmo == "alg2":
            contexto["mostrar_hgr"] = True

            if ga <= 360 or gp <= 360:
                contexto["resultado"] = True
                contexto["titulo_resultado"] = "Continuar Algoritmo 2"
                contexto["mensaje_resultado"] = "No cumple criterio de hiperglucemia refractaria. Recontrol."
                return render(request, "calculadora/guiada.html", contexto)

            if ultimo_escalon_alg2 not in ["si", "no"]:
                return render(request, "calculadora/guiada.html", contexto)

            hgr = es_hgr_algoritmo_2(
                ga,
                gp,
                ultimo_escalon=(ultimo_escalon_alg2 == "si"),
            )

            contexto["resultado"] = True
            if hgr:
                contexto["titulo_resultado"] = "Hiperglucemia refractaria"
                contexto["mensaje_resultado"] = "Cumple criterio y está en último escalón del Algoritmo 2. Avisar médico."
            else:
                contexto["titulo_resultado"] = "Continuar Algoritmo 2"
                contexto["mensaje_resultado"] = "Cumple glicemias > 360 pero no está en último escalón. Continuar Algoritmo 2 y recontrol."

            return render(request, "calculadora/guiada.html", contexto)

    return render(request, "calculadora/guiada.html", contexto)





def tiene_acceso_home(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name="Enfermeria").exists()
        or user.groups.filter(name="Medicos").exists()
    )


def _get_mode_label(modo: str) -> str:
    labels = {
        "inicio": "Inicio / Reinicio (Algoritmo 1)",
        "alg2": "Seguimiento - Algoritmo 2",
    }
    return labels.get(modo, "No definido")


def _in_range(g, lo, hi):
    if lo is None and hi is None:
        return True
    if lo is None:
        return g <= hi
    if hi is None:
        return g >= lo
    return lo <= g <= hi


def _monitoring_text(g: int) -> str:
    if g > 400:
        return "Cada 1 hora"
    if 300 <= g <= 400:
        return "Cada 2 horas"
    if 200 <= g < 300:
        return "Cada 4 horas (primeras 24 h) y luego cada 6 h si estable"
    return "Cada 6 horas si permanece estable"


def _rate_from_table(g, table):
    for lo, hi, rate in table:
        if _in_range(g, lo, hi):
            return rate
    return None


def _round_to_half(x: Decimal) -> Decimal:
    return (x * 2).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 2


def _safe_decimal_text(value):
    if value is None:
        return "—"
    return f"{value} UI/h"


def _normalizar_infusion_activa(value):
    """
    Convierte el valor del formulario a bool de forma segura.
    Sirve si el campo devuelve bool real o choices tipo 'si'/'no', '1'/'0', etc.
    """
    if isinstance(value, bool):
        return value

    if value in (None, "", 0, "0", "false", "False", "no", "No"):
        return False

    if value in (1, "1", "true", "True", "si", "sí", "Si", "Sí", "activa", "Activa"):
        return True

    return False


def _filtrar_mediciones_desde_request(request):
    usuario = request.GET.get("usuario", "").strip()
    estado = request.GET.get("estado", "").strip()
    periodo = request.GET.get("periodo", "").strip().lower()

    mediciones = MedicionGlucemia.objects.select_related("usuario").all().order_by("-fecha_hora")

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
    form = GlucemiaForm(request.POST or None)
    resultado = None
    error_general = None

    if request.method == "POST":
        if form.is_valid():
            try:
                g = int(form.cleaned_data["glucemia"])
                modo = form.cleaned_data["modo"]
                infusion_activa_raw = form.cleaned_data.get("infusion_activa")
                infusion_activa = _normalizar_infusion_activa(infusion_activa_raw)
                glucemia_previa = form.cleaned_data.get("glucemia_previa")

                rango_objetivo = f"{OBJ_MIN}–{OBJ_MAX} mg/dL"
                modo_label = _get_mode_label(modo)

                es_hipoglucemia = g < 70
                suspender = g < 120

                algoritmo_usado = None
                velocidad_sugerida = None

                if modo == "inicio":
                    algoritmo_usado = "Inicio / Reinicio (Algoritmo 1)"
                    velocidad_sugerida = _rate_from_table(g, ALG1)
                elif modo == "alg2":
                    algoritmo_usado = "Seguimiento - Algoritmo 2"
                    velocidad_sugerida = _rate_from_table(g, ALG2)
                else:
                    algoritmo_usado = "No definido"

                bolo_ui = None
                tasa_inicial_ui_h = None

                if modo == "inicio" and not suspender and g >= 180:
                    base = _round_to_half(Decimal(g) / Decimal("100"))
                    bolo_ui = base
                    tasa_inicial_ui_h = base

                proximo_control = _monitoring_text(g)

                gt360_streak = int(request.session.get("gt360_streak", 0))
                if g > 360:
                    gt360_streak += 1
                else:
                    gt360_streak = 0
                request.session["gt360_streak"] = gt360_streak

                alerta_hgr = gt360_streak >= 2

                observacion = ""
                hero_text = "—"

                if es_hipoglucemia:
                    estado = "Hipoglucemia"
                    clase = "danger"
                    conducta = "Suspender insulina EV"
                    mensaje = "Administrar dextrosa al 25% 50 ml y recontrolar a los 30 minutos."
                    proximo_control = "30 minutos"
                    observacion = "Evaluar / avisar médico"
                    hero_text = "Suspender infusión"

                elif suspender:
                    estado = "Detener infusión"
                    clase = "warn"
                    conducta = "Suspender infusión"
                    mensaje = "Glucemia menor a 120 mg/dL. Recontrol frecuente según protocolo."
                    proximo_control = "Según protocolo"
                    observacion = "Vigilar descenso / reevaluar"
                    hero_text = "Detener infusión"

                else:
                    if OBJ_MIN <= g <= OBJ_MAX:
                        estado = "En objetivo"
                        clase = "ok"
                        conducta = "Mantener conducta actual"
                        mensaje = f"Glucemia dentro del rango objetivo ({rango_objetivo})."
                        observacion = "Continuar monitoreo"
                    elif g > OBJ_MAX:
                        estado = "Hiperglucemia"
                        clase = "warn"
                        conducta = "Ajustar infusión según algoritmo"
                        mensaje = "Glucemia por encima del objetivo. Ajustar según la escala correspondiente."
                        observacion = "Evaluar protocolo 2" if modo == "inicio" else "Continuar ajuste"
                    else:
                        estado = "Bajo objetivo"
                        clase = "warn"
                        conducta = "Revisar descenso / considerar suspensión"
                        mensaje = "Glucemia por debajo del objetivo. Vigilar riesgo de hipoglucemia."
                        observacion = "Recontrolar"

                    hero_text = _safe_decimal_text(velocidad_sugerida)

                if glucemia_previa is not None and g > glucemia_previa:
                    tendencia = "Ascenso"
                elif glucemia_previa is not None and g < glucemia_previa:
                    tendencia = "Descenso"
                elif glucemia_previa is not None:
                    tendencia = "Sin cambios"
                else:
                    tendencia = "No informada"

                resultado = {
                    "g": g,
                    "modo": modo,
                    "modo_label": modo_label,
                    "estado": estado,
                    "clase": clase,
                    "conducta": conducta,
                    "mensaje": mensaje,
                    "hero_text": hero_text,
                    "proximo_control": proximo_control,
                    "observacion": observacion,
                    "algoritmo_usado": algoritmo_usado,
                    "velocidad_sugerida": velocidad_sugerida,
                    "bolo_ui": bolo_ui,
                    "tasa_inicial_ui_h": tasa_inicial_ui_h,
                    "alerta_hgr": alerta_hgr,
                    "infusion_activa": infusion_activa,
                    "glucemia_previa": glucemia_previa,
                    "tendencia": tendencia,
                }

                MedicionGlucemia.objects.create(
                    usuario=request.user,
                    glucemia=g,
                    modo=modo,
                    infusion_activa=infusion_activa,
                    glucemia_previa=glucemia_previa,
                    estado=estado,
                    clase=clase,
                    conducta=conducta,
                    mensaje=mensaje,
                    proximo_control=proximo_control,
                    observacion=observacion,
                    tendencia=tendencia,
                    algoritmo_usado=algoritmo_usado,
                    velocidad_sugerida=str(velocidad_sugerida) if velocidad_sugerida is not None else "",
                    bolo_ui=str(bolo_ui) if bolo_ui is not None else "",
                    tasa_inicial_ui_h=str(tasa_inicial_ui_h) if tasa_inicial_ui_h is not None else "",
                    alerta_hgr=alerta_hgr,
                )

            except (ValueError, TypeError, InvalidOperation):
                error_general = "No se pudo calcular el resultado. Revisá los datos ingresados."
            except Exception as e:
                error_general = f"Ocurrió un error inesperado al procesar la medición: {e}"
        else:
            error_general = "Hay datos inválidos en el formulario."

    es_enfermeria = request.user.groups.filter(name="Enfermeria").exists()
    es_medico = request.user.groups.filter(name="Medicos").exists()

    return render(
        request,
        "calculadora/home.html",
        {
            "form": form,
            "resultado": resultado,
            "error_general": error_general,
            "es_enfermeria": es_enfermeria,
            "es_medico": es_medico,
        },
    )