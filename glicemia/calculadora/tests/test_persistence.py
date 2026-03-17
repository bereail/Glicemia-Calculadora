from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.test import TestCase
from calculadora.models import MedicionGlucemia
from calculadora.forms import GlucemiaForm


class MedicionPersistenceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)

    def _get_valid_choice(self, field_name):
        field = GlucemiaForm().fields[field_name]
        for value, label in field.choices:
            if value not in ("", None):
                return value
        return None

    def test_post_valido_guarda_medicion(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        infusion_choice = self._get_valid_choice("infusion_activa")

        response = self.client.post(
            reverse("home"),
            data={
                "glucemia": 150,
                "modo": "inicio",
                "infusion_activa": infusion_choice,
            },
            follow=False
        )

        print("STATUS:", response.status_code)
        if response.status_code in (301, 302):
            print("REDIRECT LOCATION:", response["Location"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MedicionGlucemia.objects.count(), 1)

        medicion = MedicionGlucemia.objects.first()
        self.assertEqual(medicion.usuario, self.user)
        self.assertEqual(medicion.glucemia, 150)
        self.assertEqual(medicion.modo, "inicio")

    def test_post_invalido_no_guarda_medicion(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "modo": "inicio",
            },
            follow=False
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MedicionGlucemia.objects.count(), 0)