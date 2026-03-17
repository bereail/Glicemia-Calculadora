from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group


class HomeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678",
            is_staff=True,
        )
        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)
        self.user_sin_permiso = User.objects.create_user(
            username="sinpermiso",
            password="12345678",
            is_staff=False,
        )

    def test_redirige_si_no_esta_logueado(self):
        response = self.client.get(reverse("home"))
        self.assertIn(response.status_code, [301, 302])

    def test_usuario_logueado_puede_ver_home(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("home"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_usuario_sin_permiso_no_puede_ver_home(self):
        login_ok = self.client.login(username="sinpermiso", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("home"))
        self.assertIn(response.status_code, [301, 302])

    def test_post_valido_devuelve_resultado(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "glucemia": 150,
                "modo": "inicio",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "150")

    def test_post_hipoglucemia(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "glucemia": 60,
                "modo": "inicio",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "60")

    def test_post_glucemia_alta(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "glucemia": 280,
                "modo": "inicio",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "280")

    def test_post_invalido_sin_glucemia(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "modo": "inicio",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

    def test_post_invalido_sin_modo(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.post(
            reverse("home"),
            data={
                "glucemia": 150,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)