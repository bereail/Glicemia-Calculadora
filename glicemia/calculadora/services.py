from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


# =========================================================
# CONSTANTES
# =========================================================

UMBRAL_HIPO = Decimal("70")
LIMITE_ZONA_INTERMEDIA = Decimal("120")

OBJETIVO_MIN_INFUSION = Decimal("140")
OBJETIVO_MAX_INFUSION = Decimal("180")

UMBRAL_HIPER = Decimal("180")
UMBRAL_ALERTA_ALTA = Decimal("200")
UMBRAL_MUY_ALTA = Decimal("300")
UMBRAL_SEVERA = Decimal("400")


# =========================================================
# HELPERS
# =========================================================

def _a_decimal(valor, permitir_none=False):
    """
    Convierte un valor a Decimal de forma segura.
    """
    if valor in (None, ""):
        if permitir_none:
            return None
        raise ValueError("Valor requerido")

    try:
        return Decimal(str(valor).strip())
    except (InvalidOperation, TypeError, ValueError):
        if permitir_none:
            return None
        raise ValueError(f"Valor inválido: {valor}")


def _a_bool(valor):
    """
    Convierte distintas representaciones a booleano.
    """
    if isinstance(valor, bool):
        return valor

    if valor is None:
        return False

    return str(valor).strip().lower() in ("true", "1", "si", "sí", "s", "yes")


def _resultado_base():
    """
    Estructura estándar de respuesta.
    """
    return {
        "estado": None,
        "subestado": None,
        "mensaje": None,
        "conducta": None,

        "tendencia": None,
        "flecha_tendencia": None,
        "delta": None,

        "requiere_recontrol": False,
        "proximo_control": None,

        "suspender_insulina": False,
        "administrar_dextrosa": False,
        "evaluar_goteo_mantenimiento": False,
        "reiniciar_insulina": False,

        "bolo_inicial": None,
        "tasa_inicial": None,
        "tasa_algoritmo": None,

        "mostrar_resultado": False,
    }


# =========================================================
# TENDENCIA
# =========================================================

def calcular_tendencia(actual, previa):
    """
    Evalúa la tendencia comparando glicemia actual con previa.

    Categorías sugeridas:
    - delta >= +40  -> Ascenso marcado ↑
    - delta +10/+39 -> Ascenso leve ↗
    - delta -9/+9   -> Estable →
    - delta -10/-39 -> Descenso leve ↘
    - delta <= -40  -> Descenso marcado ↓
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)

    if previa is None:
        return None

    delta = actual - previa

    if delta >= Decimal("40"):
        return {
            "direccion": "sube",
            "categoria": "ascenso_marcado",
            "descripcion": "Ascenso marcado",
            "flecha": "↑",
            "delta": str(delta),
        }

    if delta >= Decimal("10"):
        return {
            "direccion": "sube",
            "categoria": "ascenso_leve",
            "descripcion": "Ascenso leve",
            "flecha": "↗",
            "delta": str(delta),
        }

    if delta <= Decimal("-40"):
        return {
            "direccion": "baja",
            "categoria": "descenso_marcado",
            "descripcion": "Descenso marcado",
            "flecha": "↓",
            "delta": str(delta),
        }

    if delta <= Decimal("-10"):
        return {
            "direccion": "baja",
            "categoria": "descenso_leve",
            "descripcion": "Descenso leve",
            "flecha": "↘",
            "delta": str(delta),
        }

    return {
        "direccion": "igual",
        "categoria": "estable",
        "descripcion": "Estable",
        "flecha": "→",
        "delta": str(delta),
    }


def _aplicar_tendencia(resultado, actual, previa):
    """
    Agrega datos de tendencia al resultado si hay previa.
    """
    tendencia = calcular_tendencia(actual, previa)
    if tendencia is None:
        return resultado

    resultado["tendencia"] = tendencia["descripcion"]
    resultado["flecha_tendencia"] = tendencia["flecha"]
    resultado["delta"] = tendencia["delta"]
    return resultado


# =========================================================
# DOSIS / ALGORITMOS / MONITOREO
# =========================================================

def calcular_bolo_y_tasa_inicial(glucemia):
    """
    Protocolo inicial:
    glucemia / 100 = bolo inicial y tasa inicial sugerida.
    Ej: 400 -> 4.0 UI
    """
    glucemia = _a_decimal(glucemia)
    return (glucemia / Decimal("100")).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP
    )


def obtener_tasa_algoritmo_inicio(glucemia):
    """
    Algoritmo de tasa sugerida para inicio / reinicio.
    """
    glucemia = _a_decimal(glucemia)

    if glucemia < Decimal("120"):
        return "Suspender"
    if glucemia <= Decimal("149"):
        return "0,5 UI/h"
    if glucemia <= Decimal("179"):
        return "1 UI/h"
    if glucemia <= Decimal("209"):
        return "1,5 UI/h"
    if glucemia <= Decimal("239"):
        return "2 UI/h"
    if glucemia <= Decimal("269"):
        return "2,5 UI/h"
    if glucemia <= Decimal("299"):
        return "3 UI/h"
    if glucemia <= Decimal("329"):
        return "3,5 UI/h"
    if glucemia <= Decimal("359"):
        return "4 UI/h"
    return "5 UI/h"


def calcular_proximo_control(glucemia, horas_desde_inicio=None, estable=False):
    """
    Sugerencia general de próximo control.
    """
    glucemia = _a_decimal(glucemia)
    estable = _a_bool(estable)

    if horas_desde_inicio is not None:
        horas_desde_inicio = _a_decimal(horas_desde_inicio, permitir_none=True)

    if glucemia > Decimal("400"):
        return "Próximo control en 1 hora"

    if Decimal("300") <= glucemia <= Decimal("400"):
        return "Próximo control en 2 horas"

    if Decimal("200") <= glucemia < Decimal("300"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return "Próximo control en 6 horas"
        return "Próximo control en 4 horas"

    if Decimal("140") <= glucemia < Decimal("200"):
        if horas_desde_inicio is not None and horas_desde_inicio > Decimal("24") and estable:
            return "Próximo control en 6 horas"
        return "Próximo control en 4 horas"

    if Decimal("70") <= glucemia < Decimal("140"):
        return "Próximo control según conducta clínica"

    return "Control inmediato / tratar hipoglucemia según protocolo"


# =========================================================
# 1) HIPOGLUCEMIA
# =========================================================

def evaluar_hipoglucemia(actual, previa=None, infusion_activa=False):
    """
    Evalúa:
    - hipoglucemia actual (<70)
    - recontrol post-hipo (actual >=70 con previa <70)
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    resultado = _resultado_base()

    # 1) Hipoglucemia actual
    if actual < UMBRAL_HIPO:
        resultado["estado"] = "hipoglucemia"
        resultado["subestado"] = "Glucemia actual < 70 mg/dL"
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

    # 2) Recontrol post-hipoglucemia
    if previa is not None and previa < UMBRAL_HIPO and actual >= UMBRAL_HIPO:
        resultado["mostrar_resultado"] = True
        resultado["requiere_recontrol"] = True

        if UMBRAL_HIPO <= actual <= LIMITE_ZONA_INTERMEDIA:
            resultado["estado"] = "recontrol_post_hipo"
            resultado["subestado"] = "Glucemia entre 70 y 120 mg/dL"
            resultado["mensaje"] = "Recuperación inicial post-hipoglucemia."
            resultado["conducta"] = "Mantener insulina suspendida y controlar glucemia cada 1 hora."
            resultado["suspender_insulina"] = infusion_activa
            resultado["proximo_control"] = "Controlar glucemia cada 1 hora"
            return resultado

        if LIMITE_ZONA_INTERMEDIA < actual <= UMBRAL_HIPER:
            resultado["estado"] = "recontrol_post_hipo"
            resultado["subestado"] = "Glucemia entre 121 y 180 mg/dL"
            resultado["mensaje"] = "Recuperación adecuada post-hipoglucemia."
            resultado["conducta"] = "Continuar monitoreo cada 1 hora. No reiniciar insulina de inmediato."
            resultado["suspender_insulina"] = infusion_activa
            resultado["proximo_control"] = "Continuar monitoreo cada 1 hora"
            return resultado

        if actual > UMBRAL_HIPER:
            resultado["estado"] = "rebote_post_hipoglucemia"
            resultado["subestado"] = "Glucemia > 180 mg/dL en recontrol post-hipoglucemia"
            resultado["mensaje"] = "Posible rebote transitorio post-corrección."
            resultado["conducta"] = "Confirmar nueva medición y reevaluar reinicio o ajuste de insulina."
            resultado["reiniciar_insulina"] = infusion_activa
            resultado["proximo_control"] = "Confirmar nueva medición en 1 hora"
            return resultado

    return None


