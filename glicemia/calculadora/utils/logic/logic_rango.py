from decimal import Decimal

from ..constants import (
    LIMITE_SUSPENDER_INFUSION,
    OBJETIVO_MAX_INFUSION,
    OBJETIVO_MIN_INFUSION,
    UMBRAL_HIPER,
    UMBRAL_HIPO,
)
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_rango_base,
    calcular_proximo_control,
    obtener_tasa_algoritmo_1,
)


def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_rango_base()
    resultado["mostrar_resultado"] = True
    resultado["conducta_extra"] = ""
    resultado["alerta_borde_hipo"] = False
    resultado["alerta_rango"] = ""
    resultado["requiere_recontrol"] = False
    resultado["observacion"] = ""
    resultado["ui_variant"] = "success"
    resultado["en_objetivo"] = False
    resultado["en_objetivo_con_alerta"] = False
    resultado["fuera_objetivo"] = False
    resultado["tasa"] = ""
    resultado["mostrar_tasa"] = False

    # SIN INFUSIÓN ACTIVA
    if not infusion_activa:
        if not (UMBRAL_HIPO <= actual <= UMBRAL_HIPER):
            return None

        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

        # 70 a 89
        if UMBRAL_HIPO <= actual <= Decimal("89"):
            resultado["estado"] = "En rango con alerta"
            resultado["subestado"] = "Cercano a hipoglucemia"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite inferior."
            resultado["conducta"] = "Mantener vigilancia clínica."
            resultado["conducta_extra"] = "Reforzar control por cercanía a hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Cercano a hipoglucemia"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["comentario_control"] = (
                "Paciente sin infusión activa y dentro del rango objetivo."
            )
            resultado["observacion"] = "Cercanía al límite inferior del objetivo."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

        # 90 a 160
        if Decimal("90") <= actual <= Decimal("160"):
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = "Paciente no insulinizado"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Glucemia dentro del objetivo."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["comentario_control"] = (
                "Paciente sin infusión activa y dentro del rango objetivo."
            )
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            return resultado

        # 161 a 180
        if Decimal("161") <= actual <= UMBRAL_HIPER:
            resultado["estado"] = "En rango con alerta"
            resultado["subestado"] = "Cercano a hiperglucemia"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite superior."
            resultado["conducta"] = "Vigilar evolución clínica."
            resultado["conducta_extra"] = "Controlar tendencia."
            resultado["alerta_rango"] = "Cercano a hiperglucemia"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["comentario_control"] = (
                "Paciente sin infusión activa y dentro del rango objetivo."
            )
            resultado["observacion"] = "Cercanía al límite superior del objetivo."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

    # CON INFUSIÓN ACTIVA
    if infusion_activa:
        if not (UMBRAL_HIPO <= actual <= OBJETIVO_MAX_INFUSION):
            return None

        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"
        resultado["tasa"] = obtener_tasa_algoritmo_1(actual)
        resultado["mostrar_tasa"] = True

        # 70 a 119
        if UMBRAL_HIPO <= actual < LIMITE_SUSPENDER_INFUSION:
            resultado["estado"] = "Fuera de objetivo por debajo"
            resultado["subestado"] = "Paciente insulinizado con glucemia < 120 mg/dL"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "Valor bajo para paciente con infusión activa."
            resultado["conducta"] = "Suspender la infusión de insulina."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            resultado["suspender_insulina"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 hora"
            resultado["comentario_control"] = (
                "Con infusión activa y glucemia < 120 mg/dL corresponde suspender la infusión."
            )
            resultado["observacion"] = "Por debajo del rango objetivo insulinizado."
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        # 120 a 139
        if LIMITE_SUSPENDER_INFUSION <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Fuera de objetivo por debajo"
            resultado["subestado"] = "Paciente insulinizado por debajo del rango objetivo"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "No está en rango objetivo insulinizado."
            resultado["conducta"] = "Suspender la infusión de insulina."
            resultado["requiere_recontrol"] = True
            resultado["suspender_insulina"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 hora"
            resultado["comentario_control"] = (
                "Glucemia por debajo del rango objetivo para paciente insulinizado."
            )
            resultado["observacion"] = "Rango objetivo insulinizado: 140 a 200 mg/dL."
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        # 140 a 200
        if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
            resultado["estado"] = "Glucemia en Objetivo"
            resultado["subestado"] = "Paciente con infusión activa"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Valor dentro del objetivo para paciente con infusión activa."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["comentario_control"] = (
                "Paciente en rango objetivo. Continuar monitoreo cada 6 horas."
            )

            if actual <= Decimal("150"):
                resultado["alerta_rango"] = "Cercano al límite inferior"
                resultado["subestado"] = "Cercano al límite inferior"
                resultado["ui_variant"] = "warning"
                resultado["en_objetivo_con_alerta"] = True
            elif actual >= Decimal("190"):
                resultado["alerta_rango"] = "Cercano al límite superior"
                resultado["subestado"] = "Cercano al límite superior"
                resultado["ui_variant"] = "warning"
                resultado["en_objetivo_con_alerta"] = True
            else:
                resultado["ui_variant"] = "success"
                resultado["en_objetivo"] = True

            return resultado

    return None