from ..constants import UMBRAL_HIPO
from ..helpers import (
    _a_bool,
    _a_decimal,
    _resultado_hipo_base,
)


def evaluar_hipoglucemia(actual, previa=None, infusion_activa=False):
    """
    Evalúa únicamente hipoglucemia actual (<= 70).
    No evalúa recontrol ni rebote post-hipoglucemia.
    """
    actual = _a_decimal(actual)
    infusion_activa = _a_bool(infusion_activa)

    texto_rango_objetivo = (
        "Paciente insulinizado: 140 a 200 mg/dL"
        if infusion_activa
        else "Paciente no insulinizado: 70 a 180 mg/dL"
    )

    # =========================================================
    # 1) HIPOGLUCEMIA ACTUAL
    # =========================================================
    if actual <= UMBRAL_HIPO:
        resultado = _resultado_hipo_base()
        resultado["mostrar_resultado"] = True
        resultado["estado"] = "Hipoglucemia"
        resultado["subestado"] = "Glucemia actual ≤ 70 mg/dL"
        resultado["mensaje"] = "Paciente en hipoglucemia."
        resultado["resumen_objetivo"] = "Fuera de rango objetivo"
        resultado["conducta"] = (
            "Suspender insulina y administrar 50 ml de dextrosa al 25%."
        )
        resultado["conducta_extra"] = (
            "Si la glucemia continúa ≤ 70 mg/dL, repetir tratamiento según protocolo."
        )
        resultado["suspender_insulina"] = infusion_activa
        resultado["administrar_dextrosa"] = True
        resultado["requiere_recontrol"] = True
        resultado["proximo_control"] = "Controlar glucemia nuevamente en 30 minutos"
        resultado["texto_rango_objetivo"] = texto_rango_objetivo
        resultado["observacion"] = (
            "Priorizar corrección inmediata y recontrol a los 30 minutos. "
            "Evaluar dar aviso al médico."
        )
        return resultado

    return None