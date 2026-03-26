from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


OBJETIVO_MIN = Decimal("140")
OBJETIVO_MAX = Decimal("200")

UMBRAL_HIPO = Decimal("70")
UMBRAL_INICIO_INSULINA = Decimal("180")
UMBRAL_ALERTA_ALTA = Decimal("200")


def _a_decimal(valor, permitir_none=False):
    """
    Convierte un valor a Decimal de forma segura.
    """
    if valor is None:
        if permitir_none:
            return None
        raise ValueError("El valor no puede ser None.")

    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            if permitir_none:
                return None
            raise ValueError("El valor no puede estar vacío.")

    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Valor numérico inválido: {valor}")


def _a_bool(valor):
    """
    Convierte distintas representaciones comunes a booleano.
    """
    if isinstance(valor, bool):
        return valor

    if valor is None:
        return False

    if isinstance(valor, str):
        valor = valor.strip().lower()
        if valor in ("true", "1", "si", "sí", "s", "yes"):
            return True
        if valor in ("false", "0", "no", "n"):
            return False

    return bool(valor)


def calcular_tendencia(actual, previa):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    if previa is None:
        return None
    if actual > previa:
        return "sube"
    if actual < previa:
        return "baja"
    return "igual"


def calcular_bolo_y_tasa_inicial(glucemia):
    """
    Protocolo:
    Dividir la glucemia inicial por 100 para sugerir bolo inicial y tasa inicial.
    Ej: 400 -> 4.0 UI de bolo y 4.0 UI/h.
    """
    glucemia = _a_decimal(glucemia)
    return (glucemia / Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def calcular_proximo_control(glucemia, horas_desde_inicio=None, estable=False):
    glucemia = _a_decimal(glucemia)
    estable = _a_bool(estable)

    if horas_desde_inicio is not None:
        horas_desde_inicio = _a_decimal(horas_desde_inicio, permitir_none=True)

    if glucemia > Decimal("400"):
        return "Próximo control en 1 hora"

    if Decimal("300") <= glucemia <= Decimal("400"):
        return "Próximo control en 2 horas"

    if Decimal("200") <= glucemia < Decimal("300"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return "Próximo control en 6 horas"
        return "Próximo control en 4 horas"

    if Decimal("140") <= glucemia < Decimal("200"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return "Próximo control en 6 horas"
        return "Próximo control en 4 horas"

    if Decimal("70") <= glucemia < Decimal("140"):
        return "Próximo control según conducta clínica"

    return "Control inmediato / tratar hipoglucemia según protocolo"


def obtener_tasa_algoritmo_inicio(glucemia):
    """
    Algoritmo 2 - Ante inicio / reinicio.
    """
    glucemia = _a_decimal(glucemia)

    if glucemia < Decimal("120"):
        return "Suspender"
    if glucemia <= Decimal("149"):
        return "0,5 UI/h"
    if glucemia <= Decimal("179"):
        return "1 UI/h"
    if glucemia <= Decimal("209"):
        return "1,5 UI/h"
    if glucemia <= Decimal("239"):
        return "2 UI/h"
    if glucemia <= Decimal("269"):
        return "2,5 UI/h"
    if glucemia <= Decimal("299"):
        return "3 UI/h"
    if glucemia <= Decimal("329"):
        return "3,5 UI/h"
    if glucemia <= Decimal("359"):
        return "4 UI/h"
    return "5 UI/h"


def resolver_flujo_glucemia(actual, insulinizado, previa=None, horas_desde_inicio=None, estable=False):
    """
    Resuelve el flujo principal según:
    - glucemia actual
    - si el paciente está insulinizado
    - glucemia previa opcional
    - horas desde inicio opcional
    - estabilidad opcional
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    insulinizado = _a_bool(insulinizado)
    estable = _a_bool(estable)

    resultado = {
        "estado": None,
        "subestado": None,
        "tendencia": calcular_tendencia(actual, previa),
        "bolo_inicial": None,
        "tasa_inicial": None,
        "tasa_algoritmo": None,
        "proximo_control": None,
    }

    # 1) Hipoglucemia siempre tiene prioridad
    if actual < UMBRAL_HIPO:
        resultado["estado"] = "hipoglucemia"
        resultado["subestado"] = "Glucemia menor a 70 mg/dL"
        resultado["proximo_control"] = "Control inmediato / tratar hipoglucemia según protocolo"
        return resultado

    # 2) Paciente insulinizado
    if insulinizado:
        if actual < OBJETIVO_MIN:
            resultado["estado"] = "fuera_de_objetivo"
            resultado["subestado"] = "Por debajo del objetivo en paciente insulinizado"
        elif OBJETIVO_MIN <= actual <= OBJETIVO_MAX:
            resultado["estado"] = "objetivo"
            resultado["subestado"] = "Dentro de objetivo en paciente insulinizado"
        else:
            resultado["estado"] = "hiperglucemia"
            resultado["subestado"] = "Por encima del objetivo en paciente insulinizado"

        resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_inicio(actual)
        resultado["proximo_control"] = calcular_proximo_control(
            actual,
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )
        return resultado

    # 3) Paciente NO insulinizado con criterio de inicio EV
    if (
        previa is not None
        and actual >= UMBRAL_INICIO_INSULINA
        and previa >= UMBRAL_INICIO_INSULINA
    ):
        resultado["estado"] = "inicio_insulina_ev"
        resultado["subestado"] = "Dos controles consecutivos >= 180 mg/dL"
        dosis = calcular_bolo_y_tasa_inicial(actual)
        resultado["bolo_inicial"] = f"{dosis} UI"
        resultado["tasa_inicial"] = f"{dosis} UI/h"
        resultado["proximo_control"] = calcular_proximo_control(
            actual,
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )
        return resultado

    # 4) Paciente NO insulinizado sin criterio de inicio EV
    if OBJETIVO_MIN <= actual < UMBRAL_INICIO_INSULINA:
        resultado["estado"] = "objetivo"
        resultado["subestado"] = "Dentro de objetivo en paciente no insulinizado"
    elif actual >= UMBRAL_INICIO_INSULINA:
        resultado["estado"] = "alerta_hiperglucemia"
        resultado["subestado"] = "Hiperglucemia, pero sin dos controles consecutivos >= 180 mg/dL"
    else:
        resultado["estado"] = "por_debajo_objetivo"
        resultado["subestado"] = "Glucemia por debajo del objetivo"

    resultado["proximo_control"] = calcular_proximo_control(
        actual,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )
    return resultado