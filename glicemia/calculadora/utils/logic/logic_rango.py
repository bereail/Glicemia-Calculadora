from decimal import Decimal

from ..constants import (
    OBJETIVO_MAX_INFUSION,
    OBJETIVO_MIN_INFUSION,
    UMBRAL_HIPER,
    UMBRAL_HIPO,
)
from ..helpers import _a_bool, _a_decimal, _resultado_base


def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    """
    Evalúa glucemias dentro de rango objetivo o cercanas a sus límites.

    Reglas:
    - Sin infusión:
        * 70-90   -> en objetivo, cercano a hipoglucemia
        * 91-160  -> en objetivo
        * 161-179 -> en objetivo, cercano a hiperglucemia
    - Con infusión:
        * 70-139  -> debajo de objetivo con infusión
        * 140-150 -> en objetivo, cercano al límite inferior
        * 151-189 -> en objetivo
        * 190-200 -> en objetivo, cercano al límite superior
    """

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True
    resultado["conducta_extra"] = None
    resultado["alerta_borde_hipo"] = False
    resultado["alerta_rango"] = ""

    # =========================================================
    # SIN INFUSIÓN ACTIVA
    # =========================================================
    if not infusion_activa:
        # Solo clasifica entre 70 y 179
        if not (UMBRAL_HIPO <= actual < UMBRAL_HIPER):
            return None

        if UMBRAL_HIPO <= actual <= Decimal("90"):
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = "Cercano a hipoglucemia"
            resultado["mensaje"] = (
                "Valor dentro del objetivo, pero cercano al límite inferior."
            )
            resultado["conducta"] = "Mantener vigilancia clínica."
            resultado["conducta_extra"] = (
                "Reforzar control por cercanía a hipoglucemia."
            )
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Cercano a hipoglucemia"
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

        if Decimal("91") <= actual <= Decimal("160"):
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = None
            resultado["mensaje"] = "Glucemia dentro del objetivo."
            resultado["conducta"] = "Continuar monitoreo."
            resultado["alerta_rango"] = ""
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

        if Decimal("161") <= actual < UMBRAL_HIPER:
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = "Cercano a hiperglucemia"
            resultado["mensaje"] = (
                "Valor dentro del objetivo, pero cercano al límite superior."
            )
            resultado["conducta"] = "Vigilar evolución clínica."
            resultado["conducta_extra"] = (
                "Controlar tendencia por cercanía a hiperglucemia."
            )
            resultado["alerta_rango"] = "Cercano a hiperglucemia"
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

    # =========================================================
    # CON INFUSIÓN ACTIVA
    # =========================================================
    if infusion_activa:
        # Solo clasifica entre 70 y 200
        if not (UMBRAL_HIPO <= actual <= OBJETIVO_MAX_INFUSION):
            return None

        if UMBRAL_HIPO <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Debajo de Objetivo con Infusión"
            resultado["subestado"] = (
                "Valor bajo para paciente con infusión activa"
            )
            resultado["mensaje"] = (
                "Valor por debajo del objetivo en paciente con infusión activa."
            )
            resultado["conducta"] = (
                "Evaluar riesgo de hipoglucemia y reevaluar conducta."
            )
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Control frecuente según protocolo"
            return resultado

        if OBJETIVO_MIN_INFUSION <= actual <= Decimal("150"):
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = "Cercano al límite inferior"
            resultado["mensaje"] = (
                "Valor dentro del objetivo, pero cercano al límite inferior."
            )
            resultado["conducta"] = "Mantener monitoreo estrecho."
            resultado["alerta_rango"] = "Cercano al límite inferior"
            resultado["proximo_control"] = "Según protocolo"
            return resultado

        if Decimal("151") <= actual <= Decimal("189"):
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = None
            resultado["mensaje"] = (
                "Valor dentro del objetivo para paciente con infusión activa."
            )
            resultado["conducta"] = (
                "Mantener conducta actual y continuar monitoreo."
            )
            resultado["alerta_rango"] = ""
            resultado["proximo_control"] = "Según protocolo"
            return resultado

        if Decimal("190") <= actual <= OBJETIVO_MAX_INFUSION:
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = "Cercano al límite superior"
            resultado["mensaje"] = (
                "Valor dentro del objetivo, pero cercano al límite superior."
            )
            resultado["conducta"] = (
                "Vigilar tendencia y mantener monitoreo."
            )
            resultado["alerta_rango"] = "Cercano al límite superior"
            resultado["proximo_control"] = "Según protocolo"
            return resultado

    return None