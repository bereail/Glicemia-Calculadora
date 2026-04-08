from .constants import (
    UMBRAL_HIPO,
    LIMITE_ZONA_INTERMEDIA,
    UMBRAL_HIPER,
)
from .helpers import _a_decimal, _a_bool, _resultado_base


def evaluar_hipoglucemia(actual, previa=None, infusion_activa=False):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_base()

    if actual <= UMBRAL_HIPO:
        resultado["estado"] = "hipoglucemia"
        resultado["subestado"] = "Glucemia actual <= 70 mg/dL"
        resultado["mensaje"] = "Paciente en hipoglucemia."
        resultado["conducta"] = (
            "Suspender insulina si está en infusión, administrar 50 ml de dextrosa al 25% "
            "y controlar glucemia a los 30 minutos."
        )
        resultado["suspender_insulina"] = infusion_activa
        resultado["administrar_dextrosa"] = True
        resultado["requiere_recontrol"] = True
        resultado["proximo_control"] = "Controlar glucemia a los 30 minutos"
        resultado["mostrar_resultado"] = True
        return resultado

    if previa is not None and previa <= UMBRAL_HIPO and actual > UMBRAL_HIPO:
        resultado["mostrar_resultado"] = True
        resultado["requiere_recontrol"] = True

        if UMBRAL_HIPO < actual <= LIMITE_ZONA_INTERMEDIA:
            resultado["estado"] = "recontrol_post_hipoglucemia"
            resultado["subestado"] = "Glucemia entre 71 y 120 mg/dL"
            resultado["mensaje"] = "Recuperación inicial post-hipoglucemia."
            resultado["conducta"] = "Mantener insulina suspendida y controlar glucemia cada 1 hora."
            resultado["suspender_insulina"] = infusion_activa
            resultado["proximo_control"] = "Controlar glucemia cada 1 hora"
            return resultado

        if LIMITE_ZONA_INTERMEDIA < actual < UMBRAL_HIPER:
            resultado["estado"] = "recontrol_post_hipoglucemia"
            resultado["subestado"] = "Glucemia entre 121 y 179 mg/dL"
            resultado["mensaje"] = "Recuperación adecuada post-hipoglucemia."
            resultado["conducta"] = "Continuar monitoreo cada 1 hora. No reiniciar insulina de inmediato."
            resultado["suspender_insulina"] = infusion_activa
            resultado["proximo_control"] = "Continuar monitoreo cada 1 hora"
            return resultado

        if actual >= UMBRAL_HIPER:
            resultado["estado"] = "rebote_post_hipoglucemia"
            resultado["subestado"] = "Glucemia >= 180 mg/dL en recontrol post-hipoglucemia"
            resultado["mensaje"] = "Posible rebote transitorio post-corrección."
            resultado["conducta"] = "Confirmar nueva medición y reevaluar reinicio o ajuste de insulina."
            resultado["reiniciar_insulina"] = infusion_activa
            resultado["proximo_control"] = "Confirmar nueva medición en 1 hora"
            return resultado

    return None