from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from calculadora.models import MedicionGlucemia


class ExportacionesHistorialTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(name="Enfermeria")
        self.user.groups.add(grupo)

        MedicionGlucemia.objects.create(
            usuario=self.user,
            glucemia_actual=180,
            modo="inicio",
            infusion_activa=True,
            glucemia_previa=170,
            estado="Hiperglucemia",
            clase="hiperglucemia",
            conducta="Ajustar infusión según algoritmo",
            mensaje="Glucemia por encima del objetivo.",
            proximo_control="Cada 4 horas (primeras 24 h) y luego cada 6 h si estable",
            observacion="Evaluar protocolo 2",
            algoritmo_usado="Inicio / Reinicio (Algoritmo 1)",
            velocidad_sugerida="1.5",
            bolo_ui="2",
            tasa_inicial_ui_h="2",
            alerta_hgr=False,
        )

    def test_exportar_excel_requiere_login(self):
        response = self.client.get(reverse("exportar_historial_excel"))
        self.assertEqual(response.status_code, 302)

    def test_exportar_pdf_requiere_login(self):
        response = self.client.get(reverse("exportar_historial_pdf"))
        self.assertEqual(response.status_code, 302)

    def test_exportar_excel_usuario_autorizado(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("exportar_historial_excel"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn(".xlsx", response["Content-Disposition"])

    def test_exportar_pdf_usuario_autorizado(self):
        login_ok = self.client.login(username="testuser", password="12345678")
        self.assertTrue(login_ok)

        response = self.client.get(reverse("exportar_historial_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn(".pdf", response["Content-Disposition"])