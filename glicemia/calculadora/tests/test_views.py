from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class ControlGlicemiaViewTests(TestCase):
    VALOR_SI = "True"
    VALOR_NO = "False"

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)

    def login(self):
        login_ok = self.client.login(username="admin", password="1234")
        self.assertTrue(login_ok)

    def _contenido(self, response):
        return response.content.decode("utf-8").lower()

    def test_redirect_si_no_esta_logueado(self):
        response = self.client.get(reverse("control_glicemia"))
        self.assertIn(response.status_code, [301, 302])

    def test_get_ok_si_esta_logueado(self):
        self.login()
        response = self.client.get(reverse("control_glicemia"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Control de glicemia")

    def test_post_hipoglucemia_sin_infusion(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 65,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("hipogluc", contenido)

    def test_post_actual_70_tambien_es_hipoglucemia(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 70,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("hipogluc", contenido)

    def test_en_rango_sin_infusion_y_sin_previa(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 120,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertTrue("rango" in contenido or "objetivo" in contenido)

    def test_en_rango_sin_infusion_con_previa(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 150,
                "glicemia_previa": 140,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertTrue("rango" in contenido or "objetivo" in contenido)

    def test_hiperglucemia_sin_infusion_con_previa_alta(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 210,
                "glicemia_previa": 190,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("hipergluc", contenido)

    def test_con_infusion_y_previa_valida(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 180,
                "glicemia_previa": 170,
                "infusion_activa": self.VALOR_SI,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("resultado", contenido)

    def test_con_infusion_sin_previa_es_invalido(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 180,
                "infusion_activa": self.VALOR_SI,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertIn("glicemia_previa", form.errors)

    def test_con_infusion_y_ajuste_no_con_tercera_medicion(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 220,
                "glicemia_previa": 210,
                "infusion_activa": self.VALOR_SI,
                "hubo_ajuste_insulina": self.VALOR_NO,
                "tercera_medicion": 230,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("resultado", contenido)

    def test_post_valido_guarda_y_muestra_resultado(self):
        self.login()

        response = self.client.post(
            reverse("control_glicemia"),
            data={
                "glicemia_actual": 190,
                "glicemia_previa": 185,
                "infusion_activa": self.VALOR_NO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        contenido = self._contenido(response)
        self.assertIn("resultado", contenido)
