from decimal import Decimal


OBJETIVO_MIN = Decimal("140")
OBJETIVO_MAX = Decimal("200")

UMBRAL_HIPO = Decimal("70")              # protocolo: hipoglucemia < 70
UMBRAL_INICIO_INSULINA = Decimal("180")  # no insulinizados: >=180 en 2 controles consecutivos
UMBRAL_ALERTA_ALTA = Decimal("200")


def calcular_tendencia(actual, previa):
    if previa is None:
        return None
    if actual > previa:
        return "sube"
    if actual < previa:
        return "baja"
    return "igual"


def resolver_flujo_glucemia(actual, insulinizado, previa=None):
    actual = Decimal(str(actual))
    previa = Decimal(str(previa)) if previa not in (None, "") else None
    tendencia = calcular_tendencia(actual, previa)

    # 1) Hipoglucemia
    if actual < UMBRAL_HIPO:
        return {
            "titulo_principal": "Urgente",
            "clasificacion": "Hipoglucemia",
            "subclasificacion": (
                "Hipoglucemia en paciente insulinizado"
                if insulinizado == "si"
                else "Hipoglucemia en paciente no insulinizado"
            ),
            "conducta": "Activar manejo de hipoglucemia según protocolo institucional.",
            "proximo_control": "Control inmediato según protocolo.",
            "observacion": (
                f"Tendencia: {tendencia}."
                if tendencia else "No se registró glicemia previa."
            ),
            "clase_css": "hipo",
        }

    # 2) Paciente NO insulinizado:
    # >=180 en 2 controles consecutivos = hiperglucemia sostenida / inicio de insulinización
    if insulinizado == "no":
        if (
            previa is not None
            and actual >= UMBRAL_INICIO_INSULINA
            and previa >= UMBRAL_INICIO_INSULINA
        ):
            if actual >= Decimal("400") or previa >= Decimal("400"):
                sub = "Hiperglucemia sostenida severa"
            elif actual >= Decimal("300") or previa >= Decimal("300"):
                sub = "Hiperglucemia sostenida marcada"
            elif actual > UMBRAL_ALERTA_ALTA or previa > UMBRAL_ALERTA_ALTA:
                sub = "Hiperglucemia sostenida > 200"
            else:
                sub = "≥ 180 mg/dL en 2 controles consecutivos"

            return {
                "titulo_principal": "Atención",
                "clasificacion": "Hiperglucemia sostenida",
                "subclasificacion": sub,
                "conducta": "Corresponde valorar inicio de insulinización según protocolo y condición clínica.",
                "proximo_control": "Repetir control según protocolo institucional.",
                "observacion": f"Actual: {actual} / Previa: {previa}. Tendencia: {tendencia}.",
                "clase_css": "alerta",
            }

    # 3) Paciente insulinizado:
    # 140-200 = objetivo glucémico
    if insulinizado == "si" and OBJETIVO_MIN <= actual <= OBJETIVO_MAX:
        observacion = "Paciente insulinizado dentro del objetivo glucémico (140-200 mg/dL)."
        if tendencia:
            observacion += f" Tendencia: {tendencia}."

        return {
            "titulo_principal": "En rango",
            "clasificacion": "Objetivo glucémico",
            "subclasificacion": "Paciente insulinizado dentro de objetivo",
            "conducta": "Mantener conducta según protocolo y situación clínica.",
            "proximo_control": "Continuar monitoreo según protocolo.",
            "observacion": observacion,
            "clase_css": "objetivo",
        }

    # 4) Si no está insulinizado y el valor actual está en 140-200,
    # no significa 'objetivo terapéutico' igual que el insulinizado.
    # Lo tomamos como valor en rango intermedio, pero sin llamarlo objetivo del protocolo de infusión.
    if insulinizado == "no" and OBJETIVO_MIN <= actual <= OBJETIVO_MAX:
        observacion = "Paciente no insulinizado. Si hay glicemia previa, puede ayudar a evaluar tendencia o persistencia."
        if tendencia:
            observacion = f"Paciente no insulinizado. Tendencia: {tendencia}."

        return {
            "titulo_principal": "Vigilancia",
            "clasificacion": "Valor intermedio",
            "subclasificacion": "Paciente no insulinizado",
            "conducta": "Continuar monitoreo y evaluar evolución según protocolo.",
            "proximo_control": "Repetir control según protocolo.",
            "observacion": observacion,
            "clase_css": "alerta",
        }

    # 5) Por debajo del objetivo, sin hipoglucemia
    if UMBRAL_HIPO <= actual < OBJETIVO_MIN:
        observacion = "Valor por debajo del objetivo, sin criterios de hipoglucemia."
        if tendencia:
            observacion += f" Tendencia: {tendencia}."

        return {
            "titulo_principal": "Vigilancia",
            "clasificacion": "Por debajo del objetivo",
            "subclasificacion": "Sin hipoglucemia",
            "conducta": "Vigilar evolución y reevaluar según protocolo.",
            "proximo_control": "Repetir control según protocolo.",
            "observacion": observacion,
            "clase_css": "alerta",
        }

    # 6) Por encima del objetivo, sin cumplir criterio de sostenida en no insulinizado
    if actual > OBJETIVO_MAX:
        observacion = "Valor por encima del objetivo."
        if tendencia:
            observacion += f" Tendencia: {tendencia}."

        return {
            "titulo_principal": "Atención",
            "clasificacion": "Por encima del objetivo",
            "subclasificacion": (
                "Hiperglucemia aislada" if previa is None else "Hiperglucemia no sostenida"
            ),
            "conducta": "Valorar conducta según protocolo, tendencia y condición clínica.",
            "proximo_control": "Repetir control según protocolo.",
            "observacion": observacion,
            "clase_css": "alerta",
        }

    return {
        "titulo_principal": "Evaluación",
        "clasificacion": "Resultado no categorizado",
        "subclasificacion": None,
        "conducta": "Revisar datos ingresados.",
        "proximo_control": "Según criterio clínico.",
        "observacion": None,
        "clase_css": "alerta",
    }