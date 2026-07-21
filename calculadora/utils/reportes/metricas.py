from datetime import timedelta

from django.utils import timezone

# Diagnósticos del Control Glicémico en la UCI-HEEP: cada uno corresponde
# exactamente al valor que el motor de reglas guarda en MedicionGlucemia.estado.
DIAGNOSTICOS_PROTOCOLO = [
    ("Hipoglucemia", "Hipoglucemia"),
    ("Hiperglucemia Aislada", "Hiperglucemia aislada"),
    ("Hiperglucemia Sostenida", "Hiperglucemia sostenida"),
    ("Hiperglucemia Persistente", "Hiperglucemia persistente"),
    ("Hiperglucemia Refractaria", "Hiperglucemia refractaria"),
]


def calcular_metricas_dashboard(mediciones_qs):
    """Calcula todas las métricas del panel a partir de un queryset ya filtrado."""
    total = mediciones_qs.count()
    hipoglucemias = mediciones_qs.filter(clase="hipoglucemia").count()
    post_hipoglucemias = mediciones_qs.filter(clase="post_hipoglucemia").count()
    en_objetivo = mediciones_qs.filter(clase="en_rango").count()
    hiperglucemias = mediciones_qs.filter(clase="hiperglucemia").count()

    uso_medicos = mediciones_qs.filter(usuario__groups__name="Medicos").count()
    uso_enfermeria = mediciones_qs.filter(usuario__groups__name="Enfermeria").count()
    uso_sin_grupo = mediciones_qs.filter(usuario__groups__isnull=True).count()

    turnos = {"manana": 0, "tarde": 0, "noche": 0, "madrugada": 0}
    semanas = {}
    for fecha, clase_m in mediciones_qs.values_list("fecha_hora", "clase"):
        fecha_local = timezone.localtime(fecha)
        h = fecha_local.hour
        if 6 <= h < 12:
            turnos["manana"] += 1
        elif 12 <= h < 18:
            turnos["tarde"] += 1
        elif 18 <= h < 24:
            turnos["noche"] += 1
        else:
            turnos["madrugada"] += 1

        lunes = (fecha_local - timedelta(days=fecha_local.weekday())).date()
        semana = semanas.setdefault(lunes, {"total": 0, "objetivo": 0, "hipo": 0, "hiper": 0})
        semana["total"] += 1
        if clase_m == "en_rango":
            semana["objetivo"] += 1
        elif clase_m == "hipoglucemia":
            semana["hipo"] += 1
        elif clase_m == "hiperglucemia":
            semana["hiper"] += 1

    lt_labels, lt_objetivo, lt_hipo, lt_hiper = [], [], [], []
    for lunes in sorted(semanas):
        d = semanas[lunes]
        t = d["total"] or 1
        lt_labels.append(lunes.strftime("%d/%m"))
        lt_objetivo.append(round(d["objetivo"] / t * 100, 1))
        lt_hipo.append(round(d["hipo"] / t * 100, 1))
        lt_hiper.append(round(d["hiper"] / t * 100, 1))

    rango_labels = ["< 70", "70–200", "200–300", "301–400", "401–500", "> 500"]
    rango_datos = [
        mediciones_qs.filter(glicemia_actual__lt=70).count(),
        mediciones_qs.filter(glicemia_actual__gte=70, glicemia_actual__lte=200).count(),
        mediciones_qs.filter(glicemia_actual__gt=200, glicemia_actual__lte=300).count(),
        mediciones_qs.filter(glicemia_actual__gt=300, glicemia_actual__lte=400).count(),
        mediciones_qs.filter(glicemia_actual__gt=400, glicemia_actual__lte=500).count(),
        mediciones_qs.filter(glicemia_actual__gt=500).count(),
    ]

    dg_labels = [etiqueta for _, etiqueta in DIAGNOSTICOS_PROTOCOLO]
    dg_valores = [
        mediciones_qs.filter(estado=estado_exacto).count()
        for estado_exacto, _ in DIAGNOSTICOS_PROTOCOLO
    ]
    dg_total = sum(dg_valores)
    dg_porcentajes = [
        round(v / dg_total * 100, 1) if dg_total else 0
        for v in dg_valores
    ]

    return {
        "total": total,
        "hipoglucemias": hipoglucemias,
        "post_hipoglucemias": post_hipoglucemias,
        "en_objetivo": en_objetivo,
        "hiperglucemias": hiperglucemias,
        "pct_hipo": round(hipoglucemias / (total or 1) * 100, 1),
        "pct_ok": round(en_objetivo / (total or 1) * 100, 1),
        "pct_hiper": round(hiperglucemias / (total or 1) * 100, 1),
        "uso_medicos": uso_medicos,
        "uso_enfermeria": uso_enfermeria,
        "uso_sin_grupo": uso_sin_grupo,
        "turno_manana": turnos["manana"],
        "turno_tarde": turnos["tarde"],
        "turno_noche": turnos["noche"],
        "turno_madrugada": turnos["madrugada"],
        "lt_labels": lt_labels,
        "lt_objetivo": lt_objetivo,
        "lt_hipo": lt_hipo,
        "lt_hiper": lt_hiper,
        "rango_labels": rango_labels,
        "rango_datos": rango_datos,
        "dg_labels": dg_labels,
        "dg_valores": dg_valores,
        "dg_porcentajes": dg_porcentajes,
        "dg_total": dg_total,
    }


def calcular_detalle_categoria(mediciones):
    """Gráficos de apoyo para el detalle de una categoría (card): dónde (turno)
    y en qué contexto (con o sin infusión) conviene ajustar."""
    en_orden = sorted(mediciones, key=lambda m: m.fecha_hora)

    serie_labels, serie_valores = [], []
    turnos = {"manana": 0, "tarde": 0, "noche": 0, "madrugada": 0}
    infusion_si = infusion_no = 0

    for m in en_orden:
        fecha_local = timezone.localtime(m.fecha_hora)
        serie_labels.append(fecha_local.strftime("%d/%m %H:%M"))
        serie_valores.append(m.glicemia_actual)

        h = fecha_local.hour
        if 6 <= h < 12:
            turnos["manana"] += 1
        elif 12 <= h < 18:
            turnos["tarde"] += 1
        elif 18 <= h < 24:
            turnos["noche"] += 1
        else:
            turnos["madrugada"] += 1

        if m.infusion_activa:
            infusion_si += 1
        else:
            infusion_no += 1

    return {
        "detalle_serie_labels": serie_labels,
        "detalle_serie_valores": serie_valores,
        "detalle_turno_labels": ["Mañana (06–12)", "Tarde (12–18)", "Noche (18–24)", "Madrugada (00–06)"],
        "detalle_turno_valores": [turnos["manana"], turnos["tarde"], turnos["noche"], turnos["madrugada"]],
        "detalle_infusion_si": infusion_si,
        "detalle_infusion_no": infusion_no,
    }
