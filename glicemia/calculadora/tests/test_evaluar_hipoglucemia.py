from django.test import SimpleTestCase

from calculadora.utils.logic.logic_hipo import evaluar_hipoglucemia


class EvaluarHipoglucemiaTests(SimpleTestCase):
    def test_menor_70_es_hipoglucemia(self):
        resultado = evaluar_hipoglucemia(
            actual=65,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertIn("hipoglucemia", resultado["estado"].lower())

    def test_en_70_es_hipoglucemia(self):
        resultado = evaluar_hipoglucemia(
            actual=70,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertIn("hipoglucemia", resultado["estado"].lower())

    def test_mayor_70_no_es_hipoglucemia_directa(self):
        resultado = evaluar_hipoglucemia(
            actual=71,
            infusion_activa=False,
        )
        self.assertIsNone(resultado)

    def test_hipoglucemia_con_infusion_muestra_conducta(self):
        resultado = evaluar_hipoglucemia(
            actual=68,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertTrue(resultado["mostrar_resultado"])
        self.assertTrue(resultado["conducta"])

    def test_hipoglucemia_sin_infusion_muestra_recontrol(self):
        resultado = evaluar_hipoglucemia(
            actual=60,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertTrue(resultado["requiere_recontrol"])