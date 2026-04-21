from decimal import Decimal

# Hipoglucemia
UMBRAL_HIPO = Decimal("70")

# Suspensión de infusión
LIMITE_SUSPENDER_INFUSION = Decimal("120")

# Objetivo con infusión activa
OBJETIVO_MIN_INFUSION = Decimal("140")
OBJETIVO_MAX_INFUSION = Decimal("200")

# Hiperglucemia sin infusión / inicio de insulinización
UMBRAL_HIPER = Decimal("180")

# Fuera de objetivo alto en insulinizado
UMBRAL_FUERA_OBJETIVO_ALTO = Decimal("200")

# Umbrales de severidad / control
UMBRAL_CONTROL_2H = Decimal("300")
UMBRAL_REFRACTARIA = Decimal("360")
UMBRAL_CONTROL_1H = Decimal("400")