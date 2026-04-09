from django.contrib.auth import get_user_model
from django.test import TestCase


class RegresionClinicaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_staff=True,      # 👈 clave
            is_superuser=True   # 👈 más seguro todavía
        )
        self.client.login(username="testuser", password="testpass123")
    def test_caso_1_hipoglucemia_severa(self):
        response = self.client.post("/", {
            "glicemia_actual": 55,
        }, follow=True)
        self.assertContains(response, "hipoglucemia")

    def test_caso_2_rango_normal_sin_infusion(self):
        response = self.client.post("/", {
            "glicemia_actual": 110,
            "infusion_activa": "false",
        }, follow=True)
        self.assertContains(response, "rango")

    def test_caso_3_rango_con_alerta(self):
        response = self.client.post("/", {
            "glicemia_actual": 85,
            "infusion_activa": "false",
        }, follow=True)
        self.assertContains(response, "hipoglucemia")

    def test_caso_4_hiper_aislada(self):
        response = self.client.post("/", {
            "glicemia_actual": 185,
            "infusion_activa": "false",
        }, follow=True)
        self.assertContains(response, "aislada")

    def test_caso_5_hiper_en_ascenso(self):
        response = self.client.post("/", {
            "glicemia_actual": 200,
            "infusion_activa": "false",
            "glicemia_previa": 150,
        }, follow=True)
        self.assertContains(response, "ascenso")

    def test_caso_6_iniciar_insulina(self):
        response = self.client.post("/", {
            "glicemia_actual": 220,
            "infusion_activa": "false",
            "glicemia_previa": 200,
        }, follow=True)
        self.assertContains(response, "algoritmo")

    def test_caso_7_hiper_con_infusion(self):
        response = self.client.post("/", {
            "glicemia_actual": 240,
            "infusion_activa": "true",
            "glicemia_previa": 220,
        }, follow=True)
        self.assertContains(response, "hiperglucemia")

    def test_caso_8_pide_tercera_medicion(self):
        response = self.client.post("/", {
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 230,
        }, follow=True)
        self.assertContains(response, "tercera")

    def test_caso_9_persistente(self):
        response = self.client.post("/", {
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 240,
            "tercera_medicion": 230,
        }, follow=True)
        self.assertContains(response, "persistente")
        self.assertContains(response, "algoritmo 2")

    def test_caso_10_persistente_severa(self):
        response = self.client.post("/", {
            "glicemia_actual": 380,
            "infusion_activa": "true",
            "glicemia_previa": 370,
        }, follow=True)
        self.assertContains(response, "persistente")

    def test_caso_11_refractaria(self):
        response = self.client.post("/", {
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 245,
            "hubo_ajuste_insulina": "true",
        }, follow=True)
        self.assertContains(response, "refractaria")

    def test_caso_12_borde_200_con_infusion(self):
        response = self.client.post("/", {
            "glicemia_actual": 200,
            "infusion_activa": "true",
            "glicemia_previa": 180,
        }, follow=True)
        self.assertNotContains(response, "persistente")