from decimal import Decimal
from django.test import SimpleTestCase
from calculadora.services import (
    rate_from_table,
    es_hipoglucemia,
    debe_suspender,
    ALG1,
)


class LogicTest(SimpleTestCase):

    def test_rate_from_table_devuelve_none_bajo_120(self):
        resultado = rate_from_table(100, ALG1)
        self.assertIsNone(resultado)

    def test_rate_from_table_120_a_149(self):
        resultado = rate_from_table(130, ALG1)
        self.assertEqual(resultado, Decimal("0.5"))

    def test_rate_from_table_150_a_179(self):
        resultado = rate_from_table(160, ALG1)
        self.assertEqual(resultado, Decimal("1"))

    def test_rate_from_table_180_a_209(self):
        resultado = rate_from_table(190, ALG1)
        self.assertEqual(resultado, Decimal("1.5"))

    def test_rate_from_table_210_a_239(self):
        resultado = rate_from_table(220, ALG1)
        self.assertEqual(resultado, Decimal("2"))

    def test_rate_from_table_240_a_269(self):
        resultado = rate_from_table(250, ALG1)
        self.assertEqual(resultado, Decimal("2.5"))

    def test_rate_from_table_270_a_299(self):
        resultado = rate_from_table(280, ALG1)
        self.assertEqual(resultado, Decimal("3"))

    def test_rate_from_table_300_a_329(self):
        resultado = rate_from_table(310, ALG1)
        self.assertEqual(resultado, Decimal("3.5"))

    def test_rate_from_table_330_o_mas(self):
        resultado = rate_from_table(340, ALG1)
        self.assertEqual(resultado, Decimal("4"))

    def test_es_hipoglucemia_true(self):
        self.assertTrue(es_hipoglucemia(69))

    def test_es_hipoglucemia_false_en_70(self):
        self.assertFalse(es_hipoglucemia(70))

    def test_debe_suspender_true(self):
        self.assertTrue(debe_suspender(110))

    def test_debe_suspender_false_en_120(self):
        self.assertFalse(debe_suspender(120))

    # ===== CASOS BORDE IMPORTANTES =====

    def test_borde_69_es_hipoglucemia(self):
        self.assertTrue(es_hipoglucemia(69))

    def test_borde_70_no_es_hipoglucemia(self):
        self.assertFalse(es_hipoglucemia(70))

    def test_borde_119_suspende(self):
        self.assertTrue(debe_suspender(119))

    def test_borde_120_no_suspende(self):
        self.assertFalse(debe_suspender(120))

    def test_borde_119_tabla_devuelve_none(self):
        resultado = rate_from_table(119, ALG1)
        self.assertIsNone(resultado)

    def test_borde_120_tabla_devuelve_0_5(self):
        resultado = rate_from_table(120, ALG1)
        self.assertEqual(resultado, Decimal("0.5"))

    def test_borde_149_tabla_devuelve_0_5(self):
        resultado = rate_from_table(149, ALG1)
        self.assertEqual(resultado, Decimal("0.5"))

    def test_borde_150_tabla_devuelve_1(self):
        resultado = rate_from_table(150, ALG1)
        self.assertEqual(resultado, Decimal("1"))

    def test_borde_179_tabla_devuelve_1(self):
        resultado = rate_from_table(179, ALG1)
        self.assertEqual(resultado, Decimal("1"))

    def test_borde_180_tabla_devuelve_1_5(self):
        resultado = rate_from_table(180, ALG1)
        self.assertEqual(resultado, Decimal("1.5"))

    def test_borde_209_tabla_devuelve_1_5(self):
        resultado = rate_from_table(209, ALG1)
        self.assertEqual(resultado, Decimal("1.5"))

    def test_borde_210_tabla_devuelve_2(self):
        resultado = rate_from_table(210, ALG1)
        self.assertEqual(resultado, Decimal("2"))

    def test_borde_239_tabla_devuelve_2(self):
        resultado = rate_from_table(239, ALG1)
        self.assertEqual(resultado, Decimal("2"))

    def test_borde_240_tabla_devuelve_2_5(self):
        resultado = rate_from_table(240, ALG1)
        self.assertEqual(resultado, Decimal("2.5"))

    def test_borde_269_tabla_devuelve_2_5(self):
        resultado = rate_from_table(269, ALG1)
        self.assertEqual(resultado, Decimal("2.5"))

    def test_borde_270_tabla_devuelve_3(self):
        resultado = rate_from_table(270, ALG1)
        self.assertEqual(resultado, Decimal("3"))

    def test_borde_299_tabla_devuelve_3(self):
        resultado = rate_from_table(299, ALG1)
        self.assertEqual(resultado, Decimal("3"))

    def test_borde_300_tabla_devuelve_3_5(self):
        resultado = rate_from_table(300, ALG1)
        self.assertEqual(resultado, Decimal("3.5"))

    def test_borde_329_tabla_devuelve_3_5(self):
        resultado = rate_from_table(329, ALG1)
        self.assertEqual(resultado, Decimal("3.5"))

    def test_borde_330_tabla_devuelve_4(self):
        resultado = rate_from_table(330, ALG1)
        self.assertEqual(resultado, Decimal("4"))