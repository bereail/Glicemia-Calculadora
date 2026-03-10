from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect
from .forms import GlucemiaForm

OBJ_MIN = 140
OBJ_MAX = 200

ALG1 = [
    (None, 119, None),      # <120 Suspender
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
    (None, 119, None),      # <120 Suspender
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


def _in_range(g, lo, hi):
    if lo is None and hi is None:
        return True
    if lo is None:
        return g <= hi
    if hi is None:
        return g >= lo
    return lo <= g <= hi


def _rate_from_table(g, table):
    for lo, hi, rate in table:
        if _in_range(g, lo, hi):
            return rate
    return None


def _round_to_half(x: Decimal) -> Decimal:
    return (x * 2).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 2


def _monitoring_text(g: int) -> str:
    if g > 400:
        return "Cada 1 hora"
    if 300 <= g <= 400:
        return "Cada 2 horas"
    if 200 <= g < 300:
        return "Cada 4 horas (primeras 24 h) y luego cada 6 h si estable"
    return "Cada 6 horas si permanece estable"


def _get_mode_label(modo: str) -> str:
    labels = {
        "inicio": "Inicio / Reinicio",
        "alg1": "Seguimiento - Algoritmo 1",
        "alg2": "Seguimiento - Algoritmo 2",
    }
    return labels.get(modo, "No definido")


def home(request):
    form = GlucemiaForm()
    return render(request, "calculadora/home.html", {"form": form})


def resultado(request):
    if request.method != "POST":
        return redirect("home")

    form = GlucemiaForm(request.POST)
    if not form.is_valid():
        return render(request, "calculadora/home.html", {"form": form})

    g = int(form.cleaned_data["glucemia"])
    modo = form.cleaned_data["modo"]

    rango_objetivo = f"{OBJ_MIN}–{OBJ_MAX} mg/dL"
    modo_label = _get_mode_label(modo)

    # ===== 1) Controles consecutivos >=180 para inicio/reinicio =====
    streak = int(request.session.get("gt180_streak", 0))
    if g >= 180:
        streak += 1
    else:
        streak = 0
    request.session["gt180_streak"] = streak

    iniciar_ev = streak >= 2

    # ===== 2) Estados críticos =====
    es_hipoglucemia = g < 70
    suspender = g < 120

    # ===== 3) Bolo + tasa inicial si corresponde inicio/reinicio =====
    bolo_ui = None
    tasa_inicial_ui_h = None
    if modo == "inicio" and iniciar_ev and not suspender:
        base = _round_to_half(Decimal(g) / Decimal(100))
        bolo_ui = base
        tasa_inicial_ui_h = base

    # ===== 4) Elegir algoritmo según modo =====
    algoritmo_usado = None
    velocidad_sugerida = None

    if modo == "alg1":
        algoritmo_usado = "Algoritmo 1"
        velocidad_sugerida = _rate_from_table(g, ALG1)
    elif modo == "alg2":
        algoritmo_usado = "Algoritmo 2"
        velocidad_sugerida = _rate_from_table(g, ALG2)
    elif modo == "inicio" and iniciar_ev and not suspender:
        algoritmo_usado = "Inicio / Reinicio"
        velocidad_sugerida = tasa_inicial_ui_h

    # ===== 5) Monitoreo =====
    proximo_control = _monitoring_text(g)

    # ===== 6) Alertas =====
    gt360_streak = int(request.session.get("gt360_streak", 0))
    if g > 360:
        gt360_streak += 1
    else:
        gt360_streak = 0
    request.session["gt360_streak"] = gt360_streak

    alerta_hgr = gt360_streak >= 2
    alerta_hgp = False  # se deja pendiente para una versión siguiente

    # ===== 7) Salida clínica =====
    if es_hipoglucemia:
        estado = "Hipoglucemia"
        clase = "danger"
        conducta = "Suspender insulina EV"
        mensaje = "Administrar dextrosa 25% 50 ml y recontrolar a los 30 minutos."
        proximo_control = "30 minutos"
    elif suspender:
        estado = "Detener infusión"
        clase = "warn"
        conducta = "Suspender infusión"
        mensaje = "Glucemia menor a 120 mg/dL. Recontrol frecuente según protocolo."
    elif modo == "inicio" and not iniciar_ev:
        estado = "Aún no iniciar EV"
        clase = "warn"
        conducta = "Esperar segundo control consecutivo"
        mensaje = "La insulinización EV inicia con 2 controles consecutivos de 180 mg/dL o más."
    else:
        if OBJ_MIN <= g <= OBJ_MAX:
            estado = "En objetivo"
            clase = "ok"
            conducta = "Mantener conducta actual"
            mensaje = f"Glucemia dentro del rango objetivo ({rango_objetivo})."
        elif g > OBJ_MAX:
            estado = "Hiperglucemia"
            clase = "warn"
            conducta = "Ajustar infusión según algoritmo"
            mensaje = "Glucemia por encima del objetivo. Ajustar según la escala correspondiente."
        else:
            estado = "Bajo objetivo"
            clase = "warn"
            conducta = "Revisar descenso / considerar suspensión"
            mensaje = "Glucemia por debajo del objetivo. Vigilar riesgo de hipoglucemia."

    ctx = {
        "g": g,
        "modo": modo,
        "modo_label": modo_label,
        "estado": estado,
        "clase": clase,
        "conducta": conducta,
        "mensaje": mensaje,
        "iniciar_ev": iniciar_ev,
        "streak": streak,
        "rango_objetivo": rango_objetivo,
        "bolo_ui": bolo_ui,
        "tasa_inicial_ui_h": tasa_inicial_ui_h,
        "algoritmo_usado": algoritmo_usado,
        "velocidad_sugerida": velocidad_sugerida,
        "proximo_control": proximo_control,
        "alerta_hgp": alerta_hgp,
        "alerta_hgr": alerta_hgr,
    }
    return render(request, "calculadora/resultado.html", ctx)