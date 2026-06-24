_SKIP_PREFIXES = (
    "/static/",
    "/staticfiles/",
    "/analytics/ping/",
    "/favicon.ico",
    "/admin/",
)


def _get_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _detectar_navegador(ua: str) -> str:
    u = ua.lower()
    if "edg/" in u or "edge/" in u:
        return "Edge"
    if "opr/" in u or "opera" in u:
        return "Opera"
    if "firefox" in u or "fxios" in u:
        return "Firefox"
    if "chrome" in u or "crios" in u:
        return "Chrome"
    if "safari" in u:
        return "Safari"
    return "Otro"


def _es_movil(ua: str) -> bool:
    u = ua.lower()
    return any(k in u for k in ("mobile", "android", "iphone", "ipad", "tablet"))


class RegistroVisitasMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pagina = request.path

        if not any(pagina.startswith(p) for p in _SKIP_PREFIXES):
            try:
                from .models import VisitaWeb

                ua = request.META.get("HTTP_USER_AGENT", "")
                usuario = (
                    request.user
                    if hasattr(request, "user") and request.user.is_authenticated
                    else None
                )
                visita = VisitaWeb.objects.create(
                    ip=_get_ip(request),
                    usuario=usuario,
                    username_display=usuario.username if usuario else "",
                    pagina=pagina,
                    metodo=request.method,
                    user_agent=ua[:500],
                    referrer=request.META.get("HTTP_REFERER", "")[:500],
                    session_key=(request.session.session_key or "")[:100],
                    es_movil=_es_movil(ua),
                    navegador=_detectar_navegador(ua),
                )
                request._visita_id = visita.id
            except Exception:
                pass

        return self.get_response(request)
