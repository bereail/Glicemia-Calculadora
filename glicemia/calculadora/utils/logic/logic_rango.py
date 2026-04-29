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
    obtener_tasa_por_algoritmo,
)
def obtener_limites(infusion_activa):
    if infusion_activa:
        return OBJETIVO_MIN_INFUSION, OBJETIVO_MAX_INFUSION
    return UMBRAL_HIPO, UMBRAL_HIPER



def evaluar_rango_70_180(
    actual,
    previa=None,
    infusion_activa=False,
    algoritmo_activo=1,
    horas_desde_inicio=None,
    estable=False,
):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    algoritmo_activo = int(algoritmo_activo or 1)

    print("RANGO algoritmo_activo:", algoritmo_activo)
    print("RANGO actual:", actual)

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
    resultado["algoritmo_activo"] = f"Algoritmo {algoritmo_activo}"
    resultado["infusion_activa"] = infusion_activa
    resultado["glicemia_previa"] = previa

    def _asignar_control(valor):
        control = calcular_proximo_control(
            glicemia=valor,
            insulinizado=infusion_activa,
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )
        resultado["proximo_control"] = control["proximo_control"]
        resultado["comentario_control"] = control["comentario_control"]

    # ... el resto de tu lógica queda igual ...

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
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 - 2 horas"
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
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1- 2 horas"
            resultado["observacion"] = f"Cercanía al límite superior ({limite_superior} mg/dL)."
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            return resultado

        return None

    # =========================================================
    # CON INFUSIÓN ACTIVA
    # =========================================================
    if infusion_activa:
        if not (UMBRAL_HIPO < actual <= OBJETIVO_MAX_INFUSION):
            return None

        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"

        # 🔴 REGLA NUEVA:
        # si actual <= 120 con infusión activa, SIEMPRE suspender
        if actual <= Decimal("120"):
            resultado["estado"] = "Debajo de Objetivo con Infusión"
            resultado["subestado"] = "Glucemia ≤ 120 mg/dL con infusión activa"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "Valor bajo para paciente con infusión activa."
            resultado["conducta"] = "Suspender insulina"
            resultado["terapia"] = "Suspender UI/h"
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            resultado["tasa"] = "Suspender"
            resultado["mostrar_tasa"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 - 2 horas"
            resultado["comentario_control"] = (
                "Si la infusión está activa, debe suspenderse y recontrolar cada hora."
            )
            resultado["observacion"] = (
                "Paciente con infusión activa y glucemia ≤ 120 mg/dL: suspender insulina."
            )
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        # 121 a 139
        # Acá ya no suspende automáticamente, pero sigue siendo valor bajo para insulinizado.
        # Y desde UI ya podés preguntar algoritmo 1/2 porque actual > 120.
        if Decimal("121") <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Debajo de Objetivo con Infusión"
            resultado["subestado"] = "Glucemia entre 121 y 139 mg/dL con infusión activa"
            resultado["resumen_objetivo"] = "Por debajo del rango objetivo"
            resultado["mensaje"] = "Valor bajo para paciente con infusión activa."
            resultado["conducta"] = "Evaluar riesgo de hipoglucemia."
            resultado["alerta_borde_hipo"] = True
            resultado["alerta_rango"] = "Por debajo del objetivo"
            resultado["requiere_recontrol"] = True
            tasa_data = obtener_tasa_por_algoritmo(actual, algoritmo_activo)
            print("RANGO tasa_data:", tasa_data)

            resultado["tasa"] = tasa_data.get("texto") or tasa_data.get("valor")
            resultado["mostrar_tasa"] = True
            _asignar_control(actual)
            resultado["observacion"] = (
                f"Por debajo del límite inferior ({limite_inferior} mg/dL)."
            )
            resultado["ui_variant"] = "warning"
            resultado["fuera_objetivo"] = True
            return resultado

        # 140 a 200
    if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
        resultado["estado"] = "Glucemia en Objetivo"
        resultado["resumen_objetivo"] = "Dentro de rango"
        resultado["mensaje"] = "Valor dentro del objetivo para paciente con infusión activa."
        resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
        tasa_data = obtener_tasa_por_algoritmo(actual, algoritmo_activo)
        print("RANGO tasa_data:", tasa_data)

        resultado["tasa"] = tasa_data.get("texto") or tasa_data.get("valor")
        resultado["mostrar_tasa"] = True

        if Decimal("140") <= actual <= Decimal("160"):
            resultado["subestado"] = "En objetivo con alerta: cercano al límite inferior"
            resultado["alerta_rango"] = "Cercano al límite inferior"
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 - 2 horas"
            resultado["comentario_control"] = (
                "Paciente insulinizado dentro de rango objetivo, pero cercano al límite inferior. "
                "Continuar monitoreo estrecho."
            )
            return resultado

        if Decimal("180") <= actual <= Decimal("200"):
            resultado["subestado"] = "En objetivo con alerta: cercano al límite superior"
            resultado["alerta_rango"] = "Cercano al límite superior"
            resultado["ui_variant"] = "warning"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 - 2 horas"
            resultado["comentario_control"] = (
                "Paciente insulinizado dentro de rango objetivo, pero cercano al límite superior. "
                "Continuar monitoreo estrecho."
            )
            return resultado

        resultado["ui_variant"] = "success"
        resultado["en_objetivo"] = True
        resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
        resultado["comentario_control"] = (
            "Paciente en rango objetivo. Continuar monitoreo cada 6 horas."
        )
        return resultado