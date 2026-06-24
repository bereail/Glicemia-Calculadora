from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.db.models.functions import ExtractHour, TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import VisitaWeb


def _es_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.email == "berenicesolohaga@gmail.com"
    )


@login_required
def panel_admin(request):
    if not _es_admin(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Acceso denegado.")

    ahora = timezone.now()
    hoy = ahora.date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # ── Métricas generales ──────────────────────────────────────────────────
    visitas_hoy = VisitaWeb.objects.filter(timestamp__date=hoy).count()
    visitas_semana = VisitaWeb.objects.filter(timestamp__date__gte=inicio_semana).count()
    visitas_mes = VisitaWeb.objects.filter(timestamp__date__gte=inicio_mes).count()

    ips_unicas_hoy = (
        VisitaWeb.objects.filter(timestamp__date=hoy)
        .values("ip")
        .distinct()
        .count()
    )

    hace_cinco = ahora - timedelta(minutes=5)
    activos_ahora = (
        VisitaWeb.objects.filter(timestamp__gte=hace_cinco)
        .values("ip")
        .distinct()
        .count()
    )

    avg_dur = (
        VisitaWeb.objects.filter(
            timestamp__date=hoy,
            duracion_segundos__isnull=False,
            duracion_segundos__gt=0,
        ).aggregate(avg=Avg("duracion_segundos"))["avg"]
    )
    duracion_promedio_hoy = round(avg_dur) if avg_dur else None

    total_usuarios = User.objects.filter(is_active=True).count()

    # ── Visitas por hora (hoy) ──────────────────────────────────────────────
    horas_qs = (
        VisitaWeb.objects.filter(timestamp__date=hoy)
        .annotate(hora=ExtractHour("timestamp"))
        .values("hora")
        .annotate(total=Count("id"))
        .order_by("hora")
    )
    por_hora = [0] * 24
    for h in horas_qs:
        por_hora[h["hora"]] = h["total"]

    # ── Visitas últimos 7 días ──────────────────────────────────────────────
    hace_7 = hoy - timedelta(days=6)
    dias_qs = (
        VisitaWeb.objects.filter(timestamp__date__gte=hace_7)
        .annotate(dia=TruncDate("timestamp"))
        .values("dia")
        .annotate(total=Count("id"))
        .order_by("dia")
    )
    dias_mapa = {str(d["dia"]): d["total"] for d in dias_qs}
    labels_7d, data_7d = [], []
    for i in range(7):
        d = hace_7 + timedelta(days=i)
        labels_7d.append(d.strftime("%d/%m"))
        data_7d.append(dias_mapa.get(str(d), 0))

    # ── Top páginas ─────────────────────────────────────────────────────────
    top_paginas_qs = (
        VisitaWeb.objects.values("pagina")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )
    top_paginas_labels = [p["pagina"] for p in top_paginas_qs]
    top_paginas_data = [p["total"] for p in top_paginas_qs]

    # ── Top usuarios ────────────────────────────────────────────────────────
    top_usuarios = (
        VisitaWeb.objects.filter(usuario__isnull=False)
        .values("username_display")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # ── Top IPs ─────────────────────────────────────────────────────────────
    top_ips = (
        VisitaWeb.objects.values("ip")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # ── Dispositivos (móvil vs desktop) ─────────────────────────────────────
    movil_count = VisitaWeb.objects.filter(es_movil=True).count()
    desktop_count = VisitaWeb.objects.filter(es_movil=False).count()

    # ── Navegadores ─────────────────────────────────────────────────────────
    navegadores_qs = (
        VisitaWeb.objects.values("navegador")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    nav_labels = [n["navegador"] for n in navegadores_qs]
    nav_data = [n["total"] for n in navegadores_qs]

    # ── Usuarios activos ahora (detalle) ────────────────────────────────────
    activos_detalle = (
        VisitaWeb.objects.filter(timestamp__gte=hace_cinco)
        .order_by("-timestamp")[:20]
    )

    # ── Tabla de visitas recientes ──────────────────────────────────────────
    qs = VisitaWeb.objects.select_related("usuario").all()

    filtro_ip = request.GET.get("ip", "").strip()
    filtro_usuario = request.GET.get("usuario", "").strip()
    filtro_pagina = request.GET.get("pagina", "").strip()

    if filtro_ip:
        qs = qs.filter(ip__icontains=filtro_ip)
    if filtro_usuario:
        qs = qs.filter(
            Q(username_display__icontains=filtro_usuario)
            | Q(usuario__first_name__icontains=filtro_usuario)
        )
    if filtro_pagina:
        qs = qs.filter(pagina__icontains=filtro_pagina)

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "ahora": ahora,
        "visitas_hoy": visitas_hoy,
        "visitas_semana": visitas_semana,
        "visitas_mes": visitas_mes,
        "ips_unicas_hoy": ips_unicas_hoy,
        "activos_ahora": activos_ahora,
        "duracion_promedio_hoy": duracion_promedio_hoy,
        "total_usuarios": total_usuarios,
        "por_hora": por_hora,
        "labels_7d": labels_7d,
        "data_7d": data_7d,
        "top_paginas_labels": top_paginas_labels,
        "top_paginas_data": top_paginas_data,
        "nav_labels": nav_labels,
        "nav_data": nav_data,
        "movil_count": movil_count,
        "desktop_count": desktop_count,
        "top_usuarios": top_usuarios,
        "top_ips": top_ips,
        "activos_detalle": activos_detalle,
        "page_obj": page_obj,
        "filtro_ip": filtro_ip,
        "filtro_usuario": filtro_usuario,
        "filtro_pagina": filtro_pagina,
    }
    return render(request, "analytics/panel_admin.html", context)


@csrf_exempt
@require_POST
def ping_visita(request):
    try:
        visita_id = int(request.POST.get("visita_id", 0))
        duracion = int(request.POST.get("duracion", 0))
        if visita_id > 0 and duracion > 0:
            VisitaWeb.objects.filter(pk=visita_id).update(duracion_segundos=duracion)
    except (ValueError, TypeError):
        pass
    return JsonResponse({"ok": True})
