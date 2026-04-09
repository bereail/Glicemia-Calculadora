from django.test import SimpleTestCase

from calculadora.utils.logic.logic_hiper import (
    obtener_escalon_glucemia,
    estan_en_mismo_escalon,
    es_hiperglucemia_persistente,
    es_fallo_algoritmo_1,
    sugerir_algoritmo,
    obtener_tasa_algoritmo_1,
    obtener_tasa_algoritmo_2,
)


class HiperglucemiaLogicTests(SimpleTestCase):
    def test_obtener_escalon_glucemia_120_es_e1(self):
        self.assertEqual(obtener_escalon_glucemia(120), "E1")

    def test_obtener_escalon_glucemia_149_es_e1(self):
        self.assertEqual(obtener_escalon_glucemia(149), "E1")

    def test_obtener_escalon_glucemia_150_es_e2(self):
        self.assertEqual(obtener_escalon_glucemia(150), "E2")

    def test_obtener_escalon_glucemia_239_es_e4(self):
        self.assertEqual(obtener_escalon_glucemia(239), "E4")

    def test_obtener_escalon_glucemia_240_es_e5(self):
        self.assertEqual(obtener_escalon_glucemia(240), "E5")

    def test_estan_en_mismo_escalon_true(self):
        self.assertTrue(estan_en_mismo_escalon(240, 250))

    def test_estan_en_mismo_escalon_false(self):
        self.assertFalse(estan_en_mismo_escalon(230, 250))

    def test_persistente_con_dos_mayores_iguales_360(self):
        self.assertTrue(
            es_hiperglucemia_persistente(
                actual=380,
                previa=370,
                infusion_activa=True,
            )
        )

    def test_persistente_con_tres_valores_200_360(self):
        self.assertTrue(
            es_hiperglucemia_persistente(
                actual=250,
                previa=240,
                anterior=230,
                infusion_activa=True,
            )
        )

    def test_no_persistente_sin_infusion(self):
        self.assertFalse(
            es_hiperglucemia_persistente(
                actual=250,
                previa=240,
                anterior=230,
                infusion_activa=False,
            )
        )

    def test_no_persistente_si_falta_tercera_en_200_360(self):
        self.assertFalse(
            es_hiperglucemia_persistente(
                actual=250,
                previa=240,
                infusion_activa=True,
            )
        )

    def test_fallo_algoritmo_1_true(self):
        self.assertTrue(
            es_fallo_algoritmo_1(
                actual=250,
                previa=245,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            )
        )

    def test_fallo_algoritmo_1_false_sin_ajuste(self):
        self.assertFalse(
            es_fallo_algoritmo_1(
                actual=250,
                previa=245,
                infusion_activa=True,
                hubo_ajuste_insulina=False,
            )
        )

    def test_fallo_algoritmo_1_false_distinto_escalon(self):
        self.assertFalse(
            es_fallo_algoritmo_1(
                actual=250,
                previa=180,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            )
        )

    def test_sugerir_algoritmo_2_si_persistente(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=250,
                previa=240,
                anterior=230,
                infusion_activa=True,
            ),
            2,
        )

    def test_sugerir_algoritmo_2_si_fallo_algoritmo_1(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=250,
                previa=245,
                infusion_activa=True,
                hubo_ajuste_insulina=True,
            ),
            2,
        )

    def test_sugerir_algoritmo_1_si_no_hay_persistente_ni_fallo(self):
        self.assertEqual(
            sugerir_algoritmo(
                actual=250,
                previa=210,
                infusion_activa=True,
                hubo_ajuste_insulina=False,
            ),
            1,
        )

    def test_tasa_algoritmo_1_e5(self):
        self.assertEqual(obtener_tasa_algoritmo_1(250), "2,5 UI/h")

    def test_tasa_algoritmo_2_e5(self):
        self.assertEqual(obtener_tasa_algoritmo_2(250), "3,5 UI/h")