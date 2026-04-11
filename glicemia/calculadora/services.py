from .utils.resolver import resolver_glucemia


def evaluar_glucemia_service(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    horas_desde_inicio=None,
    estable=False,
):
    return resolver_glucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )