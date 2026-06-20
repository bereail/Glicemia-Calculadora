from .utils.resolver import resolver_glucemia


def evaluar_glucemia_service(
    actual,
    previa=None,
    infusion_activa=False,
    tercera_medicion=None,
    algoritmo_activo=1,
    horas_desde_inicio=None,
    estable=False,
):

    return resolver_glucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        tercera_medicion=tercera_medicion,
        algoritmo_activo=algoritmo_activo,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )