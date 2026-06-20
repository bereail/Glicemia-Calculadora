from datetime import timedelta
from django.db.models import Count
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from .forms import GlucemiaForm
from .models import MedicionGlucemia
from .services import evaluar_glucemia_service
from .utils.helpers import _a_bool
from .utils.ui.presentation import (
    enriquecer_resultado_ui,
    normalizar_clase_desde_estado,
    texto_seguro,
)


# =========================================================
# PERMISOS
# =========================================================

def _calcular_contexto_infusion(user):
    primera = (
        MedicionGlucemia.objects
        .filter(usuario=user, infusion_activa=True)
        .order_by("fecha_hora")
        .first()
    )
    horas_desde_inicio = None
    if primera:
        delta = timezone.now() - primera.fecha_hora
        horas_desde_inicio = delta.total_seconds() / 3600

    ultimas = list(
        MedicionGlucemia.objects
        .filter(usuario=user, infusion_activa=True)
        .order_by("-fecha_hora")[:2]
    )
    estable = len(ultimas) >= 2 and all(m.clase == "en_rango" for m in ultimas)

    return horas_desde_inicio, estable


def tiene_acceso_home(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name="Enfermeria").exists()
        or user.groups.filter(name="Medicos").exists()
    )


def tiene_acceso_historial(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.username == "metanutric"
    )


# =========================================================
# GUARDADO
# =========================================================

def _guardar_medicion(request, cleaned_data, resultado):
    if not request.user.is_authenticated:
        return None

    estado = resultado.get("estado")
    clase = normalizar_clase_desde_estado(estado)

    medicion = MedicionGlucemia.objects.create(
        usuario=request.user,
        glicemia_actual=int(cleaned_data["glicemia_actual"]),
        glicemia_previa=(
            int(cleaned_data["glicemia_previa"])
            if cleaned_data.get("glicemia_previa") is not None
            else None
        ),
        infusion_activa=_a_bool(cleaned_data.get("infusion_activa")),
        tercera_medicion=(
            int(cleaned_data["tercera_medicion"])
            if cleaned_data.get("tercera_medicion") is not None
            else None
        ),
        modo=cleaned_data.get("modo") or "seguimiento",
        estado=texto_seguro(resultado.get("estado")),
        subestado=texto_seguro(resultado.get("subestado")),
        clase=clase,
        mensaje=texto_seguro(resultado.get("mensaje")),
        conducta=texto_seguro(resultado.get("conducta")),
        proximo_control=texto_seguro(resultado.get("proximo_control")),
        observacion=texto_seguro(
            resultado.get("observacion")
            or resultado.get("conducta_extra")
        ),
        tendencia=texto_seguro(resultado.get("tendencia")),
        flecha_tendencia=texto_seguro(resultado.get("flecha_tendencia")),
        delta=texto_seguro(resultado.get("delta")),
        algoritmo_usado=texto_seguro(
            resultado.get("algoritmo_usado") or resultado.get("algoritmo_sugerido")
        ),
        velocidad_sugerida=texto_seguro(resultado.get("velocidad_sugerida")),
        bolo_ui=texto_seguro(resultado.get("bolo_inicial")),
        tasa_inicial_ui_h=texto_seguro(resultado.get("tasa_inicial")),
        tasa_algoritmo=texto_seguro(resultado.get("tasa_algoritmo")),
        requiere_recontrol=bool(resultado.get("requiere_recontrol")),
        suspender_insulina=bool(resultado.get("suspender_insulina")),
        administrar_dextrosa=bool(resultado.get("administrar_dextrosa")),
        reiniciar_insulina=bool(resultado.get("reiniciar_insulina")),
        alerta_hgr=(
            clase == "hiperglucemia"
            and "refractaria" in texto_seguro(estado).lower()
        ),
    )

    return medicion


# =========================================================
# VIEW PRINCIPAL
def _json_safe(obj):
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


# =========================================================

