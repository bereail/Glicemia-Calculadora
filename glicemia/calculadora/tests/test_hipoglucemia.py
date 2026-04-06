from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from calculadora.services import evaluar_glucemia


class HipoglucemiaLogicTests(SimpleTestCase):
    def test_todos_los_valores_menores_a_60_son_hipoglucemia(self):
        casos = [
            {"actual": 59, "previa": None, "infusion": False},
            {"actual": 59, "previa": 300, "infusion": False},
            {"actual": 59, "previa": 180, "infusion": True},
            {"actual": 55, "previa": 100, "infusion": False},
            {"actual": 45, "previa": 80, "infusion": True},
            {"actual": 30, "previa": 250, "infusion": False},
            {"actual": 1, "previa": 90, "infusion": False},
        ]

        for caso in casos:
            with self.subTest(caso=caso):
                resultado = evaluar_glucemia(
                    glucemia_actual=caso["actual"],
                    glucemia_previa=caso["previa"],
                    infusion_activa=caso["infusion"],
                )
                self.assertEqual(resultado["estado"], "hipoglucemia")

    def test_60_y_mayores_no_son_hipoglucemia(self):
        casos = [
            {"actual": 60, "previa": 90, "infusion": False},
            {"actual": 61, "previa": 90, "infusion": False},
            {"actual": 100, "previa": 90, "infusion": True},
        ]

        for caso in casos:
            with self.subTest(caso=caso):
                resultado = evaluar_glucemia(
                    glucemia_actual=caso["actual"],
                    glucemia_previa=caso["previa"],
                    infusion_activa=caso["infusion"],
                )
                self.assertNotEqual(resultado["estado"], "hipoglucemia")

    def test_hipoglucemia_tiene_prioridad_absoluta(self):
        resultado = evaluar_glucemia(
            glucemia_actual=40,
            glucemia_previa=300,
            infusion_activa=True,
        )
        self.assertEqual(resultado["estado"], "hipoglucemia")
        self.assertNotEqual(resultado.get("estado"), "hiperglucemia")
        self.assertNotEqual(resultado.get("clase"), "hiperglucemia")
        self.assertNotEqual(resultado.get("clase"), "en_rango")


class VistaHipoglucemiaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="1234",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.user)

    def test_post_con_actual_menor_a_60_muestra_hipoglucemia(self):
        response = self.client.post(
            reverse("home"),
            {
                "glucemia_actual": 55,
                "glucemia_previa": 180,
                "infusion_activa": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado")
        self.assertIn("hipoglucemia", response.content.decode().lower())

    def test_post_con_actual_menor_a_60_no_muestra_hiperglucemia(self):
        response = self.client.post(
            reverse("home"),
            {
                "glucemia_actual": 55,
                "glucemia_previa": 180,
                "infusion_activa": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode().lower()
        self.assertIn("hipoglucemia", contenido)
        self.assertNotIn("hiperglucemia", contenido)

    def test_post_con_actual_menor_a_60_funciona_aunque_la_previa_sea_alta(self):
        response = self.client.post(
            reverse("home"),
            {
                "glucemia_actual": 50,
                "glucemia_previa": 300,
                "infusion_activa": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode().lower()
        self.assertIn("resultado", contenido)
        self.assertIn("hipoglucemia", contenido)

    def test_post_con_actual_59_y_sin_previa_tambien_da_hipoglucemia(self):
        response = self.client.post(
            reverse("home"),
            {
                "glucemia_actual": 59,
                "infusion_activa": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode().lower()
        self.assertIn("hipoglucemia", contenido)