from django.test import SimpleTestCase
from calculadora.forms import GlucemiaForm


class GlucemiaFormTests(SimpleTestCase):
    def test_form_valido_con_actual_e_infusion(self):
        form = GlucemiaForm(data={
            "glicemia_actual": 150,
            "infusion_activa": "no",
        })
        self.assertTrue(form.is_valid())

    def test_form_invalido_sin_glicemia_actual(self):
        form = GlucemiaForm(data={
            "infusion_activa": "no",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("glicemia_actual", form.errors)

    def test_form_invalido_sin_infusion_activa(self):
        form = GlucemiaForm(data={
            "glicemia_actual": 150,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("infusion_activa", form.errors)

    def test_previa_opcional(self):
        form = GlucemiaForm(data={
            "glicemia_actual": 160,
            "infusion_activa": "no",
            "glicemia_previa": "",
        })
        self.assertTrue(form.is_valid())