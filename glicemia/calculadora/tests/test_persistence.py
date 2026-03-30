from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from calculadora.forms import GlucemiaForm
from calculadora.models import MedicionGlucemia


class MedicionPersistenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)

    def _get_choice(self, field_name, preferred=None):
        field = GlucemiaForm().fields[field_name]
        choices = [value for value, _label in field.choices if value not in ("", None)]

        if preferred in choices:
            return preferred

        return choices[0] if choices else None

    def test_post_valido_guarda_medicion(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        infusion_choice = self._get_choice("infusion_activa", preferred="si")

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 150,
                "infusion_activa": infusion_choice,
                "glicemia_previa": 140,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MedicionGlucemia.objects.count(), 1)

        medicion = MedicionGlucemia.objects.first()
        self.assertIsNotNone(medicion)

        if hasattr(medicion, "usuario"):
            self.assertEqual(medicion.usuario, self.user)

        if hasattr(medicion, "glicemia_actual"):
            self.assertEqual(medicion.glicemia_actual, 150)

        if hasattr(medicion, "glicemia_previa"):
            self.assertEqual(medicion.glicemia_previa, 140)

    def test_post_invalido_no_guarda_medicion(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        infusion_choice = self._get_choice("infusion_activa", preferred="si")

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 150,
                "infusion_activa": infusion_choice,
                # falta glicemia_previa a propósito
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MedicionGlucemia.objects.count(), 0)

        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertIn("glicemia_previa", form.errors)