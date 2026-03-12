from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="1234testseguro"
        )
        self.url = reverse("home")

    def login(self):
        self.client.login(username="admin", password="1234testseguro")

    def test_home_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_home_loads_for_logged_user(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculadora/home.html")
        self.assertContains(response, "Ingresar medición")

    def test_valid_form_shows_result(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": 180,
            "glucemia_previa": 160,
            "modo": "inicio",
            "infusion_activa": "no",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado")

    def test_invalid_form_missing_glucemia(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": "",
            "glucemia_previa": 160,
            "modo": "inicio",
            "infusion_activa": "no",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hay datos inválidos")
        self.assertFormError(response, "form", "glucemia", "Ingresá la glucemia actual.")

    def test_invalid_form_non_numeric_glucemia(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": "abc",
            "glucemia_previa": 160,
            "modo": "inicio",
            "infusion_activa": "no",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hay datos inválidos")

    def test_hypoglycemia_result(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": 60,
            "glucemia_previa": 80,
            "modo": "inicio",
            "infusion_activa": "no",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hipoglucemia")
        self.assertContains(response, "Suspender infusión")
        self.assertContains(response, "30 minutos")

    def test_suspend_infusion_result_under_120(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": 100,
            "glucemia_previa": 140,
            "modo": "inicio",
            "infusion_activa": "si",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detener infusión")
        self.assertContains(response, "Suspender infusión")

    def test_in_target_result(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": 150,
            "glucemia_previa": 170,
            "modo": "alg2",
            "infusion_activa": "si",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "En objetivo")
        self.assertContains(response, "Mantener conducta actual")

    def test_hyperglycemia_result(self):
        self.login()
        response = self.client.post(self.url, {
            "glucemia": 250,
            "glucemia_previa": 220,
            "modo": "alg2",
            "infusion_activa": "si",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hiperglucemia")
        self.assertContains(response, "Ajustar infusión según algoritmo")

    def test_persistent_severe_hyperglycemia_alert(self):
        self.login()

        self.client.post(self.url, {
            "glucemia": 380,
            "glucemia_previa": 300,
            "modo": "alg2",
            "infusion_activa": "si",
        })

        response = self.client.post(self.url, {
            "glucemia": 390,
            "glucemia_previa": 380,
            "modo": "alg2",
            "infusion_activa": "si",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "URGENTE")
        self.assertContains(response, "Hiperglucemia persistente grave")

    def test_clean_get_after_post_still_works(self):
        self.login()

        self.client.post(self.url, {
            "glucemia": 180,
            "glucemia_previa": 170,
            "modo": "inicio",
            "infusion_activa": "no",
        })

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresar medición")