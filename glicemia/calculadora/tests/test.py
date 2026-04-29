from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CalculadoraFlujoActualTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="1234")

    def test_redirige_si_no_esta_logueado(self):
        response = self.client.get(reverse("control_glicemia"))
        self.assertIn(response.status_code, [301, 302])

    def test_get_logueado_muestra_pantalla(self):
        self.client.login(username="tester", password="1234")
        response = self.client.get(reverse("control_glicemia"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Control de glicemia")

    def test_post_hipoglucemia(self):
        self.client.login(username="tester", password="1234")
        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 65,
                "infusion_activa": "no",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado")

    def test_post_con_previa(self):
        self.client.login(username="tester", password="1234")
        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 190,
                "glicemia_previa": 185,
                "infusion_activa": "no",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado")

    def test_post_con_infusion_activa(self):
        self.client.login(username="tester", password="1234")
        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 180,
                "glicemia_previa": 170,
                "infusion_activa": "si",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado")
