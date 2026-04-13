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
    """
    Estructura única para todos los resultados clínicos.
    Esto permite que hipo, hiper y rango compartan la misma línea estética
    y el mismo contrato de datos para la UI.
    """
    return {
        # Control general
        "mostrar_resultado": False,
        "clase": clase,  # "hipo", "hiper", "rango"

        # Jerarquía visual principal
        "estado": None,
        "subestado": None,
        "resumen_objetivo": None,      # Ej: "En rango objetivo"
        "conducta": None,              # Bloque principal
        "conducta_extra": None,        # Apoyo opcional
        "proximo_control": None,       # Siempre concreto
        "comentario_control": None,    # Texto de apoyo

        # Contexto clínico
        "mensaje": None,
        "observacion": None,
        "texto_rango_objetivo": None,
        "recordatorio_objetivo": None,

        # Alertas visuales
        "alerta_rango": "",
        "alerta_borde_hipo": False,
        "requiere_recontrol": False,
        "es_critica": False,

        # Tendencia
        "tendencia": None,
        "flecha_tendencia": None,
        "delta": None,

        # Acciones clínicas
        "suspender_insulina": False,
        "administrar_dextrosa": False,
        "evaluar_goteo_mantenimiento": False,
        "reiniciar_insulina": False,

        # Insulinización / dosis
        "bolo_inicial": None,
        "tasa_inicial": None,
        "tasa_algoritmo": None,
        "tasa_calculada": None,
        "bolo_calculado": None,
        "calculo_texto": None,

        # Monitoreo
        "monitoreo_glucemico": None,
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


def obtener_tasa_algoritmo_inicio(glicemia):
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


def calcular_proximo_control(glicemia, horas_desde_inicio=None, estable=False):
    """
    Devuelve textos consistentes para la UI.
    Evita frases vagas como 'según protocolo' o 'según monitoreo habitual'
    cuando se puede expresar algo más concreto.
    """
    glicemia = _a_decimal(glicemia)
    estable = _a_bool(estable)

    if horas_desde_inicio is not None:
        horas_desde_inicio = _a_decimal(horas_desde_inicio, permitir_none=True)

    comentario_fijo = (
        "En pacientes hipotensos el monitoreo capilar puede ser inapropiado"
        "Evaluar muestra venosa."
    )

    if glicemia >= Decimal("400"):
        return {
            "proximo_control": "Controlar glicemia nuevamente en 1 hora",
            "comentario_control": (
                "Hasta alcanzar objetivo >140 y <200 mg/dL. " + comentario_fijo
            ),
        }

    if Decimal("300") <= glicemia < Decimal("400"):
        return {
            "proximo_control": "Controlar glicemia nuevamente en 2 horas",
            "comentario_control": comentario_fijo,
        }

    if Decimal("200") <= glicemia < Decimal("300"):
        if (
            horas_desde_inicio is not None
            and horas_desde_inicio > Decimal("24")
            and estable
        ):
            return {
                "proximo_control": "Controlar glicemia nuevamente en 6 horas",
                "comentario_control": (
                    "Durante las primeras 24 h controlar cada 4 horas; luego cada 6 horas si permanece estable. "
                    + comentario_fijo
                ),
            }
        return {
            "proximo_control": "Controlar glicemia nuevamente en 4 horas",
            "comentario_control": (
                "Durante las primeras 24 h controlar cada 4 horas; luego cada 6 horas si permanece estable. "
                + comentario_fijo
            ),
        }

    if Decimal("140") <= glicemia < Decimal("200"):
        if (
            horas_desde_inicio is not None
            and horas_desde_inicio > Decimal("24")
            and estable
        ):
            return {
                "proximo_control": "Controlar glicemia nuevamente en 6 horas",
                "comentario_control": (
                    "Durante las primeras 24 h controlar cada 4 horas; luego cada 6 horas si permanece estable. "
                    + comentario_fijo
                ),
            }
        return {
            "proximo_control": "Controlar glicemia nuevamente en 4 horas",
            "comentario_control": (
                "Durante las primeras 24 h controlar cada 4 horas; luego cada 6 horas si permanece estable. "
                + comentario_fijo
            ),
        }

    if Decimal("70") <= glicemia < Decimal("140"):
        return {
            "proximo_control": "Controlar glicemia en el próximo horario habitual",
            "comentario_control": comentario_fijo,
        }

    return {
        "proximo_control": "Control inmediato",
        "comentario_control": "Tratar hipoglucemia según protocolo. " + comentario_fijo,
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


def armar_resultado_insulinizacion(glicemia):
    glicemia = _a_decimal(glicemia)

    resultado = _resultado_hiper_base()
    resultado["mostrar_resultado"] = True
    resultado["es_critica"] = True

    dosis = calcular_bolo_y_tasa_inicial(glicemia)
    control_info = calcular_proximo_control(glicemia)

    resultado["estado"] = "Hiperglucemia Sostenida"
    resultado["subestado"] = "Dos controles consecutivos ≥ 180 mg/dL"
    resultado["mensaje"] = "Hiperglucemia sostenida."
    resultado["conducta"] = "Iniciar protocolo de insulinización endovenosa."
    resultado["observacion"] = "Se requieren dos controles consecutivos ≥ 180 mg/dL para iniciar insulinización."
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"

    resultado["bolo_inicial"] = f"{dosis} UI"
    resultado["tasa_inicial"] = f"{dosis} UI/h"
    resultado["bolo_calculado"] = f"{dosis}"
    resultado["tasa_calculada"] = f"{dosis}"
    resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_inicio(glicemia)
    resultado["calculo_texto"] = "Dosis inicial estimada según glucemia actual."

    resultado["proximo_control"] = control_info["proximo_control"]
    resultado["comentario_control"] = control_info["comentario_control"]
    resultado["monitoreo_glucemico"] = "Se sugiere monitoreo glucémico frecuente."

    return resultado