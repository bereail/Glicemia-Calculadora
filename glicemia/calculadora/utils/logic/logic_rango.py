from decimal import Decimal

from ..constants import (LIMITE_ZONA_INTERMEDIA, OBJETIVO_MAX_INFUSION,
                         OBJETIVO_MIN_INFUSION, UMBRAL_HIPER, UMBRAL_HIPO)
from ..helpers import _a_bool, _a_decimal, _resultado_base


def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    """
    Evalúa glucemias en rango o cercanas a rango, sin invadir la lógica de hiperglucemia real.

    Reglas:
    - Sin infusión:
        * 70-90   -> en rango, pero cercano a hipoglucemia
        * 91-120  -> en rango
        * 121-179 -> por encima del objetivo, aún sin criterio de hiperglucemia
    - Con infusión:
        * 70-120  -> alerta por cercanía a hipoglucemia
        * 121-139 -> por debajo del objetivo con infusión
        * 140-200 -> en objetivo con infusión
    """

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True
    resultado["alerta_borde_hipo"] = False
    resultado["conducta_extra"] = None
    resultado["recordatorio_objetivo"] = (
        "Objetivo sin insulinización: 70–120 mg/dL. "
        "Con insulinización: 140–200 mg/dL."
    )

    # =========================================================
    # SIN INFUSIÓN ACTIVA
    # =========================================================
    if not infusion_activa:
        # Solo evalúa hasta 179 sin infusión.
        # >=180 ya es hiperglucemia y debe resolverlo logic_hiper.
        if not (UMBRAL_HIPO <= actual < UMBRAL_HIPER):
            return None

        # 70-90: rango, pero cercano a hipo
        if UMBRAL_HIPO <= actual <= Decimal("90"):
            resultado["estado"] = "En Rango"
            resultado["subestado"] = None
            resultado["mensaje"] = "Valor dentro de rango, pero cercano a hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["conducta"] = "Mantener vigilancia clínica."
            resultado["conducta_extra"] = "Evaluar y consultar médico de guardia."
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

        # Sin previa
        if previa is None:
            if Decimal("91") <= actual <= Decimal("120"):
                resultado["estado"] = "En Rango"
                resultado["subestado"] = None
                resultado["mensaje"] = "Glucemia dentro del objetivo."
                resultado["conducta"] = "Continuar monitoreo."
                resultado["proximo_control"] = "Según monitoreo habitual"
                return resultado

            if Decimal("121") <= actual < UMBRAL_HIPER:
                resultado["estado"] = "Límite Alto"
                resultado["subestado"] = "Glucemia entre 121 y 179 mg/dL"
                resultado["mensaje"] = (
                    "Valor por encima del objetivo sin criterio de hiperglucemia."
                )
                resultado["conducta"] = (
                    "Solicitar nueva medición para evaluar tendencia."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Nueva medición para valorar tendencia"
                return resultado

        # Con previa
        if previa is not None:
            if actual > previa:
                resultado["estado"] = "Ascenso en Rango"
                resultado["subestado"] = None
                resultado["mensaje"] = "Glucemia en ascenso dentro del rango evaluado."
                resultado["conducta"] = (
                    "Control evolutivo para evaluar si continúa en ascenso."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Recontrol según evolución clínica"
                return resultado

            if actual < previa:
                resultado["estado"] = "Descenso en Rango"
                resultado["subestado"] = None
                resultado["mensaje"] = "Glucemia en descenso dentro del rango evaluado."
                resultado["conducta"] = (
                    "Vigilar evolución para evitar hipoglucemia si continúa bajando."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Recontrol según evolución clínica"
                return resultado

            resultado["estado"] = "Estable en Rango"
            resultado["subestado"] = None
            resultado["mensaje"] = "Glucemia estable dentro del rango evaluado."
            resultado["conducta"] = "Continuar monitoreo."
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

    # =========================================================
    # CON INFUSIÓN ACTIVA
    # =========================================================
    if infusion_activa:
        # Con infusión, el rango clínico llega hasta 200.
        # >200 debe ir a logic_hiper.
        if not (UMBRAL_HIPO <= actual <= OBJETIVO_MAX_INFUSION):
            return None

        if previa is None:
            # 70-120 con infusión: alerta por borde hipo
            if UMBRAL_HIPO <= actual <= LIMITE_ZONA_INTERMEDIA:
                resultado["estado"] = "En Rango"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor dentro de rango, pero cercano a hipoglucemia."
                )
                resultado["alerta_borde_hipo"] = True
                resultado["conducta"] = "Mantener vigilancia clínica."
                resultado["conducta_extra"] = "Evaluar y consultar médico de guardia."
                resultado["proximo_control"] = "Según monitoreo habitual"
                return resultado

            # 121-139 con infusión
            if LIMITE_ZONA_INTERMEDIA < actual < OBJETIVO_MIN_INFUSION:
                resultado["estado"] = "Debajo de Objetivo con Infusión"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor por debajo del objetivo para paciente con infusión activa."
                )
                resultado["conducta"] = (
                    "Evaluar descenso y considerar ajuste de insulina por riesgo de hipoglucemia."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Control frecuente según protocolo"
                return resultado

            # 140-200 con infusión = objetivo
            if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
                resultado["estado"] = "Objetivo con Infusión"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor dentro del objetivo para paciente con infusión activa."
                )
                resultado["conducta"] = (
                    "Mantener conducta actual y continuar monitoreo."
                )
                resultado["proximo_control"] = "Según protocolo"
                return resultado

        # Con previa
        if previa is not None:
            # 70-120 con infusión: alerta por borde hipo
            if UMBRAL_HIPO <= actual <= LIMITE_ZONA_INTERMEDIA:
                resultado["estado"] = "En Rango"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor dentro de rango, pero cercano a hipoglucemia."
                )
                resultado["alerta_borde_hipo"] = True
                resultado["conducta"] = "Mantener vigilancia clínica."
                resultado["conducta_extra"] = "Evaluar y consultar médico de guardia."
                resultado["proximo_control"] = "Según monitoreo habitual"
                return resultado

            # 121-139 con infusión
            if LIMITE_ZONA_INTERMEDIA < actual < OBJETIVO_MIN_INFUSION:
                resultado["estado"] = "Debajo de Objetivo con Infusión"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor por debajo del objetivo para paciente con infusión activa."
                )
                resultado["conducta"] = (
                    "Evaluar descenso y considerar ajuste de insulina por riesgo de hipoglucemia."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Control frecuente según protocolo"
                return resultado

            # 140-200 con infusión = objetivo
            if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
                if actual < previa:
                    resultado["estado"] = "Objetivo con Descenso"
                    resultado["subestado"] = None
                    resultado["mensaje"] = (
                        "Dentro de objetivo con tendencia descendente."
                    )
                    resultado["conducta"] = (
                        "Vigilar riesgo de hipoglucemia y reevaluar infusión."
                    )
                    resultado["requiere_recontrol"] = True
                    resultado["proximo_control"] = "Control según protocolo"
                    return resultado

                if actual > previa:
                    resultado["estado"] = "Objetivo con Ascenso"
                    resultado["subestado"] = None
                    resultado["mensaje"] = (
                        "Dentro de objetivo con tendencia ascendente."
                    )
                    resultado["conducta"] = "Mantener monitoreo y evaluar tendencia."
                    resultado["requiere_recontrol"] = True
                    resultado["proximo_control"] = "Control según protocolo"
                    return resultado

                resultado["estado"] = "Objetivo con Infusión"
                resultado["subestado"] = None
                resultado["mensaje"] = (
                    "Valor dentro del objetivo para paciente con infusión activa."
                )
                resultado["conducta"] = (
                    "Mantener conducta actual y continuar monitoreo."
                )
                resultado["proximo_control"] = "Según protocolo"
                return resultado

    return None
