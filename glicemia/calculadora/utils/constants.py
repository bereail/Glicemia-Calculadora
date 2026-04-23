from decimal import Decimal

# =========================================================
# UMBRALES GENERALES
# =========================================================

UMBRAL_HIPO = Decimal("70")
LIMITE_ZONA_INTERMEDIA = Decimal("120")   # se conserva por compatibilidad

# Objetivo en paciente con infusión activa
OBJETIVO_MIN_INFUSION = Decimal("140")
OBJETIVO_MAX_INFUSION = Decimal("200")

# Hiperglucemia sin infusión / umbral de insulinización
UMBRAL_HIPER = Decimal("180")

# Cortes de alerta / severidad
UMBRAL_ALERTA_ALTA = Decimal("200")
UMBRAL_MUY_ALTA = Decimal("300")
UMBRAL_REFRACTARIA = Decimal("360")
UMBRAL_SEVERA = Decimal("400")

# =========================================================
# REGLAS DEL PROTOCOLO
# =========================================================

# Inicio de insulinización: 2 controles consecutivos >180 mg/dL
CONTROLES_CONSECUTIVOS_INICIO_INSULINA = 2

# Reinstaurar goteo post-hipo cuando glucemia >180 y siempre en Algoritmo 1
UMBRAL_REINICIO_POST_HIPO = Decimal("180")
ALGORITMO_REINICIO_POST_HIPO = 1

# Hiperglucemia persistente (HGP)
CONTROLES_HGP_ULTIMO_ESCALON = 2
CONTROLES_HGP_MISMO_ESCALON = 3

# Hiperglucemia refractaria (HGR)
CONTROLES_HGR = 2

# =========================================================
# TABLAS EXACTAS DE ALGORITMOS
# Según protocolo
# =========================================================

TABLA_ALGORITMO_1 = [
    {"min": None,            "max": Decimal("119.999"), "tasa": None,           "texto": "Suspender"},
    {"min": Decimal("120"),  "max": Decimal("149"),     "tasa": Decimal("0.5"), "texto": "0,5 UI/h"},
    {"min": Decimal("150"),  "max": Decimal("179"),     "tasa": Decimal("1"),   "texto": "1 UI/h"},
    {"min": Decimal("180"),  "max": Decimal("209"),     "tasa": Decimal("1.5"), "texto": "1,5 UI/h"},
    {"min": Decimal("210"),  "max": Decimal("239"),     "tasa": Decimal("2"),   "texto": "2 UI/h"},
    {"min": Decimal("240"),  "max": Decimal("269"),     "tasa": Decimal("2.5"), "texto": "2,5 UI/h"},
    {"min": Decimal("270"),  "max": Decimal("299"),     "tasa": Decimal("3"),   "texto": "3 UI/h"},
    {"min": Decimal("300"),  "max": Decimal("329"),     "tasa": Decimal("3.5"), "texto": "3,5 UI/h"},
    {"min": Decimal("330"),  "max": Decimal("359"),     "tasa": Decimal("4"),   "texto": "4 UI/h"},
    {"min": Decimal("360"),  "max": None,               "tasa": Decimal("5"),   "texto": "5 UI/h"},
]

TABLA_ALGORITMO_2 = [
    {"min": None,            "max": Decimal("119.999"), "tasa": None,           "texto": "Suspender"},
    {"min": Decimal("120"),  "max": Decimal("149"),     "tasa": Decimal("1"),   "texto": "1 UI/h"},
    {"min": Decimal("150"),  "max": Decimal("179"),     "tasa": Decimal("1.5"), "texto": "1,5 UI/h"},
    {"min": Decimal("180"),  "max": Decimal("209"),     "tasa": Decimal("2.5"), "texto": "2,5 UI/h"},
    {"min": Decimal("210"),  "max": Decimal("239"),     "tasa": Decimal("3"),   "texto": "3 UI/h"},
    {"min": Decimal("240"),  "max": Decimal("269"),     "tasa": Decimal("3.5"), "texto": "3,5 UI/h"},
    {"min": Decimal("270"),  "max": Decimal("299"),     "tasa": Decimal("4"),   "texto": "4 UI/h"},
    {"min": Decimal("300"),  "max": Decimal("329"),     "tasa": Decimal("5"),   "texto": "5 UI/h"},
    {"min": Decimal("330"),  "max": Decimal("359"),     "tasa": Decimal("6"),   "texto": "6 UI/h"},
    {"min": Decimal("360"),  "max": None,               "tasa": Decimal("8"),   "texto": "8 UI/h"},
]