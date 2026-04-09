from django.test import SimpleTestCase

from calculadora.utils.logic.logic_rango import evaluar_rango_70_180


class EvaluarRangoObjetivoTests(SimpleTestCase):
    def test_sin_infusion_entre_90_y_179_es_rango(self):
        resultado = evaluar_rango_70_180(
            actual=120,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertIn("rango", resultado["estado"].lower())

    def test_sin_infusion_entre_70_y_90_es_rango_con_advertencia(self):
        resultado = evaluar_rango_70_180(
            actual=85,
            infusion_activa=False,
        )
        self.assertIsNotNone(resultado)
        self.assertIn("rango", resultado["estado"].lower())
        texto = f'{resultado.get("mensaje", "")} {resultado.get("comentario_control", "")}'.lower()
        self.assertIn("hipoglucemia", texto)

    def test_sin_infusion_en_180_ya_no_es_rango(self):
        resultado = evaluar_rango_70_180(
            actual=180,
            infusion_activa=False,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_140_a_180_es_objetivo(self):
        resultado = evaluar_rango_70_180(
            actual=160,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        self.assertIn("objetivo", resultado["estado"].lower())

    def test_con_infusion_entre_70_y_120_es_objetivo_con_alerta(self):
        resultado = evaluar_rango_70_180(
            actual=100,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)
        texto = (
            f'{resultado.get("estado", "")} '
            f'{resultado.get("mensaje", "")} '
            f'{resultado.get("comentario_control", "")}'
        ).lower()
        self.assertTrue("hipoglucemia" in texto or "cercano" in texto)

    def test_con_infusion_120_a_139_devuelve_resultado_segun_logica_actual(self):
        resultado = evaluar_rango_70_180(
            actual=130,
            infusion_activa=True,
        )
        self.assertIsNotNone(resultado)

    def test_con_infusion_181_no_entra_en_evaluar_rango_70_180(self):
        resultado = evaluar_rango_70_180(
            actual=181,
            infusion_activa=True,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_190_no_entra_en_evaluar_rango_70_180(self):
        resultado = evaluar_rango_70_180(
            actual=190,
            infusion_activa=True,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_200_no_entra_en_evaluar_rango_70_180(self):
        resultado = evaluar_rango_70_180(
            actual=200,
            infusion_activa=True,
        )
        self.assertIsNone(resultado)

    def test_con_infusion_en_201_ya_no_es_rango(self):
        resultado = evaluar_rango_70_180(
            actual=201,
            infusion_activa=True,
        )
        self.assertIsNone(resultado)