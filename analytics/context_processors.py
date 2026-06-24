def visita_id(request):
    return {"visita_id": getattr(request, "_visita_id", None)}


def es_admin_analytics(request):
    es_admin = (
        request.user.is_authenticated
        and (
            request.user.is_superuser
            or request.user.email == "berenicesolohaga@gmail.com"
        )
    )
    return {"es_admin_analytics": es_admin}
