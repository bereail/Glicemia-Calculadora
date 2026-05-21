from django.test import SimpleTestCase

from calculadora.forms import GlucemiaForm


class GlucemiaFormTests(SimpleTestCase):
    def test_form_valido_con_actual_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glicemia_actual": 100,
                "infusion_activa": "on",
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_valido_con_actual_previa_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glicemia_actual": 55,
                "glicemia_previa": 180,
                "infusion_activa": "on",
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_previa_opcional(self):
        form = GlucemiaForm(
            data={
                "glicemia_actual": 59,
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())
from django.test import TestCase

from calculadora.forms import GlucemiaForm


class GlucemiaFormTests(TestCase):
    def test_form_valido_con_actual_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glicemia_actual": 100,
                "infusion_activa": "true",
                "glicemia_previa": 110,
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_valido_con_actual_previa_e_infusion(self):
        form = GlucemiaForm(
            data={
                "glicemia_actual": 55,
                "glicemia_previa": 180,
                "infusion_activa": "true",
            }
        )
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_invalido_sin_actual(self):
        form = GlucemiaForm(
            data={
                "infusion_activa": "false",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("glicemia_actual", form.errors)