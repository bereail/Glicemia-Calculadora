from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


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


def _resultado_base(clase=None):
    return {
        "mostrar_resultado": False,
        "clase": clase,
        "estado": None,
        "subestado": None,
        "resumen_objetivo": None,
        "conducta": None,
        "conducta_extra": None,
        "proximo_control": None,
        "comentario_control": None,
        "mensaje": None,
        "observacion": None,
        "texto_rango_objetivo": None,
        "recordatorio_objetivo": None,
        "alerta_rango": "",
        "alerta_borde_hipo": False,
        "requiere_recontrol": False,
        "es_critica": False,
        "tendencia": None,
        "flecha_tendencia": None,
        "delta": None,
        "suspender_insulina": False,
        "administrar_dextrosa": False,
        "evaluar_goteo_mantenimiento": False,
        "reiniciar_insulina": False,
        "bolo_inicial": None,
        "tasa_inicial": None,
        "tasa_algoritmo": None,
        "tasa_calculada": None,
        "bolo_calculado": None,
        "calculo_texto": None,
        "monitoreo_glucemico": None,
        "algoritmo_activo": None,
        "algoritmo_sugerido": None,
        "clasificacion_protocolo": None,
    }


def _resultado_hipo_base():
    resultado = _resultado_base(clase="hipo")
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"
    resultado["es_critica"] = True
    return resultado


def _resultado_hiper_base():
    resultado = _resultado_base(clase="hiper")
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"
    return resultado


def _resultado_rango_base():
    resultado = _resultado_base(clase="rango")
    resultado["resumen_objetivo"] = "Dentro de rango"
    return resultado


def calcular_bolo_y_tasa_inicial(glicemia):
    glicemia = _a_decimal(glicemia)
    return (glicemia / Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def obtener_escalon_algoritmo(glucemia) -> str:
    glucemia = _a_decimal(glucemia)

    if glucemia < Decimal("120"):
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

    if glicemia < Decimal("120"):
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

    if glicemia < Decimal("120"):
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
    if int(algoritmo) == 1:
        return obtener_tasa_algoritmo_1(glicemia)
    if int(algoritmo) == 2:
        return obtener_tasa_algoritmo_2(glicemia)
    raise ValueError("Algoritmo inválido. Debe ser 1 o 2.")


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

    return previa > Decimal("360") and actual > Decimal("360")


def _comentario_monitoreo_insulinizado():
    return (
        "En pacientes hipotensos el monitoreo capilar puede ser inapropiado. "
        "Evaluar muestra venosa."
    )


def _control_4_o_6_horas(horas_desde_inicio=None, estable=False):
    estable = _a_bool(estable)

    if horas_desde_inicio is not None:
        horas_desde_inicio = _a_decimal(horas_desde_inicio, permitir_none=True)

    primeras_24h = horas_desde_inicio is None or horas_desde_inicio <= Decimal("24")

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

    if glicemia > Decimal("400"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Mantener controles horarios hasta alcanzar rango objetivo "
                "140 a 200 mg/dL. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if Decimal("300") <= glicemia <= Decimal("400"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 2 horas",
            "comentario_control": _comentario_monitoreo_insulinizado(),
        }

    if Decimal("200") <= glicemia < Decimal("300"):
        return _control_4_o_6_horas(
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )

    if Decimal("140") <= glicemia < Decimal("200"):
        return _control_4_o_6_horas(
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )

    if Decimal("120") < glicemia < Decimal("140"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 2 horas",
            "comentario_control": (
                "Glucemia por debajo del rango objetivo para paciente insulinizado. "
                "Vigilar descenso y reevaluar ajuste de infusión. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if Decimal("70") < glicemia <= Decimal("120"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Si la infusión está activa, debe permanecer suspendida y "
                "recontrolar cada hora hasta nueva reevaluación. "
                + _comentario_monitoreo_insulinizado()
            ),
        }

    if glicemia == Decimal("70"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
            "comentario_control": (
                "Valor límite de hipoglucemia. Manejar según protocolo y "
                "recontrolar precozmente. "
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

    if glicemia <= Decimal("70"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
            "comentario_control": (
                "Si la glucemia continúa ≤ 70 mg/dL, repetir tratamiento según protocolo."
            ),
        }

    if glicemia <= Decimal("120"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 1 hora",
            "comentario_control": (
                "Si la glucemia es > 70 mg/dL y ≤ 120 mg/dL, mantener la infusión suspendida "
                "y controlar cada hora."
            ),
        }

    if glicemia <= Decimal("180"):
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

    if glicemia < Decimal("70"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 30 minutos",
            "comentario_control": "Hipoglucemia: tratar según protocolo y recontrolar.",
        }

    if glicemia < Decimal("180"):
        return {
            "proximo_control": "Controlar glucemia según monitoreo clínico indicado",
            "comentario_control": (
                "Paciente sin infusión activa y sin criterio actual de insulinización endovenosa."
            ),
        }

    if glicemia < Decimal("300"):
        return {
            "proximo_control": "Repetir glucemia en corto intervalo para confirmar tendencia",
            "comentario_control": (
                "Si presenta dos controles consecutivos ≥ 180 mg/dL, corresponde iniciar "
                "protocolo de insulinización endovenosa."
            ),
        }

    if glicemia <= Decimal("400"):
        return {
            "proximo_control": "Controlar glucemia nuevamente en 2 horas",
            "comentario_control": (
                "Hiperglucemia significativa. Si se confirma persistencia o ya cumple criterio, "
                "iniciar protocolo de insulinización."
            ),
        }

    return {
        "proximo_control": "Controlar glucemia nuevamente en 1 hora",
        "comentario_control": (
            "Hiperglucemia marcada. Reevaluar de forma prioritaria e iniciar protocolo "
            "si corresponde."
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

    dosis = calcular_bolo_y_tasa_inicial(glicemia)
    control_info = calcular_proximo_control(
        glicemia,
        insulinizado=True,
    )

    resultado["estado"] = "Hiperglucemia Sostenida"
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
    resultado["calculo_texto"] = "Dosis inicial estimada según glucemia actual."

    resultado["proximo_control"] = control_info["proximo_control"]
    resultado["comentario_control"] = control_info["comentario_control"]
    resultado["monitoreo_glucemico"] = "Se sugiere monitoreo glucémico frecuente."

    return resultado