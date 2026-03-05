from decimal import Decimal, ROUND_HALF_UP

TARGET_MIN = 140
TARGET_MAX = 200

def _step_for_glicemia(g: int) -> str:
    """Identifica el escalón por rango (para detectar HGP por 'mismo escalón')."""
    if g < 120: return "<120"
    if 120 <= g <= 149: return "120-149"
    if 150 <= g <= 179: return "150-179"
    if 180 <= g <= 209: return "180-209"
    if 210 <= g <= 239: return "210-239"
    if 240 <= g <= 269: return "240-269"
    if 270 <= g <= 299: return "270-299"
    if 300 <= g <= 329: return "300-329"
    if 330 <= g <= 359: return "330-359"
    return ">360"

def infusion_rate_uh(g: int, algoritmo: str):
    """
    Tabla de U/h del protocolo.
    Algoritmo 1 (inicio/reinicios) y Algoritmo 2 (ante HGR / falla).
    """
    if g < 120:
        return None  # "Suspender"

    if algoritmo == "1":
        # Algoritmo 1: 120–149:0.5, 150–179:1, 180–209:1.5, 210–239:2, 240–269:2.5,
        # 270–299:3, 300–329:3.5, 330–359:4, >360:5
        if 120 <= g <= 149: return Decimal("0.5")
        if 150 <= g <= 179: return Decimal("1")
        if 180 <= g <= 209: return Decimal("1.5")
        if 210 <= g <= 239: return Decimal("2")
        if 240 <= g <= 269: return Decimal("2.5")
        if 270 <= g <= 299: return Decimal("3")
        if 300 <= g <= 329: return Decimal("3.5")
        if 330 <= g <= 359: return Decimal("4")
        return Decimal("5")

    # algoritmo 2
    # 120–149:1, 150–179:1.5, 180–209:2.5, 210–239:3, 240–269:3.5,
    # 270–299:4, 300–329:5, 330–359:6, >360:8
    if 120 <= g <= 149: return Decimal("1")
    if 150 <= g <= 179: return Decimal("1.5")
    if 180 <= g <= 209: return Decimal("2.5")
    if 210 <= g <= 239: return Decimal("3")
    if 240 <= g <= 269: return Decimal("3.5")
    if 270 <= g <= 299: return Decimal("4")
    if 300 <= g <= 329: return Decimal("5")
    if 330 <= g <= 359: return Decimal("6")
    return Decimal("8")

def monitoring_suggestion(g: int) -> str:
    # Frecuencias según protocolo
    if g > 400:
        return "Control cada 1 hora (hasta entrar en objetivo 140–200)."
    if 300 <= g <= 400:
        return "Control cada 2 horas."
    if 200 <= g < 300:
        return "Control cada 4 horas (primeras 24 hs; luego cada 6 hs si estable)."
    return "Control según estabilidad (hasta cada 6 hs si permanece estable)."

def bolo_inicial_y_tasa_inicial(g: int):
    # “Dividir la glucemia inicial por 100” (bolo UI y tasa UI/h)
    d = Decimal(g) / Decimal(100)
    # redondeo a 1 decimal por si viene 185 => 1.9
    d = d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return d, d

def evaluar_glicemia(g: int, algoritmo: str, session: dict) -> dict:
    """
    Usa session para:
    - detectar 2 consecutivos ≥180 (inicio insulinización EV)
    - detectar posible HGP (misma escalón repetida fuera de objetivo)
    """
    # --- consecutivos ≥180 ---
    consec = int(session.get("consec_ge_180", 0))
    if g >= 180:
        consec += 1
    else:
        consec = 0
    session["consec_ge_180"] = consec

    iniciar_insulina = consec >= 2  # 2 determinaciones consecutivas ≥180
    # Protocolo: inicio ante hiperglucemia sostenida (≥180 en 2 controles). :contentReference[oaicite:2]{index=2}

    # --- estados críticos ---
    if g < 70:
        return {
            "estado": "Hipoglicemia",
            "color": "danger",
            "accion": "Suspender infusión y tratar hipoglicemia (dextrosa 25% y control a 30 min).",
            "iniciar_insulina": False,
            "suspender_insulina": True,
            "monitor": "Control a los 30 min y luego según evolución.",
            "uh": None,
            "step": _step_for_glicemia(g),
        }

    if g < 120:
        return {
            "estado": "Suspender infusión",
            "color": "warn",
            "accion": "Detener infusión (punto de detención <120 mg/dL).",
            "iniciar_insulina": False,
            "suspender_insulina": True,
            "monitor": "Control cada 1 hora.",
            "uh": None,
            "step": _step_for_glicemia(g),
        }

    # --- objetivo ---
    if TARGET_MIN <= g <= TARGET_MAX:
        estado = "En rango objetivo (140–200)"
        color = "ok"
    elif g > TARGET_MAX:
        estado = "Fuera de rango (>200)"
        color = "danger"
    else:
        estado = "Por debajo de objetivo (120–139)"
        color = "warn"

    uh = infusion_rate_uh(g, algoritmo)
    monitor = monitoring_suggestion(g)

    # --- posible HGP (simplificado) ---
    # HGP: fuera de objetivo (>200) y sin cambios repetidos en escalón / último escalón, avisar médico y pasar a Algoritmo 2. :contentReference[oaicite:3]{index=3}
    step = _step_for_glicemia(g)
    prev_step = session.get("prev_step")
    same_step_count = int(session.get("same_step_count", 0))

    if step == prev_step and g > 200:
        same_step_count += 1
    else:
        same_step_count = 1

    session["prev_step"] = step
    session["same_step_count"] = same_step_count

    # último escalón depende del algoritmo
    last_step = ">360"  # ambos tienen >360 como último escalón en tabla
    alerta_hgp = False
    if g > 200:
        if step == last_step and same_step_count >= 2:
            alerta_hgp = True
        if step != last_step and same_step_count >= 3:
            alerta_hgp = True

    # signo de alarma HGR (si ya estás en Algoritmo 2 y >360 sostenido)
    alerta_hgr = (algoritmo == "2" and step == ">360" and same_step_count >= 2)

    result = {
        "estado": estado,
        "color": color,
        "accion": "Ajustar infusión según tabla del algoritmo seleccionado.",
        "iniciar_insulina": iniciar_insulina,
        "suspender_insulina": False,
        "monitor": monitor,
        "uh": uh,  # puede ser Decimal o None
        "step": step,
        "alerta_hgp": alerta_hgp,
        "alerta_hgr": alerta_hgr,
    }

    # Bolo/tasa inicial si corresponde iniciar (solo como “sugerencia”)
    if iniciar_insulina:
        bolo, tasa = bolo_inicial_y_tasa_inicial(g)
        result["bolo_ui"] = bolo
        result["tasa_inicial_ui_h"] = tasa

    return result