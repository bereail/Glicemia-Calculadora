from decimal import Decimal

from ..constants import (
    OBJETIVO_MAX_INFUSION,
    OBJETIVO_MIN_INFUSION,
    UMBRAL_HIPER,
    UMBRAL_HIPO,
)
from ..helpers import _a_bool, _a_decimal, _resultado_base
from .logic_hiper import obtener_tasa_algoritmo_1


def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True
    resultado["conducta_extra"] = None
    resultado["alerta_borde_hipo"] = False
    resultado["alerta_rango"] = ""
    resultado["requiere_recontrol"] = False
    resultado["resumen_objetivo"] = ""
    resultado["observacion"] = ""

    resultado["ui_variant"] = "success"
    resultado["en_objetivo"] = False
    resultado["en_objetivo_con_alerta"] = False
    resultado["fuera_objetivo"] = False

    # NUEVO
    resultado["tasa"] = None

    if not infusion_activa:
        if not (UMBRAL_HIPO <= actual < UMBRAL_HIPER):
            return None

        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

        if UMBRAL_HIPO <= actual <= Decimal("90"):
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = "Cercano a hipoglucemia"
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite inferior."
            resultado["conducta"] = "Mantener vigilancia clínica."
            resultado["conducta_extra"] = "Reforzar control por cercanía a hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Cercano a hipoglucemia"
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Valor en objetivo, con cercanía al límite inferior."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

        if Decimal("91") <= actual <= Decimal("160"):
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = None
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Glucemia dentro del objetivo."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["alerta_rango"] = ""
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Sin alertas de proximidad a los límites del rango."
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            return resultado

        if Decimal("161") <= actual < UMBRAL_HIPER:
            resultado["estado"] = "En Objetivo"
            resultado["subestado"] = "Cercano a hiperglucemia"
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite superior."
            resultado["conducta"] = "Vigilar evolución clínica."
            resultado["conducta_extra"] = "Controlar tendencia por cercanía a hiperglucemia."
            resultado["alerta_rango"] = "Cercano a hiperglucemia"
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Valor en objetivo, con cercanía al límite superior."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

    if infusion_activa:
        if not (UMBRAL_HIPO <= actual <= OBJETIVO_MAX_INFUSION):
            return None

        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"

        # NUEVO: mostrar tasa con infusión activa
        resultado["tasa"] = obtener_tasa_algoritmo_1(actual)

        if UMBRAL_HIPO <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Debajo de Objetivo con Infusión"
            resultado["subestado"] = "Valor bajo para paciente con infusión activa"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "Valor por debajo del objetivo en paciente con infusión activa."
            resultado["conducta"] = "Evaluar riesgo de hipoglucemia y reevaluar conducta."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Paciente con infusión activa por debajo del rango deseado."
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        if OBJETIVO_MIN_INFUSION <= actual <= Decimal("150"):
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = "Cercano al límite inferior"
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite inferior."
            resultado["conducta"] = "Mantener monitoreo estrecho."
            resultado["conducta_extra"] = "Vigilar tendencia por proximidad al límite inferior."
            resultado["alerta_rango"] = "Cercano al límite inferior"
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Valor en objetivo, cercano al límite inferior del rango con infusión."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

        if Decimal("151") <= actual <= Decimal("189"):
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = None
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Valor dentro del objetivo para paciente con infusión activa."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["alerta_rango"] = ""
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Sin alertas de proximidad a los límites del rango con infusión."
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            return resultado

        if Decimal("190") <= actual <= OBJETIVO_MAX_INFUSION:
            resultado["estado"] = "Objetivo con Infusión"
            resultado["subestado"] = "Cercano al límite superior"
            resultado["resumen_objetivo"] = "En rango objetivo"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite superior."
            resultado["conducta"] = "Vigilar tendencia y mantener monitoreo."
            resultado["conducta_extra"] = "Controlar evolución por proximidad al límite superior."
            resultado["alerta_rango"] = "Cercano al límite superior"
            resultado["proximo_control"] = "Controlar glicemia nuevamente en 1 hora"
            resultado["observacion"] = "Valor en objetivo, cercano al límite superior del rango con infusión."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

    return None