def normalizar_clase_desde_estado(estado):
    """
    Traduce el estado clínico a una clase resumida para guardar en BD.
    """
    if not estado:
        return "sin_clasificacion"

    estado = str(estado).lower()

    if "hipogluc" in estado:
        return "hipoglucemia"

    if (
        "post-hipogluc" in estado
        or "post_hipogluc" in estado
        or "rebote post-hipoglucemia" in estado
        or "rebote_post_hipoglucemia" in estado
    ):
        return "post_hipoglucemia"

    if (
        "objetivo" in estado
        or "rango" in estado
        or "debajo de objetivo con infusión" in estado
    ):
        return "en_rango"

    if (
        "hipergluc" in estado
        or "fuera de objetivo" in estado
    ):
        return "hiperglucemia"

    return "sin_clasificacion"


def asignar_clase_visual(resultado):
    """
    Define clase visual:
    - critico
    - alerta
    - rango
    """
    if not resultado:
        return resultado

    estado = str(resultado.get("estado") or "").lower()

    if "hipogluc" in estado:
        resultado["clase_visual"] = "critico"
        return resultado

    if "persistente" in estado or "refractaria" in estado:
        resultado["clase_visual"] = "critico"
        return resultado

    if "hipergluc" in estado:
        resultado["clase_visual"] = "alerta"
        return resultado

    if (
        "objetivo" in estado
        or "rango" in estado
        or "debajo de objetivo con infusión" in estado
    ):
        resultado["clase_visual"] = "rango"
        return resultado

    resultado["clase_visual"] = "rango"
    return resultado


def texto_seguro(valor):
    """
    Convierte None a string vacío.
    """
    return "" if valor is None else str(valor)


def asignar_resumen_objetivo(resultado, infusion_activa):
    """
    Define título superior y texto de rango usado.
    """
    if not resultado:
        return resultado

    clase_visual = resultado.get("clase_visual")

    if clase_visual == "rango":
        resultado["resumen_objetivo"] = "En rango objetivo"
    else:
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"

    if infusion_activa:
        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"
    else:
        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

    return resultado