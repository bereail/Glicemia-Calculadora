from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from calculadora.models import MedicionGlucemia


class HistorialViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)

        MedicionGlucemia.objects.create(
            usuario=self.user,
            glicemia=150,
            modo="inicio",
            infusion_activa=True,
            glicemia_previa=140,
            estado="En objetivo",
            clase="ok",
            conducta="Mantener conducta actual",
            mensaje="Glucemia dentro del rango objetivo.",
            proximo_control="Cada 6 horas si permanece estable",
            observacion="Continuar monitoreo",
            tendencia="Ascenso",
            algoritmo_usado="Inicio / Reinicio (Algoritmo 1)",
            velocidad_sugerida="1",
            bolo_ui="",
            tasa_inicial_ui_h="",
            alerta_hgr=False,
        )

    def test_historial_requiere_login(self):
        response = self.client.get(reverse("historial"))
        self.assertEqual(response.status_code, 302)

    def test_historial_usuario_autorizado_puede_verlo(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("historial"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historial de mediciones")
        self.assertContains(response, "150")
        self.assertContains(response, "En objetivo")

    def test_historial_filtra_por_usuario(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("historial"), {"usuario": "testuser"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "150")

    def test_historial_filtra_por_estado(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("historial"), {"estado": "En objetivo"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "En objetivo")
