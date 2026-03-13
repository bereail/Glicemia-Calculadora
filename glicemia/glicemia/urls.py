from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from calculadora.views import home, historial

urlpatterns = [
    path("admin/", admin.site.urls),

    # LOGIN
    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),

    # LOGOUT
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # HOME
    path("", home, name="home"),

    # HISTORIAL
    path("historial/", historial, name="historial"),
]