@login_required
@user_passes_test(tiene_acceso_home, login_url="/login/")
def control_glicemia(request):
    if request.method == "POST":
        form = GlucemiaForm(request.POST)

        if form.is_valid():
            actual = form.cleaned_data["glicemia_actual"]
            previa = form.cleaned_data.get("glicemia_previa")
            infusion_activa = form.cleaned_data.get("infusion_activa")
            tercera_medicion = form.cleaned_data.get("tercera_medicion")
            algoritmo_activo = form.cleaned_data.get("algoritmo_activo", "1")

            horas_desde_inicio, estable = _calcular_contexto_infusion(request.user)

            resultado = evaluar_glucemia_service(
                actual=actual,
                previa=previa,
                infusion_activa=infusion_activa,
                tercera_medicion=tercera_medicion,
                algoritmo_activo=algoritmo_activo,
                horas_desde_inicio=horas_desde_inicio,
                estable=estable,
            )

            resultado = enriquecer_resultado_ui(
                resultado=resultado,
                actual=actual,
                infusion_activa=_a_bool(infusion_activa),
            )

            resultado["infusion_activa"] = _a_bool(infusion_activa)

            estado_lower = str(resultado.get("estado") or "").lower()

            if "persistente" in estado_lower or "refractaria" in estado_lower:
                resultado["es_critico"] = True
                resultado["nivel_visual"] = "critico"
                resultado["clase_visual"] = "alerta"
            elif "hipergluc" in estado_lower:
                resultado["clase_visual"] = "alerta"

            _guardar_medicion(request, form.cleaned_data, resultado)

            request.session["glicemia_resultado"] = _json_safe(resultado)
            request.session["glicemia_post_data"] = request.POST.dict()
            return redirect("control_glicemia")

        return render(
            request,
            "calculadora/control_glicemia.html",
            {
                "form": form,
                "resultado": None,
                "medicion_guardada": None,
                "es_medico": request.user.groups.filter(name="Medicos").exists(),
            },
        )

    resultado = request.session.pop("glicemia_resultado", None)
    post_data = request.session.pop("glicemia_post_data", None)

    if post_data:
        form = GlucemiaForm(post_data)
        form.is_valid()
    else:
        form = GlucemiaForm()

    return render(
        request,
        "calculadora/control_glicemia.html",
        {
            "form": form,
            "resultado": resultado,
            "medicion_guardada": None,
            "es_medico": request.user.groups.filter(name="Medicos").exists(),
        },
    )



_TURNOS = {
    "manana":    (6, 12),
    "tarde":     (12, 18),
    "noche":     (18, 24),
    "madrugada": (0, 6),
}


def _filtrar_mediciones_desde_request(request):
    usuario = request.GET.get("usuario", "").strip()
    estado = request.GET.get("estado", "").strip()
    clase = request.GET.get("clase", "").strip()
    periodo = request.GET.get("periodo", "").strip().lower()
    turno = request.GET.get("turno", "").strip().lower()

    mediciones = (
        MedicionGlucemia.objects.select_related("usuario")
        .all()
        .order_by("-fecha_hora")
    )

    if usuario:
        mediciones = mediciones.filter(usuario__username=usuario)

    if estado:
        mediciones = mediciones.filter(estado=estado)

    if clase:
        mediciones = mediciones.filter(clase=clase)

    ahora = timezone.now()

    if periodo == "semanal":
        desde = ahora - timedelta(days=7)
        mediciones = mediciones.filter(fecha_hora__gte=desde)
    elif periodo == "mensual":
        desde = ahora - timedelta(days=30)
        mediciones = mediciones.filter(fecha_hora__gte=desde)

    if turno and turno in _TURNOS:
        h_ini, h_fin = _TURNOS[turno]
        ids = [
            pk for pk, fecha in mediciones.values_list("pk", "fecha_hora")
            if h_ini <= timezone.localtime(fecha).hour < h_fin
        ]
        mediciones = mediciones.filter(pk__in=ids)

    return mediciones, usuario, estado, clase, periodo, turno


@login_required
@user_passes_test(tiene_acceso_historial, login_url="/login/")
def historial(request):
    (
        mediciones_qs,
        usuario_seleccionado,
        estado_seleccionado,
        clase_seleccionada,
        periodo,
        turno_seleccionado,
    ) = _filtrar_mediciones_desde_request(request)

    total = mediciones_qs.count()
    hipoglucemias = mediciones_qs.filter(clase="hipoglucemia").count()
    post_hipoglucemias = mediciones_qs.filter(clase="post_hipoglucemia").count()
    en_objetivo = mediciones_qs.filter(clase="en_rango").count()
    hiperglucemias = mediciones_qs.filter(clase="hiperglucemia").count()

    uso_medicos = MedicionGlucemia.objects.filter(usuario__groups__name="Medicos").count()
    uso_enfermeria = MedicionGlucemia.objects.filter(usuario__groups__name="Enfermeria").count()
    uso_sin_grupo = MedicionGlucemia.objects.filter(usuario__groups__isnull=True).count()

    turnos = {"manana": 0, "tarde": 0, "noche": 0, "madrugada": 0}
    for fecha in MedicionGlucemia.objects.values_list("fecha_hora", flat=True):
        h = timezone.localtime(fecha).hour
        if 6 <= h < 12:
            turnos["manana"] += 1
        elif 12 <= h < 18:
            turnos["tarde"] += 1
        elif 18 <= h < 24:
            turnos["noche"] += 1
        else:
            turnos["madrugada"] += 1

    paginator = Paginator(mediciones_qs, 5)
    page_number = request.GET.get("page")
    mediciones = paginator.get_page(page_number)

    usuarios = (
        MedicionGlucemia.objects.values_list("usuario__username", flat=True)
        .distinct()
        .order_by("usuario__username")
    )

    estados = (
        MedicionGlucemia.objects.values_list("estado", flat=True)
        .distinct()
        .exclude(estado="Hiperglucemia Severa")
        .order_by("estado")
    )

    clases = (
        MedicionGlucemia.objects.values_list("clase", flat=True)
        .distinct()
        .order_by("clase")
    )

    return render(
        request,
        "calculadora/historial.html",
        {
            "mediciones": mediciones,
            "usuarios": usuarios,
            "estados": estados,
            "clases": clases,
            "usuario_seleccionado": usuario_seleccionado,
            "estado_seleccionado": estado_seleccionado,
            "clase_seleccionada": clase_seleccionada,
            "periodo_seleccionado": periodo,
            "turno_seleccionado": turno_seleccionado,
            "total": total,
            "hipoglucemias": hipoglucemias,
            "post_hipoglucemias": post_hipoglucemias,
            "en_objetivo": en_objetivo,
            "hiperglucemias": hiperglucemias,
            "uso_medicos": uso_medicos,
            "uso_enfermeria": uso_enfermeria,
            "uso_sin_grupo": uso_sin_grupo,
            "turno_manana": turnos["manana"],
            "turno_tarde": turnos["tarde"],
            "turno_noche": turnos["noche"],
            "turno_madrugada": turnos["madrugada"],
        },
    )


