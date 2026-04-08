from decimal import Decimal

from .constants import (
    UMBRAL_HIPER,
    UMBRAL_ALERTA_ALTA,
)
from .helpers import (
    _a_decimal,
    _a_bool,
    _resultado_base,
    calcular_proximo_control,
    armar_resultado_insulinizacion,
)


# =========================================================
# ESCALONES Y ALGORITMOS
# =========================================================

def obtener_escalon_glucemia(glucemia):
    glucemia = _a_decimal(glucemia)

    if glucemia < Decimal("120"):
        return "E0"
    if glucemia <= Decimal("149"):
        return "E1"
    if glucemia <= Decimal("179"):
        return "E2"
    if glucemia <= Decimal("209"):
        return "E3"
    if glucemia <= Decimal("239"):
        return "E4"
    if glucemia <= Decimal("269"):
        return "E5"
    if glucemia <= Decimal("299"):
        return "E6"
    if glucemia <= Decimal("329"):
        return "E7"
    if glucemia <= Decimal("359"):
        return "E8"
    return "E9"


def obtener_tasa_algoritmo_1(glucemia):
    tabla = {
        "E0": "Suspender",
        "E1": "0,5 UI/h",
        "E2": "1 UI/h",
        "E3": "1,5 UI/h",
        "E4": "2 UI/h",
        "E5": "2,5 UI/h",
        "E6": "3 UI/h",
        "E7": "3,5 UI/h",
        "E8": "4 UI/h",
        "E9": "5 UI/h",
    }
    return tabla[obtener_escalon_glucemia(glucemia)]


def obtener_tasa_algoritmo_2(glucemia):
    tabla = {
        "E0": "Suspender",
        "E1": "1 UI/h",
        "E2": "1,5 UI/h",
        "E3": "2,5 UI/h",
        "E4": "3 UI/h",
        "E5": "3,5 UI/h",
        "E6": "4 UI/h",
        "E7": "5 UI/h",
        "E8": "6 UI/h",
        "E9": "8 UI/h",
    }
    return tabla[obtener_escalon_glucemia(glucemia)]


def obtener_tasa_por_algoritmo(glucemia, algoritmo=1):
    if algoritmo == 1:
        return obtener_tasa_algoritmo_1(glucemia)
    if algoritmo == 2:
        return obtener_tasa_algoritmo_2(glucemia)
    raise ValueError("Algoritmo inválido. Debe ser 1 o 2.")


def estan_en_mismo_escalon(*valores):
    escalones = [obtener_escalon_glucemia(v) for v in valores if v is not None]
    if len(escalones) < 2:
        return False
    return len(set(escalones)) == 1


# =========================================================
# REGLAS CLÍNICAS DE HIPER
# =========================================================

def es_hiperglucemia_persistente(actual, previa=None, anterior=None, infusion_activa=False):
    """
    Persistente si:
    - con infusión activa y 2 controles consecutivos >= 360
    - o 3 controles consecutivos > 200 en el mismo escalón
    """
    if not _a_bool(infusion_activa):
        return False

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    anterior = _a_decimal(anterior, permitir_none=True)

    if previa is not None and actual >= Decimal("360") and previa >= Decimal("360"):
        return True

    if (
        previa is not None
        and anterior is not None
        and actual > Decimal("200")
        and previa > Decimal("200")
        and anterior > Decimal("200")
        and estan_en_mismo_escalon(actual, previa, anterior)
    ):
        return True

    return False


def es_fallo_algoritmo_1(actual, previa=None, infusion_activa=False, hubo_ajuste_insulina=False):
    """
    Fallo algoritmo 1:
    - paciente con infusión activa
    - 2 controles consecutivos en el mismo escalón
    - ambos fuera del rango objetivo 140-200
    - y ya hubo ajuste de insulina
    """
    if not _a_bool(infusion_activa):
        return False

    if not _a_bool(hubo_ajuste_insulina):
        return False

    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    if previa is None:
        return False

    fuera_objetivo_actual = actual < Decimal("140") or actual > Decimal("200")
    fuera_objetivo_previa = previa < Decimal("140") or previa > Decimal("200")

    return (
        fuera_objetivo_actual
        and fuera_objetivo_previa
        and estan_en_mismo_escalon(actual, previa)
    )


def sugerir_algoritmo(actual, previa=None, anterior=None, infusion_activa=False, hubo_ajuste_insulina=False):
    """
    Sugerencia:
    - Algoritmo 2 si hay persistente
    - Algoritmo 2 si hubo ajuste y persiste en mismo escalón fuera de objetivo
    - sino Algoritmo 1
    """
    if es_hiperglucemia_persistente(
        actual=actual,
        previa=previa,
        anterior=anterior,
        infusion_activa=infusion_activa,
    ):
        return 2

    if es_fallo_algoritmo_1(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
    ):
        return 2

    return 1


# =========================================================
# EVALUACIÓN PRINCIPAL
# =========================================================

