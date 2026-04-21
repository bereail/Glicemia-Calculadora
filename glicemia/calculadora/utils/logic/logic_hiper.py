from ..constants import UMBRAL_FUERA_OBJETIVO_ALTO, UMBRAL_HIPER, UMBRAL_REFRACTARIA
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_hiper_base,
    armar_resultado_insulinizacion,
    calcular_proximo_control,
    mismo_escalon,
    obtener_escalon_algoritmo,
    obtener_tasa_algoritmo_2,
    obtener_tasa_por_algoritmo,
    tres_mediciones_mismo_escalon,
)


def _marcar_visual(resultado, *, es_critico=False, nivel_visual="alerta"):
    resultado["es_critico"] = es_critico
    resultado["es_critica"] = es_critico
    resultado["nivel_visual"] = nivel_visual
    return resultado


def cumple_dos_mayor_igual_360(actual, previa=None):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    if previa is None:
        return False

    return actual >= UMBRAL_REFRACTARIA and previa >= UMBRAL_REFRACTARIA


def cumple_tres_mayor_200_menor_360_mismo_escalon(actual, previa=None, anterior=None):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    anterior = _a_decimal(anterior, permitir_none=True)

    if previa is None or anterior is None:
        return False

    return (
        actual > UMBRAL_FUERA_OBJETIVO_ALTO
        and actual < UMBRAL_REFRACTARIA
        and previa > UMBRAL_FUERA_OBJETIVO_ALTO
        and previa < UMBRAL_REFRACTARIA
        and anterior > UMBRAL_FUERA_OBJETIVO_ALTO
        and anterior < UMBRAL_REFRACTARIA
        and tres_mediciones_mismo_escalon(anterior, previa, actual)
    )


def es_hiperglucemia_persistente_algoritmo_1(
    actual,
    previa=None,
    anterior=None,
    infusion_activa=False,
    algoritmo_activo=1,
):
    if not _a_bool(infusion_activa):
        return False

    if int(algoritmo_activo) != 1:
        return False

    return (
        cumple_dos_mayor_igual_360(actual, previa)
        or cumple_tres_mayor_200_menor_360_mismo_escalon(actual, previa, anterior)
    )


def es_hiperglucemia_refractaria_algoritmo_2(
    actual,
    previa=None,
    anterior=None,
    infusion_activa=False,
    algoritmo_activo=1,
):
    if not _a_bool(infusion_activa):
        return False

    if int(algoritmo_activo) != 2:
        return False

    return (
        cumple_dos_mayor_igual_360(actual, previa)
        or cumple_tres_mayor_200_menor_360_mismo_escalon(actual, previa, anterior)
    )


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
        anterior=anterior,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        return 2

    if es_hiperglucemia_persistente_algoritmo_1(
        actual=actual,
        previa=previa,
        anterior=anterior,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        return 2

    return int(algoritmo_activo or 1)


def evaluar_hiperglucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    algoritmo_activo=1,
    horas_desde_inicio=None,
    estable=False,
):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)
    algoritmo_activo = int(algoritmo_activo or 1)

    if not infusion_activa and actual < UMBRAL_HIPER:
        return None

    if infusion_activa and actual <= UMBRAL_FUERA_OBJETIVO_ALTO:
        return None

    resultado = _resultado_hiper_base()
    resultado["mostrar_resultado"] = True
    resultado["texto_rango_objetivo"] = (
        "Paciente insulinizado: 140 a 200 mg/dL"
        if infusion_activa
        else "Paciente no insulinizado: 70 a 180 mg/dL"
    )
    resultado["algoritmo_activo"] = f"Algoritmo {algoritmo_activo}"
    resultado["algoritmo_usado"] = f"Algoritmo {algoritmo_activo}"

    def _asignar_control(valor, insulinizado=False):
        control = calcular_proximo_control(
            valor,
            insulinizado=insulinizado,
            horas_desde_inicio=horas_desde_inicio,
            estable=estable,
        )
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
    resultado["escalon_algoritmo"] = obtener_escalon_algoritmo(actual)

    # ------------------------------------------------------
    # HGR - ALGORITMO 2
    # ------------------------------------------------------
    if es_hiperglucemia_refractaria_algoritmo_2(
        actual=actual,
        previa=previa,
        anterior=tercera_medicion,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        if cumple_dos_mayor_igual_360(actual, previa):
            resultado["subestado"] = (
                "Dos mediciones consecutivas ≥ 360 mg/dL durante Algoritmo 2"
            )
            resultado["observacion"] = (
                "Hiperglucemia refractaria por dos mediciones consecutivas ≥ 360 mg/dL."
            )
        else:
            resultado["subestado"] = (
                "Tres mediciones consecutivas > 200 y < 360 mg/dL en el mismo escalón durante Algoritmo 2"
            )
            resultado["observacion"] = (
                "Hiperglucemia refractaria por persistencia en el mismo escalón."
            )

        resultado["estado"] = "Hiperglucemia Refractaria"
        resultado["mensaje"] = "Hiperglucemia refractaria."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = (
            "Dar aviso médico de guardia para definir conducta individualizada."
        )
        resultado["requiere_recontrol"] = True
        resultado["algoritmo_activo"] = "Algoritmo 2"
        resultado["algoritmo_usado"] = "Algoritmo 2"
        resultado["algoritmo_sugerido"] = "Algoritmo 2"
        resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
        resultado["clasificacion_protocolo"] = "HGR"
        resultado["escalamiento_clinico"] = "refractaria"
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

    # ------------------------------------------------------
    # HGP - ALGORITMO 1
    # ------------------------------------------------------
    if es_hiperglucemia_persistente_algoritmo_1(
        actual=actual,
        previa=previa,
        anterior=tercera_medicion,
        infusion_activa=infusion_activa,
        algoritmo_activo=algoritmo_activo,
    ):
        if cumple_dos_mayor_igual_360(actual, previa):
            resultado["subestado"] = (
                "Dos mediciones consecutivas ≥ 360 mg/dL durante Algoritmo 1"
            )
            resultado["observacion"] = (
                "Hiperglucemia persistente por dos mediciones consecutivas ≥ 360 mg/dL."
            )
        else:
            resultado["subestado"] = (
                "Tres mediciones consecutivas > 200 y < 360 mg/dL en el mismo escalón durante Algoritmo 1"
            )
            resultado["observacion"] = (
                "Hiperglucemia persistente por persistencia en el mismo escalón."
            )

        resultado["estado"] = "Hiperglucemia Persistente"
        resultado["mensaje"] = "Hiperglucemia persistente fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Dar aviso médico y continuar con Algoritmo 2."
        resultado["requiere_recontrol"] = True
        resultado["algoritmo_sugerido"] = "Algoritmo 2"
        resultado["clasificacion_protocolo"] = "HGP"
        resultado["escalamiento_clinico"] = "persistente"
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

    # ------------------------------------------------------
    # 2 FUERA DE RANGO EN MISMO ESCALÓN -> +0,5 UI/h
    # solo si TODAVÍA no cumple HGP/HGR
    # ------------------------------------------------------
    if (
        previa is not None
        and actual > UMBRAL_FUERA_OBJETIVO_ALTO
        and previa > UMBRAL_FUERA_OBJETIVO_ALTO
        and mismo_escalon(actual, previa)
        and tercera_medicion is None
    ):
        resultado["estado"] = "Hiperglucemia Fuera de Objetivo"
        resultado["subestado"] = (
            "Dos controles consecutivos fuera del rango objetivo en el mismo escalón"
        )
        resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = (
            f"Seguir {resultado['algoritmo_activo']} y aumentar 0,5 UI/h."
        )
        resultado["velocidad_sugerida"] = "Aumentar 0,5 UI/h"
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = (
            "Dos controles consecutivos fuera del rango objetivo en el mismo escalón."
        )
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    # ------------------------------------------------------
    # 2 MEDICIONES >200, PERO FALTA TERCERA
    # ------------------------------------------------------
    if (
        previa is not None
        and actual > UMBRAL_FUERA_OBJETIVO_ALTO
        and previa > UMBRAL_FUERA_OBJETIVO_ALTO
        and tercera_medicion is None
    ):
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
            "Evaluar si las 3 mediciones permanecen > 200 y < 360 mg/dL en el mismo escalón."
        )
        resultado["observacion"] = (
            "Aún no cumple criterios completos de hiperglucemia persistente o refractaria."
        )
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    # ------------------------------------------------------
    # >200 Y <=360
    # ------------------------------------------------------
    if actual > UMBRAL_FUERA_OBJETIVO_ALTO and actual < UMBRAL_REFRACTARIA:
        resultado["estado"] = "Hiperglucemia Marcada"
        resultado["subestado"] = "Actual > 200 mg/dL y < 360 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Requiere recontrol y evaluación de tendencia."
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = (
            "Valor fuera de rango con necesidad de seguimiento cercano."
        )
        _asignar_control(actual, insulinizado=True)
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    # ------------------------------------------------------
    # >=360 sola, sin segunda medición todavía
    # ------------------------------------------------------
    resultado["estado"] = "Hiperglucemia Severa"
    resultado["subestado"] = "Glucemia ≥ 360 mg/dL con infusión activa"
    resultado["mensaje"] = "Hiperglucemia severa fuera del rango objetivo."
    resultado["resumen_objetivo"] = "Fuera de rango objetivo"
    resultado["conducta"] = "Requiere seguimiento estrecho y reevaluación inmediata."
    resultado["requiere_recontrol"] = True
    resultado["observacion"] = (
        "Si se repite ≥ 360 mg/dL, clasificar según algoritmo en uso."
    )
    _asignar_control(actual, insulinizado=True)
    return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")