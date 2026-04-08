from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from .constants import (
    UMBRAL_HIPO,
)


def _a_decimal(valor, permitir_none=False):
    if valor in (None, ""):
        if permitir_none:
            return None
        raise ValueError("Valor requerido")

    try:
        return Decimal(str(valor).strip())
    except (InvalidOperation, TypeError, ValueError):
        if permitir_none:
            return None
        raise ValueError(f"Valor inválido: {valor}")


def _a_bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return False
    return str(valor).strip().lower() in ("true", "1", "si", "sí", "s", "yes")


def _resultado_base():
    return {
        "estado": None,
        "subestado": None,
        "mensaje": None,
        "conducta": None,
        "conducta_extra": None,

        "tendencia": None,
        "flecha_tendencia": None,
        "delta": None,

        "requiere_recontrol": False,
        "proximo_control": None,
        "comentario_control": None,

        "suspender_insulina": False,
        "administrar_dextrosa": False,
        "evaluar_goteo_mantenimiento": False,
        "reiniciar_insulina": False,

        "bolo_inicial": None,
        "tasa_inicial": None,
        "tasa_algoritmo": None,
        "monitoreo_glucemico": None,

        "alerta_borde_hipo": False,
        "recordatorio_objetivo": None,

        "mostrar_resultado": False,
    }


def calcular_bolo_y_tasa_inicial(glucemia):
    glucemia = _a_decimal(glucemia)
    return (glucemia / Decimal("100")).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP
    )


def obtener_tasa_algoritmo_inicio(glucemia):
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


def calcular_proximo_control(glucemia, horas_desde_inicio=None, estable=False):
    glucemia = _a_decimal(glucemia)
    estable = _a_bool(estable)

    if horas_desde_inicio is not None:
        horas_desde_inicio = _a_decimal(horas_desde_inicio, permitir_none=True)

    comentario_fijo = (
        "En pacientes insulinizados el monitoreo capilar puede ser inapropiado. "
        "Evaluar muestra venosa."
    )

    if glucemia >= Decimal("400"):
        return {
            "proximo_control": "Monitoreo capilar una vez por hora",
            "comentario_control": (
                "Hasta alcanzar objetivo >140 <200. " + comentario_fijo
            )
        }

    if Decimal("300") <= glucemia < Decimal("400"):
        return {
            "proximo_control": "Monitoreo capilar cada 2 horas",
            "comentario_control": comentario_fijo
        }

    if Decimal("200") <= glucemia < Decimal("300"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return {
                "proximo_control": "Monitoreo capilar cada 6 horas",
                "comentario_control": (
                    "Las primeras 24 h cada 4 hs; luego cada 6 hs si permanece estable. "
                    + comentario_fijo
                )
            }
        return {
            "proximo_control": "Monitoreo capilar cada 4 horas",
            "comentario_control": (
                "Las primeras 24 h cada 4 hs; luego cada 6 hs si permanece estable. "
                + comentario_fijo
            )
        }

    if Decimal("140") <= glucemia < Decimal("200"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return {
                "proximo_control": "Monitoreo capilar cada 6 horas",
                "comentario_control": (
                    "Las primeras 24 h cada 4 hs; luego cada 6 hs si permanece estable. "
                    + comentario_fijo
                )
            }
        return {
            "proximo_control": "Monitoreo capilar cada 4 horas",
            "comentario_control": (
                "Las primeras 24 h cada 4 hs; luego cada 6 hs si permanece estable. "
                + comentario_fijo
            )
        }

    if Decimal("70") <= glucemia < Decimal("140"):
        return {
            "proximo_control": "Próximo control según conducta clínica",
            "comentario_control": comentario_fijo
        }

    return {
        "proximo_control": "Control inmediato",
        "comentario_control": (
            "Tratar hipoglucemia según protocolo. " + comentario_fijo
        )
    }


def calcular_tendencia(actual, previa):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    if previa is None:
        return None

    delta = actual - previa

    if delta >= Decimal("40"):
        return {
            "direccion": "sube",
            "categoria": "ascenso_marcado",
            "descripcion": "Ascenso marcado",
            "flecha": "↑",
            "delta": str(delta),
        }

    if delta >= Decimal("10"):
        return {
            "direccion": "sube",
            "categoria": "ascenso_leve",
            "descripcion": "Ascenso leve",
            "flecha": "↗",
            "delta": str(delta),
        }

    if delta <= Decimal("-40"):
        return {
            "direccion": "baja",
            "categoria": "descenso_marcado",
            "descripcion": "Descenso marcado",
            "flecha": "↓",
            "delta": str(delta),
        }

    if delta <= Decimal("-10"):
        return {
            "direccion": "baja",
            "categoria": "descenso_leve",
            "descripcion": "Descenso leve",
            "flecha": "↘",
            "delta": str(delta),
        }

    return {
        "direccion": "igual",
        "categoria": "estable",
        "descripcion": "Estable",
        "flecha": "→",
        "delta": str(delta),
    }


def _aplicar_tendencia(resultado, actual, previa):
    tendencia = calcular_tendencia(actual, previa)
    if tendencia is None:
        return resultado

    resultado["tendencia"] = tendencia["descripcion"]
    resultado["flecha_tendencia"] = tendencia["flecha"]
    resultado["delta"] = tendencia["delta"]
    return resultado


def armar_resultado_insulinizacion(glucemia):
    glucemia = _a_decimal(glucemia)

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True

    dosis = calcular_bolo_y_tasa_inicial(glucemia)
    control_info = calcular_proximo_control(glucemia)

    resultado["estado"] = "Hiperglucemia Sostenida"
    resultado["subestado"] = "Dos controles consecutivos >= 180 mg/dL"
    resultado["mensaje"] = "Hiperglucemia sostenida."
    resultado["conducta"] = "Iniciar protocolo de insulinización endovenosa."

    resultado["bolo_inicial"] = f"{dosis} UI"
    resultado["tasa_inicial"] = f"{dosis} UI/h"
    resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_inicio(glucemia)

    resultado["proximo_control"] = control_info["proximo_control"]
    resultado["comentario_control"] = control_info["comentario_control"]
    resultado["monitoreo_glucemico"] = "Se sugiere monitoreo glucémico frecuente."

    return resultado