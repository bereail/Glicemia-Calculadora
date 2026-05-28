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
    aplicar_presentacion_terapia,
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

    # =========================================================
    # SIN INFUSIÓN ACTIVA
    # =========================================================
    if not infusion_activa:
        if not (UMBRAL_HIPO <= actual < UMBRAL_HIPER):
            return None

        resultado["texto_rango_objetivo"] = "Paciente no insulinizado: 70 a 180 mg/dL"

        # 70 a 90
        if UMBRAL_HIPO <= actual < Decimal("90"):
            resultado["estado"] = "Glucemia con alerta"
            resultado["subestado"] = "Cercano a hipoglucemia"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["conducta"] = "Mantener vigilancia clínica"
            resultado["alerta_borde_hipo"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 4 hora"
            resultado["ui_variant"] = "danger"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = True
            resultado = aplicar_presentacion_terapia(
                resultado,
                infusion_activa=infusion_activa,
            )

            return resultado
        
        # 91 a 160
        if Decimal("90") <= actual < UMBRAL_HIPER:
            resultado["estado"] = "Glucemia en objetivo"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["conducta"] = "Mantener conducta actual"
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"
            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            resultado = aplicar_presentacion_terapia(
                resultado,
                infusion_activa=infusion_activa,
            )

            return resultado

        return None

    # =========================================================
    # CON INFUSIÓN ACTIVA
    # =========================================================
    if infusion_activa:
        if not (UMBRAL_HIPO < actual <= OBJETIVO_MAX_INFUSION):
            return None

        resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"

        # 🔴 71 a 90 con infusión activa
        if UMBRAL_HIPO < actual <= Decimal("90"):
            resultado["estado"] = "Glucemia por debajo de objetivo"
            resultado["subestado"] = "Riesgo de hipoglucemia"
            resultado["resumen_objetivo"] = "Fuera de rango"
            resultado["conducta"] = "Suspender insulina"
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 1 hora"
            resultado["ui_variant"] = "danger"
            resultado["fuera_objetivo"] = True
        # No mostrar Terapia en este caso
            resultado["mostrar_terapia"] = False
            resultado["terapia"] = None
            resultado["tasa_infusional"] = None

            return resultado

        # 🟠 91 a 119 con infusión activa
        if Decimal("90") < actual < Decimal("120"):
            resultado["estado"] = "Glucemia por debajo de objetivo"
            resultado["subestado"] = "Glucemia baja con infusión activa"
            resultado["resumen_objetivo"] = "Fuera de rango"
            resultado["conducta"] = "Suspender insulina"
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Controlar glucemia nuevamente en 2 horas"
            resultado["ui_variant"] = "danger"
            resultado["fuera_objetivo"] = True
        # No mostrar Terapia en este caso
            resultado["mostrar_terapia"] = False
            resultado["terapia"] = None
            resultado["tasa_infusional"] = None

            return resultado
                # 120 a 139
        if Decimal("120") <= actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "Glucemia por debajo de objetivo"
            resultado["subestado"] = "Glucemia baja con infusión activa"
            resultado["conducta"] = "Evaluar riesgo de hipoglucemia"

            tasa_data = obtener_tasa_por_algoritmo(actual, algoritmo_activo)

            resultado["tasa"] = tasa_data.get("texto") or tasa_data.get("valor")
            resultado["tasa_algoritmo"] = resultado["tasa"]

            resultado["mostrar_tasa"] = True

            _asignar_control(actual)

            resultado["ui_variant"] = "danger"
            resultado["fuera_objetivo"] = True

            resultado = aplicar_presentacion_terapia(
                resultado,
                infusion_activa=infusion_activa,
            )

            return resultado
        # 140 a 200
        if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
            resultado["estado"] = "Glucemia en objetivo con infusión"
            resultado["resumen_objetivo"] = "Dentro de rango"
            resultado["conducta"] = "Mantener conducta actual"

            tasa_data = obtener_tasa_por_algoritmo(actual, algoritmo_activo)

            resultado["tasa"] = tasa_data.get("texto") or tasa_data.get("valor")
            resultado["tasa_algoritmo"] = resultado["tasa"]

            resultado["mostrar_tasa"] = True

            resultado["ui_variant"] = "success"
            resultado["en_objetivo"] = True
            resultado["en_objetivo_con_alerta"] = False
            resultado["fuera_objetivo"] = False
            resultado["alerta_rango"] = ""

            resultado["proximo_control"] = "Controlar glucemia nuevamente en 6 horas"

            resultado = aplicar_presentacion_terapia(
                resultado,
                infusion_activa=infusion_activa,
            )

            return resultado
    return None