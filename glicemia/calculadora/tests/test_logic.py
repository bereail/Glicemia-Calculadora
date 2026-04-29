import unittest

from django.test import SimpleTestCase


@unittest.skip(
    "Pendiente: crear una función de servicio real para evaluar la lógica clínica."
)
class EvaluarGlicemiaTests(SimpleTestCase):
    def test_hipoglucemia_si_actual_menor_o_igual_a_70(self):
        pass

    def test_en_rango_si_actual_entre_71_y_179_sin_infusion(self):
        pass

    def test_hiperglucemia_sostenida_si_actual_y_previa_mayor_o_igual_180_sin_infusion(
        self,
    ):
        pass

    def test_en_objetivo_si_infusion_activa_y_valor_entre_140_y_200(self):
        pass

    def test_si_infusion_activa_y_actual_alta_puede_requerir_previa(self):
        pass

    def test_actual_70_debe_contar_como_hipoglucemia(self):
        pass