def evaluar_hiperglucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)

    if actual < UMBRAL_HIPER:
        return None

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True

    def _asignar_control(valor):
        control = calcular_proximo_control(valor)
        resultado["proximo_control"] = control["proximo_control"]
        resultado["comentario_control"] = control["comentario_control"]

    # ======================================================
    # SIN INFUSIÓN ACTIVA
    # ======================================================
    if not infusion_activa:
        if previa is None:
            resultado["estado"] = "Hiperglucemia Aislada"
            resultado["subestado"] = "Una medición >= 180 mg/dL sin infusión activa"
            resultado["mensaje"] = "Hiperglucemia aislada."
            resultado["conducta"] = "Solicitar nueva medición para confirmar persistencia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Nueva medición para confirmar persistencia"
            return resultado

        if previa >= UMBRAL_HIPER:
            return armar_resultado_insulinizacion(actual)

        resultado["estado"] = "Hiperglucemia en ascenso"
        resultado["subestado"] = "Actual >= 180 mg/dL con previa < 180 mg/dL"
        resultado["mensaje"] = "Hiperglucemia en ascenso."
        resultado["conducta"] = "Requiere nueva medición para evaluar persistencia."
        resultado["requiere_recontrol"] = True
        resultado["proximo_control"] = "Nueva medición"
        return resultado

    # ======================================================
    # CON INFUSIÓN ACTIVA
    # ======================================================
    algoritmo_sugerido = sugerir_algoritmo(
        actual=actual,
        previa=previa,
        anterior=tercera_medicion,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
    )

    resultado["algoritmo_sugerido"] = f"Algoritmo {algoritmo_sugerido}"
    resultado["tasa_algoritmo"] = obtener_tasa_por_algoritmo(actual, algoritmo_sugerido)

    # ------------------------------------------------------
    # 1) >= 360 con infusión activa
    # ------------------------------------------------------
    if actual >= Decimal("360"):
        if previa is not None and previa >= Decimal("360"):
            resultado["estado"] = "Hiperglucemia Persistente"
            resultado["subestado"] = "2 controles consecutivos ≥ 360 mg/dL con infusión activa"
            resultado["mensaje"] = "Hiperglucemia persistente severa."
            resultado["conducta"] = "Dar aviso médico y continuar con Algoritmo 2."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            _asignar_control(actual)
            return resultado

        resultado["estado"] = "Hiperglucemia Sostenida"
        resultado["subestado"] = "Actual ≥ 360 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia sostenida."
        resultado["conducta"] = "Obtener glicemia previa para confirmar persistencia."
        resultado["requiere_recontrol"] = True
        _asignar_control(actual)
        return resultado

    # ------------------------------------------------------
    # 2) > 200 y < 360
    # ------------------------------------------------------
    if actual > UMBRAL_ALERTA_ALTA:
        if es_hiperglucemia_persistente(
            actual=actual,
            previa=previa,
            anterior=tercera_medicion,
            infusion_activa=infusion_activa,
        ):
            resultado["estado"] = "Hiperglucemia Persistente"
            resultado["subestado"] = "Tres controles consecutivos > 200 mg/dL en el mismo escalón"
            resultado["mensaje"] = "Hiperglucemia persistente fuera del rango objetivo."
            resultado["conducta"] = "Dar aviso médico y seguir Algoritmo 2 según protocolo."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            _asignar_control(actual)
            return resultado

        if es_fallo_algoritmo_1(
            actual=actual,
            previa=previa,
            infusion_activa=infusion_activa,
            hubo_ajuste_insulina=hubo_ajuste_insulina,
        ):
            resultado["estado"] = "Hiperglucemia Refractaria"
            resultado["subestado"] = "Mismo escalón fuera de objetivo pese a ajuste previo"
            resultado["mensaje"] = "Probable fallo del Algoritmo 1."
            resultado["conducta"] = "Considerar cambio a Algoritmo 2 y dar aviso médico."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            _asignar_control(actual)
            return resultado

        if previa is not None and previa > UMBRAL_ALERTA_ALTA:
            resultado["estado"] = "Hiperglucemia Fuera de Objetivo"
            resultado["subestado"] = "Dos controles consecutivos > 200 mg/dL, aún sin criterio de persistencia"
            resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
            resultado["conducta"] = "Obtener tercera medición para evaluar persistencia por escalón."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Obtener tercera medición"
            resultado["comentario_control"] = (
                "Evaluar si las 3 mediciones permanecen > 200 mg/dL en el mismo escalón."
            )
            return resultado

        resultado["estado"] = "Hiperglucemia Marcada"
        resultado["subestado"] = "Actual > 200 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
        resultado["conducta"] = "Requiere recontrol y evaluación de tendencia."
        resultado["requiere_recontrol"] = True
        _asignar_control(actual)
        return resultado

    # ------------------------------------------------------
    # 3) 180 - 200 con infusión activa
    # ------------------------------------------------------
    resultado["estado"] = "Hiperglucemia en rango alto"
    resultado["subestado"] = "Valor dentro de rango alto con infusión activa"
    resultado["mensaje"] = "Continuar monitoreo y ajustar según evolución."
    resultado["conducta"] = "Seguir algoritmo vigente."
    resultado["requiere_recontrol"] = True
    _asignar_control(actual)
    return resultado