from django.test import TestCase
from calculadora.forms import GlucemiaForm


class GlucemiaFormTest(TestCase):

    def _get_valid_choice(self, field_name):
        """
        Devuelve la primera choice válida no vacía del campo.
        Sirve para no adivinar valores como 'si', '1', 'true', etc.
        """
        field = GlucemiaForm().fields[field_name]
        for value, label in field.choices:
            if value not in ("", None):
                return value
        return None

    def test_form_valido_con_datos_minimos(self):
        infusion_choice = self._get_valid_choice("infusion_activa")

        form = GlucemiaForm(data={
            "glucemia": 150,
            "modo": "inicio",
            "infusion_activa": infusion_choice,
        })

        if not form.is_valid():
            print("ERROR FORM MINIMO:", form.errors)

        self.assertTrue(form.is_valid())

    def test_form_invalido_sin_glucemia(self):
        infusion_choice = self._get_valid_choice("infusion_activa")

        form = GlucemiaForm(data={
            "modo": "inicio",
            "infusion_activa": infusion_choice,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("glucemia", form.errors)

    def test_form_invalido_sin_modo(self):
        infusion_choice = self._get_valid_choice("infusion_activa")

        form = GlucemiaForm(data={
            "glucemia": 150,
            "infusion_activa": infusion_choice,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("modo", form.errors)

    def test_form_valido_con_glucemia_previa_en_algoritmo_seguimiento(self):
        infusion_choice = self._get_valid_choice("infusion_activa")

        form = GlucemiaForm(data={
            "glucemia": 220,
            "modo": "alg2",
            "glucemia_previa": 200,
            "infusion_activa": infusion_choice,
        })

        if not form.is_valid():
            print("ERROR FORM ALG2:", form.errors)

        self.assertTrue(form.is_valid())