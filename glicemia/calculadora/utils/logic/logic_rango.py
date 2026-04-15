from decimal import Decimal

from ..constants import (
    OBJETIVO_MAX_INFUSION,
    OBJETIVO_MIN_INFUSION,
    UMBRAL_HIPER,
    UMBRAL_HIPO,
)
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_base,
    calcular_proximo_control,
)
from .logic_hiper import obtener_tasa_algoritmo_1


def obtener_limites(infusion_activa):
    if infusion_activa:
        return OBJETIVO_MIN_INFUSION, OBJETIVO_MAX_INFUSION
    return UMBRAL_HIPO, UMBRAL_HIPER


def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    limite_inferior, limite_superior = obtener_limites(infusion_activa)

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
    resultado["tasa"] = None
    resultado["mostrar_tasa"] = False

    def _asignar_control(valor):
        control = calcular_proximo_control(
            glicemia=valor,
            insulinizado=infusion_activa,
        )
        resultado["proximo_control"] = control["proximo_control"]
        resultado["comentario_control"] = control["comentario_control"]

    # =========================================================
    # SIN INFUSIÓN ACTIVA
    # =========================================================
    if not infusion_activa:
        if not (UMBRAL_HIPO <= actual < UMBRAL_HIPER):
            return None

        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

        # 70 a 90
        if UMBRAL_HIPO <= actual <= Decimal("90"):
            resultado["estado"] = "Objetivo con alerta"
            resultado["subestado"] = "Cercano a hipoglucemia"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite inferior."
            resultado["conducta"] = "Mantener vigilancia clínica."
            resultado["conducta_extra"] = "Reforzar control por cercanía a hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Cercano a hipoglucemia"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["observacion"] = f"Cercanía al límite inferior ({limite_inferior} mg/dL)."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

        # 91 a 160
        if Decimal("91") <= actual <= Decimal("160"):
            resultado["estado"] = "En Objetivo"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Glucemia dentro del objetivo."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            return resultado

        # 161 a 179
        if Decimal("161") <= actual < UMBRAL_HIPER:
            resultado["estado"] = "Objetivo con alerta"
            resultado["subestado"] = "Cercano a hiperglucemia"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["mensaje"] = "Valor dentro del objetivo, pero cercano al límite superior."
            resultado["conducta"] = "Vigilar evolución clínica."
            resultado["conducta_extra"] = "Controlar tendencia."
            resultado["alerta_rango"] = "Cercano a hiperglucemia"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["observacion"] = f"Cercanía al límite superior ({limite_superior} mg/dL)."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

    # =========================================================
    # CON INFUSIÓN ACTIVA
    # =========================================================
    if infusion_activa:
        if not (UMBRAL_HIPO <= actual <= OBJETIVO_MAX_INFUSION):
            return None

        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"
        resultado["tasa"] = obtener_tasa_algoritmo_1(actual)
        resultado["mostrar_tasa"] = True

        # 70 a 139
        if UMBRAL_HIPO <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Debajo de Objetivo con Infusión"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "Valor bajo para paciente con infusión activa."
            resultado["conducta"] = "Evaluar riesgo de hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            _asignar_control(actual)
            resultado["observacion"] = f"Por debajo del límite inferior ({limite_inferior} mg/dL)."
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        # 140 a 200 (todo el rango usa protocolo real)
      # 140 a 200 (EN OBJETIVO → SIEMPRE 6 HORAS)
    if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
        resultado["estado"] = "Glucemia en Objetivo"
        resultado["resumen_objetivo"] = "Dentro de rango"
        resultado["mensaje"] = "Valor dentro del objetivo para paciente con infusión activa."
        resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."

        # ALERTAS visuales
        if actual <= Decimal("150"):
            resultado["subestado"] = "Cercano al límite inferior"
            resultado["alerta_rango"] = "Cercano al límite inferior"
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo_con_alerta"] = True

        elif actual >= Decimal("190"):
            resultado["subestado"] = "Cercano al límite superior"
            resultado["alerta_rango"] = "Cercano al límite superior"
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo_con_alerta"] = True

        else:
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True

        # 🔥 CONTROL FIJO (REGLA TUYA)
        resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
        resultado["comentario_control"] = (
            "Paciente en rango objetivo. Continuar monitoreo cada 6 horas."
        )

        return resultado
    return None