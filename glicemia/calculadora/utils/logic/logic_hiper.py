from decimal import Decimal

from ..constants import UMBRAL_ALERTA_ALTA, UMBRAL_HIPER
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_hiper_base,
    armar_resultado_insulinizacion,
    calcular_proximo_control,
    dos_ultimas_mayores_360,
    obtener_tasa_algoritmo_1,
    obtener_tasa_algoritmo_2,
    obtener_tasa_por_algoritmo,
    tres_mediciones_mismo_escalon,
)


def _marcar_visual(resultado, *, es_critico=False, nivel_visual="alerta"):
    resultado["es_critico"] = es_critico
    resultado["nivel_visual"] = nivel_visual
    return resultado


def es_hiperglucemia_persistente_algoritmo_1(
    actual, previa=None, anterior=None, infusion_activa=False
):
    if not _a_bool(infusion_activa):
        return False

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    anterior = _a_decimal(anterior, permitir_none=True)

    # 🔴 NUEVA REGLA: 2 ≥ 360 = PERSISTENTE
    if previa is not None:
        if actual >= Decimal("360") and previa >= Decimal("360"):
            return True

    # 🔵 REGLA ORIGINAL (3 mediciones)
    if actual <= Decimal("200"):
        return False

    if previa is None or anterior is None:
        return False

    return (
        actual > Decimal("200")
        and previa > Decimal("200")
        and anterior > Decimal("200")
        and tres_mediciones_mismo_escalon(anterior, previa, actual)
    )


def es_hiperglucemia_refractaria_algoritmo_2(
    actual, previa=None, infusion_activa=False, algoritmo_activo=1
):
    if not _a_bool(infusion_activa):
        return False

    if int(algoritmo_activo) != 2:
        return False

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    return dos_ultimas_mayores_360(previa, actual)


