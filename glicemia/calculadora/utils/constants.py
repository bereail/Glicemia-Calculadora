from decimal import Decimal

UMBRAL_HIPO = Decimal("70")
LIMITE_ZONA_INTERMEDIA = Decimal("120")

# Objetivo en paciente con infusión activa
OBJETIVO_MIN_INFUSION = Decimal("140")
OBJETIVO_MAX_INFUSION = Decimal("200")

# Hiperglucemia sin infusión
UMBRAL_HIPER = Decimal("180")

# Cortes de alerta / severidad
UMBRAL_ALERTA_ALTA = Decimal("200")
UMBRAL_MUY_ALTA = Decimal("300")
UMBRAL_SEVERA = Decimal("400")