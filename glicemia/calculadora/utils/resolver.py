from .helpers import _a_bool, _a_decimal, _aplicar_tendencia, _resultado_base
from .logic.logic_hiper import evaluar_hiperglucemia
from .logic.logic_hipo import evaluar_hipoglucemia
from .logic.logic_rango import evaluar_rango_70_180


def resolver_glucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    horas_desde_inicio=None,
    estable=False,
):
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    estable = _a_bool(estable)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)

    # 1) Hipoglucemia
    resultado = evaluar_hipoglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado is not None:
        return _aplicar_tendencia(resultado, actual, previa)

    # 2) Rango / objetivo
    resultado = evaluar_rango_70_180(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado is not None:
        return _aplicar_tendencia(resultado, actual, previa)

    # 3) Hiperglucemia
    resultado = evaluar_hiperglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
    )
    if resultado is not None:
        return _aplicar_tendencia(resultado, actual, previa)

    # 4) Fallback
    resultado = _resultado_base()
    resultado["estado"] = "Sin Clasificación"
    resultado["subestado"] = "No se pudo clasificar el caso"
    resultado["mensaje"] = "Revisar datos ingresados."
    resultado["conducta"] = "Validar entradas y lógica del flujo."
    resultado["mostrar_resultado"] = True
    return resultado


def resolver_flujo_glucemia(
    actual,
    insulinizado=False,
    previa=None,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    horas_desde_inicio=None,
    estable=False,
):
    return resolver_glucemia(
        actual=actual,
        previa=previa,
        infusion_activa=insulinizado,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )