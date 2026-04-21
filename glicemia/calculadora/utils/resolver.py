from .helpers import _a_bool, _a_decimal, _aplicar_tendencia
from .logic.logic_hiper import evaluar_hiperglucemia
from .logic.logic_hipo import evaluar_hipoglucemia
from .logic.logic_rango import evaluar_rango_70_180


def resolver_glucemia(
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
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)
    algoritmo_activo = int(algoritmo_activo or 1)
    estable = _a_bool(estable)

    # Se conserva por compatibilidad con el form / view,
    # aunque ya no define HGP/HGR en la lógica final.
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)

    # 1) Hipoglucemia / post-hipoglucemia
    resultado = evaluar_hipoglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado:
        return _aplicar_tendencia(resultado, actual, previa)

    # 2) En rango / por debajo del objetivo insulinizado
    resultado = evaluar_rango_70_180(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado:
        return _aplicar_tendencia(resultado, actual, previa)

    # 3) Hiperglucemia
    resultado = evaluar_hiperglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
        algoritmo_activo=algoritmo_activo,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )
    if resultado:
        return _aplicar_tendencia(resultado, actual, previa)

    # fallback defensivo
    return {
        "mostrar_resultado": True,
        "estado": "Sin clasificación",
        "subestado": "",
        "clase": "sin_clasificacion",
        "mensaje": "No se pudo clasificar el valor ingresado.",
        "conducta": "Revisar datos cargados.",
        "proximo_control": "",
        "observacion": "",
        "tendencia": "",
        "flecha_tendencia": "",
        "delta": "",
    }