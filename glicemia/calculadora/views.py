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
    (360, None, Decimal("5")),  # >360
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
    (360, None, Decimal("8")),  # >360
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
    # redondeo a 0.5 (ej: 2.49 -> 2.5; 2.25 -> 2.5)
    return (x * 2).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 2


def _monitoring_text(g: int) -> str:
    # Según protocolo (sin tener contexto de "primeras 24h", lo aclaramos)
    if g > 400:
        return "Cada 1 hora (hasta alcanzar objetivo 140–200)"
    if 300 <= g <= 400:
        return "Cada 2 horas"
    if 200 <= g < 300:
        return "Cada 4 horas (primeras 24h) y luego cada 6h si estable"
    return "Cada 6 horas si permanece estable"


def home(request):
    initial = {}
    g = request.GET.get("g")
    momento = request.GET.get("momento")

    if g:
        try:
            initial["glucemia"] = int(g)
        except ValueError:
            pass
    if momento:
        initial["momento"] = momento

    form = GlucemiaForm(initial=initial)
    return render(request, "calculadora/home.html", {"form": form})


def resultado(request):
    if request.method != "POST":
        return redirect("home")

    form = GlucemiaForm(request.POST)
    if not form.is_valid():
        return render(request, "calculadora/home.html", {"form": form})

    g = int(form.cleaned_data["glucemia"])
    momento = form.cleaned_data["momento"]  # opcional

    # ====== 1) Controles consecutivos >=180 (inicio insulinización) ======
    streak = int(request.session.get("gt180_streak", 0))
    if g >= 180:
        streak += 1
    else:
        streak = 0
    request.session["gt180_streak"] = streak

    iniciar_ev = streak >= 2  # protocolo: 2 controles consecutivos >=180
    rango_objetivo = f"{OBJ_MIN}–{OBJ_MAX} mg/dL"

    # ====== 2) Estados críticos ======
    es_hipoglucemia = g < 70
    suspender = g < 120  # protocolo: detener infusión <120

    # ====== 3) Bolo + tasa inicial (g/100) ======
    bolo_ui = None
    tasa_inicial_ui_h = None
    if iniciar_ev and not suspender:
        base = _round_to_half(Decimal(g) / Decimal(100))
        bolo_ui = base
        tasa_inicial_ui_h = base  # UI/h

    # ====== 4) Algoritmos 1 y 2 por tabla ======
    alg1_u_h = _rate_from_table(g, ALG1)
    alg2_u_h = _rate_from_table(g, ALG2)

    # ====== 5) Monitoreo ======
    monitor = _monitoring_text(g)

    # ====== 6) Alertas del protocolo ======
    alerta_hgr = False
    # HGR: >360 mg/dL en 2 mediciones consecutivas estando en último escalón Alg2
    # Como MVP sin “estado Alg2”, detectamos lo básico: 2 consecutivas >360
    gt360_streak = int(request.session.get("gt360_streak", 0))
    if g > 360:
        gt360_streak += 1
    else:
        gt360_streak = 0
    request.session["gt360_streak"] = gt360_streak
    if gt360_streak >= 2:
        alerta_hgr = True

    # HGP (fallo algoritmo 1) requiere comparar escalón y cambios en varias mediciones.
    # MVP: lo dejamos como “condición a evaluar” y lo implementamos bien en el siguiente paso.
    alerta_hgp = False

    # ====== 7) Mensaje principal ======
    if es_hipoglucemia:
        estado, clase = "Hipoglucemia", "danger"
        mensaje = "Suspender insulina. Administrar dextrosa 25% 50 ml y recontrol a los 30 min (según protocolo)."
    elif suspender:
        estado, clase = "Detener infusión", "warn"
        mensaje = "Glucemia <120 mg/dL: suspender infusión y recontrol frecuente."
    elif not iniciar_ev:
        estado, clase = "Aún no iniciar EV", "warn"
        mensaje = "Se inicia insulinización EV ante ≥180 mg/dL en 2 controles consecutivos."
    else:
        # ya “iniciar EV”
        if OBJ_MIN <= g <= OBJ_MAX:
            estado, clase = "En objetivo", "ok"
            mensaje = f"Rango objetivo {rango_objetivo}."
        elif g > OBJ_MAX:
            estado, clase = "Fuera de objetivo", "warn"
            mensaje = f"Glucemia >{OBJ_MAX}: ajustar según Algoritmo 1 (y Algoritmo 2 si HGP)."
        else:
            estado, clase = "Bajo objetivo", "warn"
            mensaje = f"Glucemia <{OBJ_MIN}: riesgo de hipoglucemia. Ajustar/suspender según protocolo."

    ctx = {
        "g": g,
        "momento": momento,
        "estado": estado,
        "clase": clase,
        "mensaje": mensaje,
        "iniciar_ev": iniciar_ev,
        "streak": streak,
        "rango_objetivo": rango_objetivo,
        "bolo_ui": bolo_ui,
        "tasa_inicial_ui_h": tasa_inicial_ui_h,
        "alg1_u_h": alg1_u_h,
        "alg2_u_h": alg2_u_h,
        "monitor": monitor,
        "alerta_hgp": alerta_hgp,
        "alerta_hgr": alerta_hgr,
    }
    return render(request, "calculadora/resultado.html", ctx)