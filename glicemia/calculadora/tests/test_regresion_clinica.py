from django.contrib.auth import get_user_model
from django.test import TestCase


class RegresionClinicaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(username="testuser", password="testpass123")

    def _post(self, data):
        return self.client.post("/", data, follow=True)

    def _assert_contains_text(self, response, text):
        contenido = response.content.decode("utf-8").lower()
        self.assertIn(text.lower(), contenido)

    def _assert_not_contains_text(self, response, text):
        contenido = response.content.decode("utf-8").lower()
        self.assertNotIn(text.lower(), contenido)

    def test_caso_1_hipoglucemia_severa(self):
        response = self._post({
            "glicemia_actual": 55,
        })
        self._assert_contains_text(response, "hipoglucemia")

    def test_caso_2_rango_normal_sin_infusion(self):
        response = self._post({
            "glicemia_actual": 110,
            "infusion_activa": "false",
        })
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue("rango" in contenido or "objetivo" in contenido)

    def test_caso_3_rango_con_alerta(self):
        response = self._post({
            "glicemia_actual": 85,
            "infusion_activa": "false",
        })
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue("hipoglucemia" in contenido or "cercano a hipoglucemia" in contenido)

    def test_caso_4_hiper_aislada(self):
        response = self._post({
            "glicemia_actual": 185,
            "infusion_activa": "false",
        })
        self._assert_contains_text(response, "aislada")

    def test_caso_5_hiper_en_ascenso(self):
        response = self._post({
            "glicemia_actual": 200,
            "infusion_activa": "false",
            "glicemia_previa": 150,
        })
        self._assert_contains_text(response, "ascenso")

    def test_caso_6_iniciar_insulina(self):
        response = self._post({
            "glicemia_actual": 220,
            "infusion_activa": "false",
            "glicemia_previa": 200,
        })
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue("algoritmo" in contenido or "insuliniz" in contenido)

    def test_caso_7_hiper_con_infusion(self):
        response = self._post({
            "glicemia_actual": 240,
            "infusion_activa": "true",
            "glicemia_previa": 180,
        })
        self._assert_contains_text(response, "hiperglucemia")

    def test_caso_8_pide_tercera_medicion(self):
        response = self._post({
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 230,
        })
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue("tercera medición" in contenido or "obtener tercera medición" in contenido)

    def test_caso_9_persistente(self):
        response = self._post({
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 240,
            "tercera_medicion": 230,
        })
        self._assert_contains_text(response, "hiperglucemia persistente")
        self._assert_contains_text(response, "algoritmo 2")

    def test_caso_10_persistente_severa(self):
        response = self._post({
            "glicemia_actual": 380,
            "infusion_activa": "true",
            "glicemia_previa": 370,
        })
        self._assert_contains_text(response, "persistente")
        self._assert_contains_text(response, "algoritmo 2")

    def test_caso_11_refractaria(self):
        response = self._post({
            "glicemia_actual": 250,
            "infusion_activa": "true",
            "glicemia_previa": 245,
            "hubo_ajuste_insulina": "true",
        })
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue("refractaria" in contenido or "algoritmo 2" in contenido)

    def test_caso_12_borde_200_con_infusion(self):
        response = self._post({
            "glicemia_actual": 200,
            "infusion_activa": "true",
            "glicemia_previa": 180,
        })
        self._assert_not_contains_text(response, "hiperglucemia persistente")