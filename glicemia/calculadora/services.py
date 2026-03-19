from dataclasses import dataclass
from typing import Optional, Literal
from decimal import Decimal

Algoritmo = Literal["alg1", "alg2"]

ALG1 = [
    (None, 119, None),
    (120, 149, Decimal("0.5")),
    (150, 179, Decimal("1")),
    (180, 209, Decimal("1.5")),
    (210, 239, Decimal("2")),
    (240, 269, Decimal("2.5")),
    (270, 299, Decimal("3")),
    (300, 329, Decimal("3.5")),
    (330, 359, Decimal("4")),
    (360, None, Decimal("5")),
]

ALG2 = [
    (None, 119, None),
    (120, 149, Decimal("1")),
    (150, 179, Decimal("1.5")),
    (180, 209, Decimal("2.5")),
    (210, 239, Decimal("3")),
    (240, 269, Decimal("3.5")),
    (270, 299, Decimal("4")),
    (300, 329, Decimal("4.5")),
    (330, 359, Decimal("5")),
    (360, None, Decimal("6")),
]


@dataclass
class ResultadoFlujo:
    estado: str
    titulo: str
    mensaje: str
    requiere_paso: Optional[str] = None
    mostrar_algoritmo: bool = False
    mostrar_hgp: bool = False
    mostrar_hgr: bool = False

def evaluar_paso_inicial(glucemia_actual: int, glucemia_previa: int) -> ResultadoFlujo:
    if glucemia_actual < 70:
        return ResultadoFlujo(
            estado="hipoglucemia",
            titulo="Hipoglucemia",
            mensaje="La glicemia actual es menor a 70 mg/dL.",
        )

    if glucemia_actual <= 119:
        return ResultadoFlujo(
            estado="suspender",
            titulo="Suspender infusión",
            mensaje="La glicemia actual está entre 70 y 119 mg/dL. Corresponde suspender infusión.",
        )

    if glucemia_actual >= 180 and glucemia_previa >= 180:
        return ResultadoFlujo(
            estado="hiperglucemia_sostenida",
            titulo="Hiperglucemia sostenida",
            mensaje="La glicemia actual y la previa son mayores o iguales a 180 mg/dL.",
            requiere_paso="infusion_activa",
        )

    return ResultadoFlujo(
        estado="sin_hiperglucemia_sostenida",
        titulo="Sin hiperglucemia sostenida",
        mensaje="No cumple criterio de hiperglucemia sostenida. Continuar control.",
    )


def evaluar_infusion_activa(infusion_activa: bool) -> ResultadoFlujo:
    if not infusion_activa:
        return ResultadoFlujo(
            estado="iniciar_manejo",
            titulo="Iniciar manejo",
            mensaje="No hay infusión activa. Iniciar bolo inicial, comenzar Algoritmo 1 y realizar monitoreo.",
        )

    return ResultadoFlujo(
        estado="continuar_con_algoritmo",
        titulo="Infusión activa",
        mensaje="La infusión está activa. Seleccionar algoritmo actual.",
        requiere_paso="algoritmo_actual",
    )


def evaluar_algoritmo_1(
    glucemia_actual: int,
    glucemia_previa: int,
    ultimo_escalon: bool,
    subio_ultimas_2: bool,
    mismo_escalon_3_controles: bool,
) -> ResultadoFlujo:
    if not (glucemia_actual > 200 and glucemia_previa > 200):
        return ResultadoFlujo(
            estado="continuar_algoritmo_1",
            titulo="Continuar Algoritmo 1",
            mensaje="No cumple criterio base de HGP. Ajustar tasa y recontrol.",
        )

    hgp = any([ultimo_escalon, subio_ultimas_2, mismo_escalon_3_controles])

    if hgp:
        return ResultadoFlujo(
            estado="pasar_algoritmo_2",
            titulo="HGP",
            mensaje="Cumple criterios de HGP. Corresponde pasar a Algoritmo 2.",
        )

    return ResultadoFlujo(
        estado="continuar_algoritmo_1",
        titulo="Continuar Algoritmo 1",
        mensaje="No cumple criterios de HGP. Ajustar tasa y recontrol.",
    )


def evaluar_algoritmo_2(
    glucemia_actual: int,
    glucemia_previa: int,
    ultimo_escalon: bool,
) -> ResultadoFlujo:
    if not (glucemia_actual > 360 and glucemia_previa > 360):
        return ResultadoFlujo(
            estado="continuar_algoritmo_2",
            titulo="Continuar Algoritmo 2",
            mensaje="No cumple criterio de hiperglucemia refractaria. Recontrol.",
        )

    if ultimo_escalon:
        return ResultadoFlujo(
            estado="avisar_medico",
            titulo="Hiperglucemia refractaria",
            mensaje="Cumple criterio y está en último escalón. Avisar médico.",
        )

    return ResultadoFlujo(
        estado="continuar_algoritmo_2",
        titulo="Continuar Algoritmo 2",
        mensaje="Cumple glicemias > 360 pero no está en último escalón. Continuar Algoritmo 2 y recontrol.",
    )


def in_range(g, lo, hi):
    if lo is None and hi is None:
        return True
    if lo is None:
        return g <= hi
    if hi is None:
        return g >= lo
    return lo <= g <= hi


def _rate_from_table(g, table):
    for lo, hi, rate in table:
        if in_range(g, lo, hi):
            return rate
    return None


def rate_from_table(g, table):
    return _rate_from_table(g, table)


def es_hipoglucemia(glucemia: int) -> bool:
    return glucemia < 70


def debe_suspender(glucemia: int) -> bool:
    return glucemia < 120


def esta_en_objetivo(glucemia: int, obj_min: int = 140, obj_max: int = 200) -> bool:
    return obj_min <= glucemia <= obj_max


def es_hiperglucemia(glucemia: int, obj_max: int = 200) -> bool:
    return glucemia > obj_max
    return _rate_from_table(g, table)