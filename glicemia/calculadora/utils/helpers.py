from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .constants import (
    LIMITE_SUSPENDER_INFUSION,
    OBJETIVO_MAX_INFUSION,
    OBJETIVO_MIN_INFUSION,
    UMBRAL_CONTROL_1H,
    UMBRAL_CONTROL_2H,
    UMBRAL_FUERA_OBJETIVO_ALTO,
    UMBRAL_HIPER,
    UMBRAL_HIPO,
    UMBRAL_REFRACTARIA,
)


def _a_decimal(valor, permitir_none=False):
    if valor in (None, ""):
        if permitir_none:
            return None
        raise ValueError("Valor requerido")

    try:
        return Decimal(str(valor).strip())
    except (InvalidOperation, TypeError, ValueError) as exc:
        if permitir_none:
            return None
        raise ValueError(f"Valor inválido: {valor}") from exc


def _a_bool(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return False
    return str(valor).strip().lower() in ("true", "1", "si", "sí", "s", "yes")


def _resultado_base(clase="sin_clasificacion"):
    return {
        "mostrar_resultado": True,
        "clase": clase,
        "estado": "",
        "subestado": "",
        "resumen_objetivo": "",
        "conducta": "",
        "conducta_extra": "",
        "proximo_control": "",
        "comentario_control": "",
        "mensaje": "",
        "observacion": "",
        "texto_rango_objetivo": "",
        "recordatorio_objetivo": "",
        "alerta_rango": "",
        "alerta_borde_hipo": False,
        "requiere_recontrol": False,
        "es_critica": False,
        "es_critico": False,
        "nivel_visual": "",
        "tendencia": "",
        "flecha_tendencia": "",
        "delta": "",
        "suspender_insulina": False,
        "administrar_dextrosa": False,
        "evaluar_goteo_mantenimiento": False,
        "reiniciar_insulina": False,
        "bolo_inicial": "",
        "tasa_inicial": "",
        "tasa_algoritmo": "",
        "tasa_calculada": "",
        "bolo_calculado": "",
        "calculo_texto": "",
        "monitoreo_glucemico": "",
        "algoritmo_activo": "",
        "algoritmo_sugerido": "",
        "algoritmo_usado": "",
        "clasificacion_protocolo": "",
        "velocidad_sugerida": "",
        "escalon_algoritmo": "",
        "escalamiento_clinico": "normal",
        "ui_variant": "",
        "en_objetivo": False,
        "en_objetivo_con_alerta": False,
        "fuera_objetivo": False,
        "mostrar_tasa": False,
        "tasa": "",
    }


def _resultado_hipo_base():
    resultado = _resultado_base(clase="hipoglucemia")
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"
    resultado["es_critica"] = True
    resultado["es_critico"] = True
    resultado["nivel_visual"] = "critico"
    return resultado


def _resultado_hiper_base():
    resultado = _resultado_base(clase="hiperglucemia")
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"
    resultado["nivel_visual"] = "alerta"
    return resultado


def _resultado_rango_base():
    resultado = _resultado_base(clase="en_rango")
    resultado["resumen_objetivo"] = "Dentro de rango"
    resultado["nivel_visual"] = "rango"
    return resultado


def calcular_bolo_y_tasa_inicial(glicemia):
    glicemia = _a_decimal(glicemia)
    dosis = (glicemia / Decimal("100")).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP,
    )
    return dosis


def obtener_escalon_algoritmo(glucemia):
    glucemia = _a_decimal(glucemia)

    if glucemia < LIMITE_SUSPENDER_INFUSION:
        return "<120"
    if glucemia <= Decimal("149"):
        return "120-149"
    if glucemia <= Decimal("179"):
        return "150-179"
    if glucemia <= Decimal("209"):
        return "180-209"
    if glucemia <= Decimal("239"):
        return "210-239"
    if glucemia <= Decimal("269"):
        return "240-269"
    if glucemia <= Decimal("299"):
        return "270-299"
    if glucemia <= Decimal("329"):
        return "300-329"
    if glucemia <= Decimal("359"):
        return "330-359"
    return ">360"


