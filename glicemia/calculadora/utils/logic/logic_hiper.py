from decimal import Decimal

from ..constants import UMBRAL_ALERTA_ALTA, UMBRAL_HIPER
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_hiper_base,
    armar_resultado_insulinizacion,
    calcular_proximo_control,
)

# =========================================================
# ESCALONES Y ALGORITMOS
# =========================================================


def obtener_escalon_glucemia(glicemia):
    glicemia = _a_decimal(glicemia)

    if glicemia < Decimal("120"):
        return "E0"
    if glicemia <= Decimal("149"):
        return "E1"
    if glicemia <= Decimal("179"):
        return "E2"
    if glicemia <= Decimal("209"):
        return "E3"
    if glicemia <= Decimal("239"):
        return "E4"
    if glicemia <= Decimal("269"):
        return "E5"
    if glicemia <= Decimal("299"):
        return "E6"
    if glicemia <= Decimal("329"):
        return "E7"
    if glicemia <= Decimal("359"):
        return "E8"
    return "E9"


def obtener_tasa_algoritmo_1(glicemia):
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
    return tabla[obtener_escalon_glucemia(glicemia)]


def obtener_tasa_algoritmo_2(glicemia):
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
    return tabla[obtener_escalon_glucemia(glicemia)]


def obtener_tasa_por_algoritmo(glicemia, algoritmo=1):
    if algoritmo == 1:
        return obtener_tasa_algoritmo_1(glicemia)
    if algoritmo == 2:
        return obtener_tasa_algoritmo_2(glicemia)
    raise ValueError("Algoritmo inválido. Debe ser 1 o 2.")


def estan_en_mismo_escalon(*valores):
    escalones = [obtener_escalon_glucemia(v) for v in valores if v is not None]
    if len(escalones) < 2:
        return False
    return len(set(escalones)) == 1


def _numero_escalon(valor):
    escalon = obtener_escalon_glucemia(valor)
    return int(escalon.replace("E", ""))


def estan_en_escalon_persistencia(*valores):
    valores_validos = [v for v in valores if v is not None]
    if len(valores_validos) < 3:
        return False

    numeros = [_numero_escalon(v) for v in valores_validos]
    return max(numeros) - min(numeros) <= 1


def _marcar_visual(resultado, *, es_critico=False, nivel_visual="alerta"):
    resultado["es_critico"] = es_critico
    resultado["nivel_visual"] = nivel_visual
    return resultado


def es_hiperglucemia_persistente(
    actual, previa=None, anterior=None, infusion_activa=False
):
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
        and actual > UMBRAL_ALERTA_ALTA
        and actual < Decimal("360")
        and previa > UMBRAL_ALERTA_ALTA
        and previa < Decimal("360")
        and anterior > UMBRAL_ALERTA_ALTA
        and anterior < Decimal("360")
        and estan_en_escalon_persistencia(actual, previa, anterior)
    ):
        return True

    return False


def es_fallo_algoritmo_1(
    actual, previa=None, infusion_activa=False, hubo_ajuste_insulina=False
):
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


def sugerir_algoritmo(
    actual,
    previa=None,
    anterior=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
):
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

    if not infusion_activa and actual < UMBRAL_HIPER:
        return None

    if infusion_activa and actual <= Decimal("200"):
        return None

    resultado = _resultado_hiper_base()
    resultado["mostrar_resultado"] = True
    resultado["es_critico"] = False
    resultado["nivel_visual"] = "alerta"
    resultado["texto_rango_objetivo"] = (
        "Paciente insulinizado: 140 a 200 mg/dL"
        if infusion_activa
        else "Paciente no insulinizado: 70 a 180 mg/dL"
    )

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

    if actual >= Decimal("360"):
        if previa is not None and previa >= Decimal("360"):
            resultado["estado"] = "Hiperglucemia Persistente"
            resultado["subestado"] = "2 controles consecutivos ≥ 360 mg/dL con infusión activa"
            resultado["mensaje"] = "Hiperglucemia persistente severa."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Dar aviso médico y continuar con Algoritmo 2."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            resultado["observacion"] = "Persistencia severa con infusión activa."
            _asignar_control(actual)
            return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

        resultado["estado"] = "Hiperglucemia Sostenida"
        resultado["subestado"] = "Actual ≥ 360 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia sostenida."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Obtener glicemia previa para confirmar persistencia."
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = "Se necesita confirmar persistencia con una medición previa."
        _asignar_control(actual)
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    if actual > UMBRAL_ALERTA_ALTA and actual < Decimal("360"):
        if es_hiperglucemia_persistente(
            actual=actual,
            previa=previa,
            anterior=tercera_medicion,
            infusion_activa=infusion_activa,
        ):
            resultado["estado"] = "Hiperglucemia Persistente"
            resultado["subestado"] = (
                "Tres controles consecutivos > 200 mg/dL y < 360 mg/dL "
                "en el mismo escalón o en escalones contiguos"
            )
            resultado["mensaje"] = "Hiperglucemia persistente fuera del rango objetivo."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Dar aviso médico y seguir Algoritmo 2 según protocolo."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            resultado["observacion"] = "Persistencia confirmada por criterios de escalón."
            _asignar_control(actual)
            return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

        if es_fallo_algoritmo_1(
            actual=actual,
            previa=previa,
            infusion_activa=infusion_activa,
            hubo_ajuste_insulina=hubo_ajuste_insulina,
        ):
            resultado["estado"] = "Hiperglucemia Refractaria"
            resultado["subestado"] = "Mismo escalón fuera de objetivo pese a ajuste previo"
            resultado["mensaje"] = "Probable fallo del Algoritmo 1."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Considerar cambio a Algoritmo 2 y dar aviso médico."
            resultado["requiere_recontrol"] = True
            resultado["algoritmo_sugerido"] = "Algoritmo 2"
            resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_2(actual)
            resultado["observacion"] = "Persistencia fuera de objetivo pese a ajuste previo."
            _asignar_control(actual)
            return _marcar_visual(resultado, es_critico=True, nivel_visual="critico")

        if (
            previa is not None
            and previa > UMBRAL_ALERTA_ALTA
            and previa < Decimal("360")
        ):
            resultado["estado"] = "Hiperglucemia"
            resultado["subestado"] = (
                "Dos controles consecutivos > 200 mg/dL, aún sin criterio de persistencia"
            )
            resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
            resultado["resumen_objetivo"] = "Fuera de rango objetivo"
            resultado["conducta"] = "Obtener tercera medición para evaluar persistencia por escalón."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Obtener tercera medición"
            resultado["comentario_control"] = (
                "Evaluar si las 3 mediciones permanecen > 200 mg/dL y < 360 mg/dL "
                "en el mismo escalón o en escalones contiguos."
            )
            resultado["observacion"] = "Aún no cumple criterios completos de persistencia."
            return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

        resultado["estado"] = "Hiperglucemia Marcada"
        resultado["subestado"] = "Actual > 200 mg/dL con infusión activa"
        resultado["mensaje"] = "Hiperglucemia fuera del rango objetivo."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = "Requiere recontrol y evaluación de tendencia."
        resultado["requiere_recontrol"] = True
        resultado["observacion"] = "Valor fuera de rango con necesidad de seguimiento cercano."
        _asignar_control(actual)
        return _marcar_visual(resultado, es_critico=False, nivel_visual="alerta")

    return None