from decimal import Decimal


OBJ_MIN = 140
OBJ_MAX = 200

ALG1 = [
    (None, 119, None),
    (120, 149, Decimal("0.5")),
    (150, 179, Decimal("1")),
    (180, 209, Decimal("1.5")),
    (210, 239, Decimal("2")),
    (240, 269, Decimal("2.5")),
    (270, 299, Decimal("3")),
    (300, 329, Decimal("3.5")),
    (330, None, Decimal("4")),
]


def rate_from_table(glucemia, tabla):
    for minimo, maximo, valor in tabla:
        minimo_ok = minimo is None or glucemia >= minimo
        maximo_ok = maximo is None or glucemia <= maximo

        if minimo_ok and maximo_ok:
            return valor
    return None


def es_hipoglucemia(glucemia):
    return glucemia < 70


def debe_suspender(glucemia):
    return glucemia < 120