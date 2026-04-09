from django.test import SimpleTestCase

from utils.logic.logic_hiper import (
    obtener_escalon_glucemia,
    obtener_tasa_algoritmo_1,
    obtener_tasa_algoritmo_2,
    estan_en_mismo_escalon,
    es_hiperglucemia_persistente,
    es_fallo_algoritmo_1,
    sugerir_algoritmo,
    evaluar_hiperglucemia,
)


class HiperglucemiaHelpersTests(SimpleTestCase):
    def test_obtener_escalon_glucemia(self):
        self.assertEqual(obtener_escalon_glucemia(110), "E0")
        self.assertEqual(obtener_escalon_glucemia(120), "E1")
        self.assertEqual(obtener_escalon_glucemia(149), "E1")
        self.assertEqual(obtener_escalon_glucemia(150), "E2")
        self.assertEqual(obtener_escalon_glucemia(179), "E2")
        self.assertEqual(obtener_escalon_glucemia(180), "E3")
        self.assertEqual(obtener_escalon_glucemia(209), "E3")
        self.assertEqual(obtener_escalon_glucemia(360), "E9")

    def test_tasa_algoritmo_1(self):
        self.assertEqual(obtener_tasa_algoritmo_1(110), "Suspender")
        self.assertEqual(obtener_tasa_algoritmo_1(145), "0,5 UI/h")
        self.assertEqual(obtener_tasa_algoritmo_1(185), "1,5 UI/h")
        self.assertEqual(obtener_tasa_algoritmo_1(365), "5 UI/h")

    def test_tasa_algoritmo_2(self):
        self.assertEqual(obtener_tasa_algoritmo_2(110), "Suspender")
        self.assertEqual(obtener_tasa_algoritmo_2(145), "1 UI/h")
        self.assertEqual(obtener_tasa_algoritmo_2(185), "2,5 UI/h")
        self.assertEqual(obtener_tasa_algoritmo_2(365), "8 UI/h")

    def test_estan_en_mismo_escalon(self):
        self.assertTrue(estan_en_mismo_escalon(210, 220, 235))
        self.assertFalse(estan_en_mismo_escalon(210, 250, 235))
        self.assertFalse(estan_en_mismo_escalon(210, None))


class HiperglucemiaPersistenteTests(SimpleTestCase):
    def test_persistente_si_dos_consecutivos_mayor_igual_360_con_infusion(self):
        self.assertTrue(
            es_hiperglucemia_persistente(
                actual=370,
                previa=365,
                anterior=None,
                infusion_activa=True,
            )
        )

    def test_no_persistente_si_no_hay_infusion(self):
        self.assertFalse(
            es_hiperglucemia_persistente(
                actual=370,
                previa=365,
                anterior=None,
                infusion_activa=False,
            )
        )

    def test_persistente_si_tres_mayores_a_200_y_menores_a_360_mismo_escalon(self):
        self.assertTrue(
            es_hiperglucemia_persistente(
                actual=220,
                previa=225,
                anterior=230,
                infusion_activa=True,
            )
        )

    def test_no_persistente_si_tres_mayores_a_200_pero_distinto_escalon(self):
        self.assertFalse(
            es_hiperglucemia_persistente(
                actual=220,
                previa=250,
                anterior=230,
                infusion_activa=True,
            )
        )

    def test_no_persistente_si_faltan_mediciones_en_rango_200_360(self):
        self.assertFalse(
            es_hiperglucemia_persistente(
                actual=220,
                previa=225,
                anterior=None,
                infusion_activa=True,
            )
        )