def obtener_tasa_algoritmo_1(glicemia):
    glicemia = _a_decimal(glicemia)

    if glicemia < LIMITE_SUSPENDER_INFUSION:
        return "Suspender"
    if glicemia <= Decimal("149"):
        return "0,5 UI/h"
    if glicemia <= Decimal("179"):
        return "1 UI/h"
    if glicemia <= Decimal("209"):
        return "1,5 UI/h"
    if glicemia <= Decimal("239"):
        return "2 UI/h"
    if glicemia <= Decimal("269"):
        return "2,5 UI/h"
    if glicemia <= Decimal("299"):
        return "3 UI/h"
    if glicemia <= Decimal("329"):
        return "3,5 UI/h"
    if glicemia <= Decimal("359"):
        return "4 UI/h"
    return "5 UI/h"


def obtener_tasa_algoritmo_2(glicemia):
    glicemia = _a_decimal(glicemia)

    if glicemia < LIMITE_SUSPENDER_INFUSION:
        return "Suspender"
    if glicemia <= Decimal("149"):
        return "1 UI/h"
    if glicemia <= Decimal("179"):
        return "1,5 UI/h"
    if glicemia <= Decimal("209"):
        return "2,5 UI/h"
    if glicemia <= Decimal("239"):
        return "3 UI/h"
    if glicemia <= Decimal("269"):
        return "3,5 UI/h"
    if glicemia <= Decimal("299"):
        return "4 UI/h"
    if glicemia <= Decimal("329"):
        return "5 UI/h"
    if glicemia <= Decimal("359"):
        return "6 UI/h"
    return "8 UI/h"


def obtener_tasa_por_algoritmo(glicemia, algoritmo=1):
    algoritmo = int(algoritmo or 1)
    if algoritmo == 1:
        return obtener_tasa_algoritmo_1(glicemia)
    if algoritmo == 2:
        return obtener_tasa_algoritmo_2(glicemia)
    raise ValueError("Algoritmo inválido. Debe ser 1 o 2.")


def mismo_escalon(v1, v2):
    if v1 is None or v2 is None:
        return False
    return obtener_escalon_algoritmo(v1) == obtener_escalon_algoritmo(v2)


def tres_mediciones_mismo_escalon(anterior, previa, actual):
    if anterior is None or previa is None or actual is None:
        return False
    e1 = obtener_escalon_algoritmo(anterior)
    e2 = obtener_escalon_algoritmo(previa)
    e3 = obtener_escalon_algoritmo(actual)
    return e1 == e2 == e3


def dos_ultimas_mayores_360(previa, actual):
    previa = _a_decimal(previa, permitir_none=True)
    actual = _a_decimal(actual, permitir_none=True)

    if previa is None or actual is None:
        return False

    return previa > UMBRAL_REFRACTARIA and actual > UMBRAL_REFRACTARIA


def _comentario_monitoreo_insulinizado():
    return (
        "En pacientes hipotensos el monitoreo capilar puede ser inapropiado. "
        "Evaluar muestra venosa."
    )


def _control_4_o_6_horas(horas_desde_inicio=None, estable=False):
    estable = _a_bool(estable)
    horas = _a_decimal(horas_desde_inicio, permitir_none=True)

    primeras_24h = horas is None or horas < Decimal("24")

    if primeras_24h or not estable:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 4 horas",
            "comentario_control": (
                "Durante las primeras 24 horas controlar cada 4 horas; "
                "luego cada 6 horas si permanece estable. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    return {
        "proximo_control": "Controlar glucemia nuevamente en 6 horas",
        "comentario_control": (
            "Paciente estable y con más de 24 horas de seguimiento. "
            + _comentario_monitoreo_insulinizado()
        ),
    }


def calcular_proximo_control_insulinizado(
    glicemia,
    horas_desde_inicio=None,
    estable=False,
):
    glicemia = _a_decimal(glicemia)

    if glicemia > UMBRAL_CONTROL_1H:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Mantener controles horarios hasta alcanzar rango objetivo "
                "140 a 200 mg/dL. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if UMBRAL_CONTROL_2H <= glicemia <= UMBRAL_CONTROL_1H:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 2 horas",
            "comentario_control": _comentario_monitoreo_insulinizado(),
        }

    if UMBRAL_FUERA_OBJETIVO_ALTO < glicemia < UMBRAL_CONTROL_2H:
        return _control_4_o_6_horas(
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )

    if OBJETIVO_MIN_INFUSION <= glicemia <= OBJETIVO_MAX_INFUSION:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 6 horas",
            "comentario_control": (
                "Paciente en rango objetivo. Continuar monitoreo cada 6 horas. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if LIMITE_SUSPENDER_INFUSION <= glicemia < OBJETIVO_MIN_INFUSION:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Glucemia por debajo del rango objetivo para paciente insulinizado. "
                "Suspender infusión y reevaluar. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if UMBRAL_HIPO < glicemia < LIMITE_SUSPENDER_INFUSION:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Si la infusión está activa, debe permanecer suspendida y "
                "recontrolar cada hora hasta nueva reevaluación. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    return {
        "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
        "comentario_control": (
            "Hipoglucemia: suspender infusión de insulina, tratar según protocolo "
            "y recontrolar a los 30 minutos. "
            + _comentario_monitoreo_insulinizado()
        ),
    }


def calcular_proximo_control_post_hipoglucemia(glicemia):
    glicemia = _a_decimal(glicemia)

    if glicemia <= UMBRAL_HIPO:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
            "comentario_control": (
                "Si la glucemia continúa ≤ 70 mg/dL, repetir tratamiento según protocolo."
            ),
        }

    if glicemia <= LIMITE_SUSPENDER_INFUSION:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Si la glucemia es > 70 mg/dL y ≤ 120 mg/dL, mantener la infusión suspendida "
                "y controlar cada hora."
            ),
        }

    if glicemia <= UMBRAL_HIPER:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Continuar vigilancia estrecha hasta definir reinicio o no de la infusión."
            ),
        }

    return {
        "proximo_control": "Controlar glucemia nuevamente según algoritmo de insulinización",
        "comentario_control": (
            "La infusión puede reinstaurarse cuando la glucemia sea > 180 mg/dL, "
            "siempre en Algoritmo 1."
        ),
    }


def calcular_proximo_control_no_insulinizado(glicemia):
    glicemia = _a_decimal(glicemia)

    if glicemia < UMBRAL_HIPO:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
            "comentario_control": "Hipoglucemia: tratar según protocolo y recontrolar.",
        }

    if glicemia <= UMBRAL_HIPER:
        return {
            "proximo_control": "Controlar glucemia nuevamente en 6 horas",
            "comentario_control": (
                "Paciente sin infusión activa y sin criterio actual de insulinización endovenosa."
            ),
        }

    return {
        "proximo_control": "Repetir glucemia en corto intervalo para confirmar tendencia",
        "comentario_control": (
            "Si presenta dos controles consecutivos ≥ 180 mg/dL, corresponde iniciar "
            "protocolo de insulinización endovenosa."
        ),
    }


def calcular_proximo_control(
    glicemia,
    insulinizado=False,
    horas_desde_inicio=None,
    estable=False,
    post_hipoglucemia=False,
):
    if post_hipoglucemia:
        return calcular_proximo_control_post_hipoglucemia(glicemia)

    if _a_bool(insulinizado):
        return calcular_proximo_control_insulinizado(
            glicemia,
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )

    return calcular_proximo_control_no_insulinizado(glicemia)


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


def armar_resultado_insulinizacion(glicemia):
    glicemia = _a_decimal(glicemia)

    resultado = _resultado_hiper_base()
    resultado["mostrar_resultado"] = True
    resultado["es_critica"] = True
    resultado["es_critico"] = True

    dosis = calcular_bolo_y_tasa_inicial(glicemia)
    control_info = calcular_proximo_control(
        glicemia,
        insulinizado=True,
    )

    resultado["estado"] = "Hiperglucemia sostenida"
    resultado["subestado"] = "Dos controles consecutivos ≥ 180 mg/dL"
    resultado["mensaje"] = "Hiperglucemia sostenida."
    resultado["conducta"] = "Iniciar protocolo de insulinización endovenosa."
    resultado["observacion"] = (
        "Se requieren dos controles consecutivos ≥ 180 mg/dL para iniciar insulinización."
    )
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"

    resultado["bolo_inicial"] = f"{dosis} UI"
    resultado["tasa_inicial"] = f"{dosis} UI/h"
    resultado["bolo_calculado"] = f"{dosis}"
    resultado["tasa_calculada"] = f"{dosis}"
    resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_1(glicemia)
    resultado["algoritmo_sugerido"] = "Algoritmo 1"
    resultado["calculo_texto"] = "Dosis inicial estimada según glucemia actual."

    resultado["proximo_control"] = control_info["proximo_control"]
    resultado["comentario_control"] = control_info["comentario_control"]
    resultado["monitoreo_glucemico"] = "Se sugiere monitoreo glucémico frecuente."

    return resultado