from django.test import SimpleTestCase

from calculadora.utils.logic.logic_hiper import evaluar_hiperglucemia


class EvaluarHiperglucemiaTests(SimpleTestCase):
    def test_sin_infusion_menor_180_devuelve_none(self):
        resultado = evaluar_hiperglucemia(
            actual=150,
            infusion_activa=False,
        )
        self.assertIsNone(resultado)

    def test_sin_infusion_180_sin_previa_es_aislada(self):
        resultado = evaluar_hiperglucemia(
            actual=180,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia Aislada")

    def test_sin_infusion_con_previa_alta_indica_insulinizacion(self):
        resultado = evaluar_hiperglucemia(
            actual=210,
            previa=190,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertTrue(resultado["mostrar_resultado"])

    def test_con_infusion_hasta_200_devuelve_none(self):
        resultado = evaluar_hiperglucemia(
            actual=200,
            previa=180,
            infusion_activa=True,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_mayor_200_sin_previa_es_marcada(self):
        resultado = evaluar_hiperglucemia(
            actual=250,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia Marcada")

    def test_con_infusion_dos_mayores_200_pide_tercera(self):
        resultado = evaluar_hiperglucemia(
            actual=250,
            previa=220,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia")
        self.assertEqual(resultado["proximo_control"], "Obtener tercera medición")

    def test_con_infusion_tres_mediciones_persistente(self):
        resultado = evaluar_hiperglucemia(
            actual=250,
            previa=240,
            tercera_medicion=230,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia Persistente")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")

    def test_con_infusion_dos_mayores_360_es_persistente(self):
        resultado = evaluar_hiperglucemia(
            actual=380,
            previa=370,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia Persistente")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")

    def test_con_ajuste_previo_y_mismo_escalon_es_refractaria(self):
        resultado = evaluar_hiperglucemia(
            actual=250,
            previa=245,
            infusion_activa=True,
            hubo_ajuste_insulina=True,
        )
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["estado"], "Hiperglucemia Refractaria")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")

    def test_con_ajuste_previo_pero_distinto_escalon_no_es_refractaria(self):
        resultado = evaluar_hiperglucemia(
            actual=250,
            previa=180,
            infusion_activa=True,
            hubo_ajuste_insulina=True,
        )
        self.assertIsNotNone(resultado)
        self.assertNotEqual(resultado["estado"], "Hiperglucemia Refractaria")
