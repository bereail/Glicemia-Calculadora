def texto_seguro(valor):
    return "" if valor is None else str(valor)


def normalizar_clase_desde_estado(estado):
    if not estado:
        return "sin_clasificacion"

    estado = str(estado).lower()

    if "hipogluc" in estado:
        return "hipoglucemia"

    if (
        "post_hipo" in estado
        or "post_hipogluc" in estado
        or "rebote_post_hipoglucemia" in estado
    ):
        return "post_hipoglucemia"

    if (
        "rango" in estado
        or "objetivo" in estado
        or "estable en rango" in estado
        or "objetivo con infusión" in estado.lower()
        or "en objetivo" in estado.lower()
    ):
        return "en_rango"

    if (
        "hipergluc" in estado
        or "fuera de objetivo" in estado
        or "refractaria" in estado
        or "persistente" in estado
    ):
        return "hiperglucemia"

    return "sin_clasificacion"


def asignar_clase_visual(resultado):
    if not resultado:
        return resultado

    estado = str(resultado.get("estado") or "").strip().lower()

    # Prioridad máxima: flags clínicas
    if resultado.get("es_critico") or resultado.get("nivel_visual") == "critico":
        resultado["clase_visual"] = "alerta"
        return resultado

    # Hipoglucemia
    if "hipogluc" in estado:
        resultado["clase_visual"] = "critico"
        return resultado

    # Hiperglucemia persistente / refractaria / sostenida / marcada
    if (
        "persistente" in estado
        or "refractaria" in estado
        or "hipergluc" in estado
        or "fuera de objetivo" in estado
        or "sostenida" in estado
        or "marcada" in estado
    ):
        resultado["clase_visual"] = "alerta"
        return resultado

    # En rango / objetivo
    if (
        "rango" in estado
        or "objetivo" in estado
        or "en objetivo" in estado
        or "objetivo con infusión" in estado
    ):
        resultado["clase_visual"] = "rango"
        return resultado

    resultado["clase_visual"] = "rango"
    return resultado

def asignar_resumen_objetivo(resultado, infusion_activa):
    if not resultado:
        return resultado

    clase_visual = resultado.get("clase_visual")

    if clase_visual == "rango":
        resultado["resumen_objetivo"] = "Dentro de rango"
    else:
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"

    if infusion_activa:
        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"
    else:
        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

    return resultado


def enriquecer_resultado_ui(resultado, actual, infusion_activa):
    if not resultado:
        return resultado

    resultado = asignar_clase_visual(resultado)
    resultado = asignar_resumen_objetivo(resultado, infusion_activa)

    # limpiar campos visuales
    resultado["tasa_calculada"] = resultado.get("tasa_calculada") or ""
    resultado["bolo_calculado"] = resultado.get("bolo_calculado") or ""
    resultado["calculo_texto"] = resultado.get("calculo_texto") or ""

    if infusion_activa and actual not in (None, ""):
        tasa = round(float(actual) / 100, 2)
        tasa_texto = f"{tasa:.2f}".rstrip("0").rstrip(".")

        if not resultado.get("tasa_calculada"):
            resultado["tasa_calculada"] = tasa_texto
        if not resultado.get("bolo_calculado"):
            resultado["bolo_calculado"] = tasa_texto
        if not resultado.get("bolo_inicial"):
            resultado["bolo_inicial"] = tasa_texto
        if not resultado.get("tasa_inicial"):
            resultado["tasa_inicial"] = tasa_texto

    return resultado