# =========================================================
# 2) RANGO 70-180
# =========================================================

def evaluar_rango_70_180(actual, previa=None, infusion_activa=False):
    """
    Evalúa valores entre 70 y 180 fuera del contexto de hipoglucemia.
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)

    if not (UMBRAL_HIPO <= actual <= UMBRAL_HIPER):
        return None

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True
    resultado = _aplicar_tendencia(resultado, actual, previa)

    # -----------------------------------------------------
    # SIN INFUSIÓN ACTIVA
    # -----------------------------------------------------
    if not infusion_activa:
        if previa is None:
            if Decimal("70") <= actual <= Decimal("140"):
                resultado["estado"] = "en_rango"
                resultado["subestado"] = "Glicemia entre 70 y 140 mg/dL"
                resultado["mensaje"] = "Glicemia dentro de rango normal."
                resultado["conducta"] = "Continuar monitoreo."
                resultado["proximo_control"] = "Según monitoreo habitual"
                return resultado

            if Decimal("141") <= actual <= Decimal("180"):
                resultado["estado"] = "limite_alto"
                resultado["subestado"] = "Glicemia entre 141 y 180 mg/dL"
                resultado["mensaje"] = "Glicemia en límite alto."
                resultado["conducta"] = "Solicitar nueva medición para evaluar tendencia."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Nueva medición para valorar tendencia"
                return resultado

        # Con previa
        if previa is not None:
            if actual > previa:
                resultado["estado"] = "ascenso_en_rango"
                resultado["subestado"] = "Glicemia 70-180 en ascenso"
                resultado["mensaje"] = "Valor en rango, pero con ascenso glucémico."
                resultado["conducta"] = "Control evolutivo para evaluar si continúa en ascenso."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Recontrol según evolución clínica"
                return resultado

            if actual < previa:
                resultado["estado"] = "descenso_en_rango"
                resultado["subestado"] = "Glicemia 70-180 en descenso"
                resultado["mensaje"] = "Valor en rango, pero con descenso glucémico."
                resultado["conducta"] = "Vigilar evolución para evitar hipoglucemia si continúa bajando."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Recontrol según evolución clínica"
                return resultado

            resultado["estado"] = "estable_en_rango"
            resultado["subestado"] = "Glicemia estable entre 70 y 180 mg/dL"
            resultado["mensaje"] = "Glicemia estable dentro del rango."
            resultado["conducta"] = "Continuar monitoreo."
            resultado["proximo_control"] = "Según monitoreo habitual"
            return resultado

    # -----------------------------------------------------
    # CON INFUSIÓN ACTIVA
    # -----------------------------------------------------
    if infusion_activa:
        if previa is None:
            resultado["estado"] = "datos_insuficientes"
            resultado["subestado"] = "Falta glicemia previa"
            resultado["mensaje"] = "Con infusión activa se requiere glicemia previa para valorar tendencia."
            resultado["conducta"] = "Ingresar glicemia previa."
            return resultado

        if actual < OBJETIVO_MIN_INFUSION:
            resultado["estado"] = "debajo_objetivo_infusion"
            resultado["subestado"] = "Actual < 140 con infusión activa"
            resultado["mensaje"] = "Por debajo del objetivo para paciente con infusión."
            resultado["conducta"] = "Evaluar descenso y considerar ajuste de insulina por riesgo de hipoglucemia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Control frecuente según protocolo"
            return resultado

        if OBJETIVO_MIN_INFUSION <= actual <= OBJETIVO_MAX_INFUSION:
            if actual < previa:
                resultado["estado"] = "objetivo_con_descenso"
                resultado["subestado"] = "Dentro del objetivo, pero en descenso"
                resultado["mensaje"] = "Dentro del rango objetivo para paciente insulinizado, con tendencia descendente."
                resultado["conducta"] = "Vigilar riesgo de hipoglucemia y reevaluar infusión."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Control según protocolo"
                return resultado

            if actual > previa:
                resultado["estado"] = "objetivo_con_ascenso"
                resultado["subestado"] = "Dentro del objetivo, pero en ascenso"
                resultado["mensaje"] = "Dentro del rango objetivo, aunque con tendencia ascendente."
                resultado["conducta"] = "Mantener monitoreo y evaluar tendencia."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Control según protocolo"
                return resultado

            resultado["estado"] = "objetivo_infusion"
            resultado["subestado"] = "Dentro del objetivo con infusión activa"
            resultado["mensaje"] = "Dentro del rango objetivo para paciente insulinizado."
            resultado["conducta"] = "Mantener conducta actual y continuar monitoreo."
            resultado["proximo_control"] = "Según protocolo"
            return resultado

    return None


# =========================================================
# 3) HIPERGLUCEMIA >180
# =========================================================

def evaluar_hiperglucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
):
    """
    Evalúa hiperglucemia >180.
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)

    if actual <= UMBRAL_HIPER:
        return None

    resultado = _resultado_base()
    resultado["mostrar_resultado"] = True
    resultado = _aplicar_tendencia(resultado, actual, previa)

    # -----------------------------------------------------
    # SIN INFUSIÓN ACTIVA
    # -----------------------------------------------------
    if not infusion_activa:
        if previa is None:
            resultado["estado"] = "hiperglucemia_aislada"
            resultado["subestado"] = "Actual > 180 sin previa"
            resultado["mensaje"] = "Hiperglucemia aislada."
            resultado["conducta"] = "Solicitar nueva medición para confirmar persistencia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = "Nueva medición para confirmar persistencia"
            return resultado

        if previa >= UMBRAL_HIPER:
            dosis = calcular_bolo_y_tasa_inicial(actual)

            resultado["estado"] = "hiperglucemia_sostenida"
            resultado["subestado"] = "Dos controles consecutivos > 180 mg/dL"
            resultado["mensaje"] = "Hiperglucemia sostenida."
            resultado["conducta"] = "Evaluar protocolo de insulinización endovenosa."
            resultado["bolo_inicial"] = f"{dosis} UI"
            resultado["tasa_inicial"] = f"{dosis} UI/h"
            resultado["proximo_control"] = calcular_proximo_control(actual)
            return resultado

        resultado["estado"] = "hiperglucemia_en_ascenso"
        resultado["subestado"] = "Actual > 180 con previa menor a 180"
        resultado["mensaje"] = "Hiperglucemia detectada en ascenso."
        resultado["conducta"] = "Requiere nueva medición para evaluar persistencia."
        resultado["requiere_recontrol"] = True
        resultado["proximo_control"] = "Nueva medición para confirmar persistencia"
        return resultado

    # -----------------------------------------------------
    # CON INFUSIÓN ACTIVA
    # -----------------------------------------------------
    if infusion_activa:
        resultado["tasa_algoritmo"] = obtener_tasa_algoritmo_inicio(actual)

        if actual <= UMBRAL_ALERTA_ALTA:
            if previa is not None and previa < OBJETIVO_MIN_INFUSION:
                resultado["estado"] = "ascenso_fuera_objetivo"
                resultado["subestado"] = "Actual 181-200 con previa < 140"
                resultado["mensaje"] = "Ascenso glucémico fuera del objetivo."
                resultado["conducta"] = (
                    "Requiere control más frecuente. Valorar ajuste si persiste o continúa en ascenso."
                )
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = calcular_proximo_control(actual)
                return resultado

            resultado["estado"] = "fuera_objetivo_alto"
            resultado["subestado"] = "Actual 181-200 con infusión activa"
            resultado["mensaje"] = "Fuera del objetivo alto para paciente con infusión."
            resultado["conducta"] = "Monitorizar tendencia y reevaluar ajuste."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = calcular_proximo_control(actual)
            return resultado

        # Actual > 200
        if actual > UMBRAL_ALERTA_ALTA:
            if previa is not None and previa > UMBRAL_HIPER:
                resultado["estado"] = "hiperglucemia_persistente"
                resultado["subestado"] = "Al menos 2 controles consecutivos > 180 mg/dL con infusión activa"
                resultado["mensaje"] = "Hiperglucemia persistente."
                resultado["conducta"] = "Evaluar tercera medición para confirmar persistencia o refractariedad."
                resultado["requiere_recontrol"] = True
                resultado["proximo_control"] = "Obtener tercera medición"
                
                # Si ya existe tercera medición
                if tercera_medicion is not None:
                    if tercera_medicion > UMBRAL_ALERTA_ALTA:
                        if hubo_ajuste_insulina:
                            resultado["estado"] = "hiperglucemia_refractaria"
                            resultado["subestado"] = "Persiste > 200 pese a ajuste de insulina"
                            resultado["mensaje"] = "Hiperglucemia refractaria."
                            resultado["conducta"] = "Persistencia pese a ajuste. Reevaluar estrategia terapéutica."
                            resultado["proximo_control"] = "Control estrecho según protocolo"
                            return resultado

                        resultado["estado"] = "hiperglucemia_persistente_confirmada"
                        resultado["subestado"] = "Tercera medición > 200 mg/dL"
                        resultado["mensaje"] = "Persistencia confirmada."
                        resultado["conducta"] = "Realizar ajuste de insulina y continuar control estrecho."
                        resultado["proximo_control"] = "Control estrecho post-ajuste"
                        return resultado

                    resultado["estado"] = "hiperglucemia_en_mejoria"
                    resultado["subestado"] = "Tercera medición <= 200 mg/dL"
                    resultado["mensaje"] = "Persistencia no confirmada o en mejoría."
                    resultado["conducta"] = "Continuar monitoreo y reevaluar evolución."
                    resultado["proximo_control"] = calcular_proximo_control(tercera_medicion)
                    return resultado

                return resultado

            # actual > 200 pero no cumple persistente todavía
            resultado["estado"] = "hiperglucemia_marcada"
            resultado["subestado"] = "Actual > 200 con infusión activa"
            resultado["mensaje"] = "Hiperglucemia marcada."
            resultado["conducta"] = "Requiere recontrol y evaluación de tendencia."
            resultado["requiere_recontrol"] = True
            resultado["proximo_control"] = calcular_proximo_control(actual)
            return resultado

    return None


