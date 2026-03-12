from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import GlucemiaForm


OBJ_MIN = 140
OBJ_MAX = 200

ALG1 = [
    (None, 119, None),
    (120, 149, Decimal("0.5")),
    (150, 179, Decimal("1")),
    (180, 209, Decimal("1.5")),
    (210, 239, Decimal("2")),
    (240, 269, Decimal("2.5")),
    (270, 299, Decimal("3")),
    (300, 329, Decimal("3.5")),
    (330, 359, Decimal("4")),
    (360, None, Decimal("5")),
]

ALG2 = [
    (None, 119, None),
    (120, 149, Decimal("1")),
    (150, 179, Decimal("1.5")),
    (180, 209, Decimal("2.5")),
    (210, 239, Decimal("3")),
    (240, 269, Decimal("3.5")),
    (270, 299, Decimal("4")),
    (300, 329, Decimal("5")),
    (330, 359, Decimal("6")),
    (360, None, Decimal("8")),
]


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


@login_required
def home(request):
    form = GlucemiaForm(request.POST or None)
    resultado = None
    error_general = None

    if request.method == "POST":
        if form.is_valid():
            try:
                g = int(form.cleaned_data["glucemia"])
                modo = form.cleaned_data["modo"]
                infusion_activa = form.cleaned_data.get("infusion_activa")
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

                if alerta_hgr:
                    observacion = "URGENTE: Hiperglucemia persistente grave. Evaluar protocolo 2"

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

            except (ValueError, TypeError, InvalidOperation):
                error_general = "No se pudo calcular el resultado. Revisá los datos ingresados."
            except Exception:
                error_general = "Ocurrió un error inesperado al procesar la medición."
        else:
            error_general = "Hay datos inválidos en el formulario."

    return render(
        request,
        "calculadora/home.html",
        {
            "form": form,
            "resultado": resultado,
            "error_general": error_general,
        },
    )