class FalloAlgoritmoTests(SimpleTestCase):
    def test_fallo_algoritmo_1_si_mismo_escalon_fuera_objetivo_y_hubo_ajuste(self):
        self.assertTrue(
            es_fallo_algoritmo_1(
                actual=220,
                previa=230,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            )
        )

    def test_no_fallo_algoritmo_1_si_no_hubo_ajuste(self):
        self.assertFalse(
            es_fallo_algoritmo_1(
                actual=220,
                previa=230,
                infusion_activa=True,
                hubo_ajuste_insulina=False,
            )
        )

    def test_no_fallo_algoritmo_1_si_no_mismo_escalon(self):
        self.assertFalse(
            es_fallo_algoritmo_1(
                actual=220,
                previa=280,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            )
        )


class SugerirAlgoritmoTests(SimpleTestCase):
    def test_sugerir_algoritmo_2_si_persistente(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=220,
                previa=225,
                anterior=230,
                infusion_activa=True,
                hubo_ajuste_insulina=False,
            ),
            2,
        )

    def test_sugerir_algoritmo_2_si_fallo_algoritmo_1(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=220,
                previa=230,
                anterior=None,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            ),
            2,
        )

    def test_sugerir_algoritmo_1_si_no_hay_criterios_de_algoritmo_2(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=220,
                previa=190,
                anterior=None,
                infusion_activa=True,
                hubo_ajuste_insulina=False,
            ),
            1,
        )


class EvaluarHiperglucemiaTests(SimpleTestCase):
    def test_sin_infusion_menor_180_no_es_hiper(self):
        resultado = evaluar_hiperglucemia(
            actual=170,
            previa=None,
            infusion_activa=False,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertIsNone(resultado)

    def test_sin_infusion_180_o_mas_sin_previa_es_aislada(self):
        resultado = evaluar_hiperglucemia(
            actual=180,
            previa=None,
            infusion_activa=False,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Aislada")
        self.assertTrue(resultado["requiere_recontrol"])

    def test_sin_infusion_con_dos_consecutivas_180_o_mas_inicia_insulinizacion(self):
        resultado = evaluar_hiperglucemia(
            actual=220,
            previa=200,
            infusion_activa=False,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertIsNotNone(resultado)
        self.assertTrue(resultado["mostrar_resultado"])

    def test_con_infusion_hasta_200_no_es_hiper(self):
        resultado = evaluar_hiperglucemia(
            actual=200,
            previa=190,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_360_y_previa_360_o_mas_es_persistente(self):
        resultado = evaluar_hiperglucemia(
            actual=370,
            previa=365,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Persistente")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")
        self.assertEqual(resultado["tasa_algoritmo"], "8 UI/h")

    def test_con_infusion_360_sin_previa_alta_es_sostenida(self):
        resultado = evaluar_hiperglucemia(
            actual=370,
            previa=250,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Sostenida")
        self.assertTrue(resultado["requiere_recontrol"])

    def test_con_infusion_tres_mediciones_mismo_escalon_es_persistente(self):
        resultado = evaluar_hiperglucemia(
            actual=220,
            previa=225,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=230,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Persistente")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")

    def test_con_infusion_dos_mediciones_altas_sin_tercera_pide_tercera(self):
        resultado = evaluar_hiperglucemia(
            actual=220,
            previa=225,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia")
        self.assertIn("tercera", resultado["conducta"].lower())
        self.assertEqual(resultado["proximo_control"], "Obtener tercera medición")

    def test_con_infusion_y_fallo_algoritmo_1_es_refractaria(self):
        resultado = evaluar_hiperglucemia(
            actual=220,
            previa=230,
            infusion_activa=True,
            hubo_ajuste_insulina=True,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Refractaria")
        self.assertEqual(resultado["algoritmo_sugerido"], "Algoritmo 2")

    def test_con_infusion_mayor_200_sin_previa_alta_es_marcada(self):
        resultado = evaluar_hiperglucemia(
            actual=220,
            previa=180,
            infusion_activa=True,
            hubo_ajuste_insulina=False,
            tercera_medicion=None,
        )
        self.assertEqual(resultado["estado"], "Hiperglucemia Marcada")
        self.assertTrue(resultado["requiere_recontrol"])