def sugerir_algoritmo(
    actual,
    previa=None,
    anterior=None,
    infusion_activa=False,
    algoritmo_activo=1,
):
    if es_hiperglucemia_refractaria_algoritmo_2(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        return 2

    if es_hiperglucemia_persistente_algoritmo_1(
        actual=actual,
        previa=previa,
        anterior=anterior,
        infusion_activa=infusion_activa,
    ):
        return 2

    return int(algoritmo_activo)


def evaluar_hiperglucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    algoritmo_activo=1,
):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)
    algoritmo_activo = int(algoritmo_activo or 1)

    if not infusion_activa and actual < UMBRAL_HIPER:
        return None

    if infusion_activa and actual <= Decimal("200"):
        return None

    resultado = _resultado_hiper_base()
    resultado["mostrar_resultado"] = True
    resultado["es_critica"] = False
    resultado["nivel_visual"] = "alerta"
    resultado["texto_rango_objetivo"] = (
        "Paciente insulinizado: 140 a 200 mg/dL"
        if infusion_activa
        else "Paciente no insulinizado: 70 a 180 mg/dL"
    )
    resultado["algoritmo_activo"] = f"Algoritmo {algoritmo_activo}"

    def _asignar_control(valor, insulinizado=False):
        control = calcular_proximo_control(valor, insulinizado=insulinizado)
        resultado["proximo_control"] = control["proximo_control"]
        resultado["comentario_control"] = control["comentario_control"]

    # ======================================================
    # SIN INFUSIÓN ACTIVA
    # ======================================================
    if not infusion_activa:
        if previa is None:
            resultado["estado"] = "Hiperglucemia Aislada"
            resultado["subestado"] = "Una medición ≥ 180 mg/dL sin infusión activa"
            resultado["mensaje"] = "Hiperglucemia aislada."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Solicitar nueva medición para confirmar persistencia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Obtener nueva medición para confirmar persistencia"
            resultado["observacion"] = "Una sola medición no confirma persistencia."
            return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

        if previa >= UMBRAL_HIPER:
            resultado = armar_resultado_insulinizacion(actual)
            resultado["texto_rango_objetivo"] = "Paciente insulinizado: 140 a 200 mg/dL"
            return resultado

        resultado["estado"] = "Hiperglucemia en Ascenso"
        resultado["subestado"] = "Actual ≥ 180 mg/dL con previa < 180 mg/dL"
        resultado["mensaje"] = "Hiperglucemia en ascenso."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Requiere nueva medición para evaluar persistencia."
        resultado["requiere_recontrol"] = True
        resultado["proximo_control"] = "Obtener nueva medición"
        resultado["observacion"] = "La tendencia ascendente requiere confirmación."
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    # ======================================================
    # CON INFUSIÓN ACTIVA Y FUERA DE OBJETIVO > 200
    # ======================================================
    algoritmo_sugerido = sugerir_algoritmo(
        actual=actual,
        previa=previa,
        anterior=tercera_medicion,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    )

    resultado["algoritmo_sugerido"] = f"Algoritmo {algoritmo_sugerido}"
    resultado["tasa_algoritmo"] = obtener_tasa_por_algoritmo(actual, algoritmo_activo)

    # ------------------------------------------------------
    # ALGORITMO 2 + >360 en 2 últimas = REFRACTARIA
    # ------------------------------------------------------
    if es_hiperglucemia_refractaria_algoritmo_2(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        resultado["estado"] = "Hiperglucemia Refractaria"
        resultado["subestado"] = (
            "Dos mediciones consecutivas > 360 mg/dL durante Algoritmo 2"
        )
        resultado["mensaje"] = "Hiperglucemia refractaria."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = (
            "Dar aviso médico de guardia para definir conducta individualizada."
        )
        resultado["requiere_recontrol"] = True
        resultado["algoritmo_activo"] = "Algoritmo 2"
        resultado["algoritmo_sugerido"] = "Algoritmo 2"
        resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
        resultado["clasificacion_protocolo"] = "HGR"
        resultado["observacion"] = (
            "Fallo del Algoritmo 2 en último escalón con glucemias > 360 mg/dL."
        )
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

    # ------------------------------------------------------
    # ALGORITMO 1 + 3 mediciones >200 en mismo escalón = PERSISTENTE
    # ------------------------------------------------------
    if algoritmo_activo == 1 and es_hiperglucemia_persistente_algoritmo_1(
        actual=actual,
        previa=previa,
        anterior=tercera_medicion,
        infusion_activa=infusion_activa,
    ):
        resultado["estado"] = "Hiperglucemia Persistente"
        resultado["subestado"] = (
            "Tres mediciones consecutivas > 200 mg/dL en el mismo escalón durante Algoritmo 1"
        )
        resultado["mensaje"] = "Hiperglucemia persistente fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Dar aviso médico y continuar con Algoritmo 2."
        resultado["requiere_recontrol"] = True
        resultado["algoritmo_sugerido"] = "Algoritmo 2"
        resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
        resultado["clasificacion_protocolo"] = "HGP"
        resultado["observacion"] = (
            "Fallo del Algoritmo 1: persistencia fuera de objetivo en el mismo escalón."
        )
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

    # ------------------------------------------------------
    # >360 pero sin criterio completo aún
    # ------------------------------------------------------
    if actual > Decimal("360"):
        if previa is None:
            resultado["estado"] = "Hiperglucemia Marcada"
            resultado["subestado"] = "Actual > 360 mg/dL con infusión activa"
            resultado["mensaje"] = "Hiperglucemia marcada."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Obtener glicemia previa para evaluar evolución."
            resultado["requiere_recontrol"] = True
            resultado["observacion"] = "Aún no hay segunda medición para definir conducta."
            _asignar_control(actual, insulinizado=True)
            return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

        resultado["estado"] = "Hiperglucemia Severa"
        resultado["subestado"] = "Glucemia > 360 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia severa fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Requiere seguimiento estrecho y reevaluación inmediata."
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = "Si repite > 360 mg/dL en Algoritmo 2, considerar refractaria."
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

    # ------------------------------------------------------
    # >200 y <360 con infusión activa
    # ------------------------------------------------------
    if actual > UMBRAL_ALERTA_ALTA and actual <= Decimal("360"):
        if previa is not None and tercera_medicion is None:
            resultado["estado"] = "Hiperglucemia Fuera de Objetivo"
            resultado["subestado"] = (
                "Dos mediciones consecutivas > 200 mg/dL con infusión activa"
            )
            resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Obtener tercera medición para evaluar persistencia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Obtener tercera medición"
            resultado["comentario_control"] = (
                "Evaluar si las 3 mediciones permanecen > 200 mg/dL en el mismo escalón."
            )
            resultado["observacion"] = "Aún no cumple criterios completos de hiperglucemia persistente."
            return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

        resultado["estado"] = "Hiperglucemia Marcada"
        resultado["subestado"] = "Actual > 200 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Requiere recontrol y evaluación de tendencia."
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = "Valor fuera de rango con necesidad de seguimiento cercano."
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    return None