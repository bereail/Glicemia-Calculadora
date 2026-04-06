from django.test import SimpleTestCase

from calculadora.forms import GlucemiaForm


class GlucemiaFormTests(SimpleTestCase):
    def test_form_valido_con_actual_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glucemia_actual": 100,
                "infusion_activa": "on",
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_valido_con_actual_previa_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glucemia_actual": 55,
                "glucemia_previa": 180,
                "infusion_activa": "on",
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_previa_opcional(self):
        form = GlucemiaForm(
            data={
                "glucemia_actual": 59,
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())