# =========================================================
# ORQUESTADOR PRINCIPAL
# =========================================================

def resolver_glucemia(
    actual,
    previa=None,
    infusion_activa=False,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    horas_desde_inicio=None,
    estable=False,
):
    """
    Orquestador principal.
    Prioridad:
    1) Hipoglucemia
    2) Rango 70-180
    3) Hiperglucemia
    """
    actual = _a_decimal(actual)
    previa = _a_decimal(previa, permitir_none=True)
    infusion_activa = _a_bool(infusion_activa)
    hubo_ajuste_insulina = _a_bool(hubo_ajuste_insulina)
    estable = _a_bool(estable)
    tercera_medicion = _a_decimal(tercera_medicion, permitir_none=True)

    # 1) HIPOGLUCEMIA
    resultado = evaluar_hipoglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado is not None:
        return resultado

    # 2) RANGO 70-180
    resultado = evaluar_rango_70_180(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
    )
    if resultado is not None:
        return resultado

    # 3) HIPERGLUCEMIA
    resultado = evaluar_hiperglucemia(
        actual=actual,
        previa=previa,
        infusion_activa=infusion_activa,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
    )
    if resultado is not None:
        return resultado

    # Fallback
    resultado = _resultado_base()
    resultado["estado"] = "sin_clasificacion"
    resultado["subestado"] = "No se pudo clasificar el caso"
    resultado["mensaje"] = "Revisar datos ingresados."
    resultado["conducta"] = "Validar entradas y lógica del flujo."
    resultado["mostrar_resultado"] = True
    return resultado


# =========================================================
# WRAPPER DE COMPATIBILIDAD
# =========================================================

def resolver_flujo_glucemia(
    actual,
    insulinizado=False,
    previa=None,
    hubo_ajuste_insulina=False,
    tercera_medicion=None,
    horas_desde_inicio=None,
    estable=False,
):
    """
    Wrapper para no romper tu código actual si todavía usás 'insulinizado'.

    OJO:
    por ahora lo mapea a infusion_activa.
    Si después querés separar ambos conceptos, conviene refactorizarlo.
    """
    return resolver_glucemia(
        actual=actual,
        previa=previa,
        infusion_activa=insulinizado,
        hubo_ajuste_insulina=hubo_ajuste_insulina,
        tercera_medicion=tercera_medicion,
        horas_desde_inicio=horas_desde_inicio,
        estable=estable,
    )