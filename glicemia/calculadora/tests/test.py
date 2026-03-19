from django.test import TestCase
from django.urls import reverse


class CalculadoraGuiadaTests(TestCase):
    def test_hipoglucemia(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 65,
            "glucemia_previa": 150,
        })
        self.assertContains(response, "Hipoglucemia")
        self.assertContains(response, "menor a 70")

    def test_suspender_infusion(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 100,
            "glucemia_previa": 180,
        })
        self.assertContains(response, "Suspender infusión")

    def test_muestra_infusion_activa_cuando_supera_119(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 150,
            "glucemia_previa": 160,
        })
        self.assertContains(response, "¿Infusión activa?")

    def test_sin_hiperglucemia_sostenida(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 150,
            "glucemia_previa": 160,
            "infusion_activa": "si",
        })
        self.assertContains(response, "Sin hiperglucemia sostenida")

    def test_iniciar_manejo_si_no_hay_infusion(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 220,
            "glucemia_previa": 210,
            "infusion_activa": "no",
        })
        self.assertContains(response, "Iniciar manejo")

    def test_algoritmo_1_continuar_si_no_supera_200(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 190,
            "glucemia_previa": 190,
            "infusion_activa": "si",
            "algoritmo": "alg1",
        })
        self.assertContains(response, "Continuar Algoritmo 1")

    def test_algoritmo_1_hgp_por_ultimo_escalon(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 220,
            "glucemia_previa": 210,
            "infusion_activa": "si",
            "algoritmo": "alg1",
            "ultimo_escalon_hgp": "si",
            "subio_ultimas_2": "no",
            "mismo_escalon_3": "no",
        })
        self.assertContains(response, "HGP")
        self.assertContains(response, "pasar a Algoritmo 2")

    def test_algoritmo_1_hgp_por_subio_ultimas_2(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 220,
            "glucemia_previa": 210,
            "infusion_activa": "si",
            "algoritmo": "alg1",
            "ultimo_escalon_hgp": "no",
            "subio_ultimas_2": "si",
            "mismo_escalon_3": "no",
        })
        self.assertContains(response, "HGP")

    def test_algoritmo_1_hgp_por_mismo_escalon_3(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 220,
            "glucemia_previa": 210,
            "infusion_activa": "si",
            "algoritmo": "alg1",
            "ultimo_escalon_hgp": "no",
            "subio_ultimas_2": "no",
            "mismo_escalon_3": "si",
        })
        self.assertContains(response, "HGP")

    def test_algoritmo_1_no_hgp(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 220,
            "glucemia_previa": 210,
            "infusion_activa": "si",
            "algoritmo": "alg1",
            "ultimo_escalon_hgp": "no",
            "subio_ultimas_2": "no",
            "mismo_escalon_3": "no",
        })
        self.assertContains(response, "Continuar Algoritmo 1")

    def test_algoritmo_2_continuar_si_no_supera_360(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 300,
            "glucemia_previa": 310,
            "infusion_activa": "si",
            "algoritmo": "alg2",
        })
        self.assertContains(response, "Continuar Algoritmo 2")

    def test_algoritmo_2_continuar_si_supera_360_pero_no_ultimo_escalon(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 370,
            "glucemia_previa": 365,
            "infusion_activa": "si",
            "algoritmo": "alg2",
            "ultimo_escalon_alg2": "no",
        })
        self.assertContains(response, "Continuar Algoritmo 2")

    def test_algoritmo_2_avisar_medico(self):
        response = self.client.post(reverse("guiada"), {
            "glucemia_actual": 370,
            "glucemia_previa": 365,
            "infusion_activa": "si",
            "algoritmo": "alg2",
            "ultimo_escalon_alg2": "si",
        })
        self.assertContains(response, "Hiperglucemia refractaria")
        self.assertContains(response, "Avisar médico")