@login_required
@user_passes_test(tiene_acceso_historial, login_url="/login/")
def exportar_historial_excel(request):
    mediciones, usuario, estado, clase, periodo, turno = _filtrar_mediciones_desde_request(
        request
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Historial"

    titulo = f"Reporte de mediciones - {periodo or 'completo'}"
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=14)

    ws["A2"] = f"Usuario: {usuario or 'Todos'}"
    ws["B2"] = f"Estado: {estado or 'Todos'}"
    ws["C2"] = f"Clase: {clase or 'Todas'}"
    ws["D2"] = f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}"

    headers = [
        "Fecha",
        "Usuario",
        "Glucemia actual",
        "Glucemia previa",
        "Infusión activa",
        "Modo",
        "Estado",
        "Subestado",
        "Clase",
        "Conducta",
        "Próximo control",
        "Tendencia",
        "Flecha",
    ]

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    fila_header = 4
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=fila_header, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    fill_par = PatternFill("solid", fgColor="EBF3FB")
    fill_impar = PatternFill("solid", fgColor="FFFFFF")
    wrap = Alignment(wrap_text=True, vertical="top")
    center_top = Alignment(horizontal="center", vertical="top")

    fila = 5
    for m in mediciones:
        fill = fill_par if fila % 2 == 0 else fill_impar
        valores = [
            timezone.localtime(m.fecha_hora).strftime("%d/%m/%Y %H:%M"),
            m.usuario.username if m.usuario else "",
            f"{m.glicemia_actual} mg/dL",
            f"{m.glicemia_previa} mg/dL" if m.glicemia_previa is not None else "",
            "Sí" if m.infusion_activa else "No",
            m.get_modo_display(),
            m.estado,
            m.subestado,
            m.clase,
            m.conducta,
            m.proximo_control,
            m.tendencia or "",
            m.flecha_tendencia or "",
        ]
        for col, valor in enumerate(valores, start=1):
            cell = ws.cell(row=fila, column=col, value=valor)
            cell.fill = fill
            cell.alignment = wrap if col == 10 else center_top
        ws.row_dimensions[fila].height = 28
        fila += 1

    widths = {
        "A": 18, "B": 18, "C": 16, "D": 16, "E": 14,
        "F": 18, "G": 26, "H": 30, "I": 18, "J": 42,
        "K": 26, "L": 18, "M": 10,
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
@user_passes_test(tiene_acceso_historial, login_url="/login/")
def exportar_historial_pdf(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    mediciones, usuario, estado, clase, periodo, turno = _filtrar_mediciones_desde_request(
        request
    )

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

    elements.append(
        Paragraph(f"Reporte de mediciones - {periodo or 'completo'}", styles["Title"])
    )
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Usuario: {usuario or 'Todos'}", styles["Normal"]))
    elements.append(Paragraph(f"Estado: {estado or 'Todos'}", styles["Normal"]))
    elements.append(Paragraph(f"Clase: {clase or 'Todas'}", styles["Normal"]))
    elements.append(
        Paragraph(
            f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 12))

    estilo_conducta = styles["Normal"].clone("conducta")
    estilo_conducta.fontSize = 7.5
    estilo_conducta.leading = 10

    data = [[
        "Fecha", "Usuario", "Actual", "Previa", "Infusión",
        "Estado", "Clase", "Conducta", "Tendencia"
    ]]

    for m in mediciones:
        data.append(
            [
                timezone.localtime(m.fecha_hora).strftime("%d/%m/%Y\n%H:%M"),
                m.usuario.username if m.usuario else "",
                f"{m.glicemia_actual}",
                f"{m.glicemia_previa}" if m.glicemia_previa is not None else "",
                "Sí" if m.infusion_activa else "No",
                m.estado,
                m.clase,
                Paragraph(m.conducta or "", estilo_conducta),
                f"{m.tendencia or ''} {m.flecha_tendencia or ''}".strip(),
            ]
        )

    col_widths = [28*mm, 24*mm, 16*mm, 16*mm, 16*mm, 36*mm, 22*mm, 62*mm, 20*mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C7D3E0")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#0F2E52")),
    ]
    for i, _ in enumerate(data[1:], start=1):
        bg = colors.HexColor("#EBF3FB") if i % 2 == 0 else colors.white
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_cmds))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    nombre = f"historial_{periodo or 'completo'}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return response