from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ControlGlicemiaViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_staff=True,          # 👈 CLAVE
            is_superuser=True       # 👈 MÁS SEGURO
        )

        cls.url = reverse("control_glicemia")

    def setUp(self):
        self.client.force_login(self.user)

    def post_data(self, actual, infusion_activa, previa=None, tercera=None):
        data = {
            "glicemia_actual": actual,
            "infusion_activa": infusion_activa,
        }

        if previa is not None:
            data["glicemia_previa"] = previa

        if tercera is not None:
            data["tercera_medicion"] = tercera

        return self.client.post(self.url, data=data, follow=True)

    def test_usuario_autenticado_puede_entrar_a_la_vista(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

def test_get_control_glicemia_responde_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Control de glicemia")

def test_hipoglucemia_directa_actual_menor_o_igual_a_70(self):
        response = self.post_data(
            actual=70,
            infusion_activa="false",
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertIn("hipogluc", contenido)

def test_no_insulinizado_mayor_a_200_no_es_persistente(self):
        response = self.post_data(
            actual=250,
            infusion_activa="false",
            previa=230,
            tercera=220,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertNotIn("persistente", contenido)

def test_insulinizado_tres_glicemias_mismo_escalon_es_persistente(self):
        response = self.post_data(
            actual=250,
            infusion_activa="true",
            previa=240,
            tercera=230,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertIn("persistente", contenido)

def test_insulinizado_tres_glicemias_no_mismo_escalon_no_es_persistente(self):
        response = self.post_data(
            actual=250,
            infusion_activa="true",
            previa=190,
            tercera=230,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertNotIn("persistente", contenido)

def test_insulinizado_mayor_igual_360_con_previa_mayor_igual_360(self):
        response = self.post_data(
            actual=360,
            infusion_activa="true",
            previa=380,
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue(
            "persistente" in contenido
            or "sostenida" in contenido
            or "marcada" in contenido
            or "refractaria" in contenido
            or "fuera de objetivo" in contenido
        )

def test_insulinizado_entre_200_y_360_con_previa_obligatoria_si_falta_da_error(self):
        response = self.post_data(
            actual=250,
            infusion_activa="true",
        )

        self.assertEqual(response.status_code, 200)
        contenido = response.content.decode("utf-8").lower()
        self.assertTrue(
            "previa" in contenido
            or "obligatoria" in contenido
            or "complet" in contenido
            or "error" in contenido
        )
        
def test_en_rango_con_infusion(self):
    response = self.client.post("/", {
        "glicemia_actual": 160,
        "infusion_activa": "true",
    })
    self.assertContains(response, "objetivo")
    
def test_con_infusion_entre_70_y_120_muestra_advertencia(self):
    response = self.client.post("/", {
        "glicemia_actual": 100,
        "infusion_activa": "true",
        "glicemia_previa": 130,
    })
    self.assertContains(response, "cercano a hipoglucemia")


def test_sin_infusion_entre_70_y_90_muestra_advertencia(self):
    response = self.client.post("/", {
        "glicemia_actual": 85,
        "infusion_activa": "false",
    })
    self.assertContains(response, "cercano a hipoglucemia")


def test_hipoglucemia_menor_o_igual_a_70(self):
    response = self.client.post("/", {
        "glicemia_actual": 70,
    })
    self.assertContains(response, "hipoglucemia")   

def test_con_infusion_sin_previa_muestra_error(self):
    response = self.client.post("/", {
        "glicemia_actual": 220,
        "infusion_activa": "true",
    })
    self.assertContains(response, "La glicemia previa es obligatoria")


def test_tercera_sin_previa_muestra_error(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "tercera_medicion": 230,
    })
    self.assertContains(response, "primero necesitás una glicemia previa")
    
def test_sin_infusion_con_previa_baja_y_actual_alta_es_ascenso(self):
    response = self.client.post("/", {
        "glicemia_actual": 190,
        "infusion_activa": "false",
        "glicemia_previa": 150,
    })
    self.assertContains(response, "ascenso")


def test_con_infusion_dos_valores_altos_pero_sin_tercera_no_es_persistente(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 240,
    })
    self.assertContains(response, "obtener tercera medición")
    self.assertNotContains(response, "persistente")


def test_con_infusion_tres_glicemias_no_contiguas_no_es_persistente(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 210,
        "tercera_medicion": 300,
    })
    self.assertNotContains(response, "hiperglucemia persistente")


def test_con_infusion_dos_controles_mayores_iguales_360_es_persistente(self):
    response = self.client.post("/", {
        "glicemia_actual": 380,
        "infusion_activa": "true",
        "glicemia_previa": 370,
    })
    self.assertContains(response, "persistente")
    self.assertContains(response, "algoritmo 2")
    
def test_sin_infusion_una_sola_hiper_es_aislada(self):
    response = self.client.post("/", {
        "glicemia_actual": 185,
        "infusion_activa": "false",
    })
    self.assertContains(response, "aislada")


def test_sin_infusion_dos_hiper_consecutivas_indican_insulinizacion(self):
    response = self.client.post("/", {
        "glicemia_actual": 210,
        "infusion_activa": "false",
        "glicemia_previa": 190,
    })
    self.assertContains(response, "protocolo")
    
def test_con_infusion_y_ajuste_previo_en_mismo_escalon_fuera_objetivo_es_refractaria(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 245,
        "hubo_ajuste_insulina": "true",
    })
    self.assertContains(response, "refractaria")
    self.assertContains(response, "algoritmo 2")


def test_con_infusion_y_ajuste_previo_pero_distinto_escalon_no_es_refractaria(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 180,
        "hubo_ajuste_insulina": "true",
    })
    self.assertNotContains(response, "refractaria")


def test_sin_infusion_y_menor_180_no_muestra_hiperglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 150,
        "infusion_activa": "false",
    })
    self.assertNotContains(response, "hiperglucemia")


def test_con_infusion_y_menor_igual_200_no_muestra_hiperglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 200,
        "infusion_activa": "true",
        "glicemia_previa": 190,
    })
    self.assertNotContains(response, "hiperglucemia persistente")
    self.assertNotContains(response, "hiperglucemia marcada")
def test_hubo_ajuste_sin_infusion_muestra_error_de_formulario(self):
    response = self.client.post("/", {
        "glicemia_actual": 210,
        "infusion_activa": "false",
        "hubo_ajuste_insulina": "true",
    })
    self.assertContains(response, "solo aplica si hay infusión activa")
    
def test_sin_infusion_en_179_no_es_hiperglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 179,
        "infusion_activa": "false",
    })
    self.assertNotContains(response, "hiperglucemia")


def test_sin_infusion_en_180_si_es_hiperglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 180,
        "infusion_activa": "false",
    })
    self.assertContains(response, "hiperglucemia")


def test_con_infusion_en_200_no_es_hiperglucemia_real(self):
    response = self.client.post("/", {
        "glicemia_actual": 200,
        "infusion_activa": "true",
        "glicemia_previa": 180,
    })
    self.assertNotContains(response, "hiperglucemia marcada")
    self.assertNotContains(response, "hiperglucemia persistente")


def test_con_infusion_en_201_si_entra_en_hiperglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 201,
        "infusion_activa": "true",
        "glicemia_previa": 190,
    })
    self.assertContains(response, "hiperglucemia")


def test_con_infusion_359_y_previa_359_no_es_persistente_severa(self):
    response = self.client.post("/", {
        "glicemia_actual": 359,
        "infusion_activa": "true",
        "glicemia_previa": 359,
    })
    self.assertNotContains(response, "persistente severa")


def test_con_infusion_360_y_previa_360_si_es_persistente_severa(self):
    response = self.client.post("/", {
        "glicemia_actual": 360,
        "infusion_activa": "true",
        "glicemia_previa": 360,
    })
    self.assertContains(response, "persistente")
    self.assertContains(response, "algoritmo 2")


def test_en_70_es_hipoglucemia(self):
    response = self.client.post("/", {
        "glicemia_actual": 70,
    })
    self.assertContains(response, "hipoglucemia")


def test_en_71_ya_no_es_hipoglucemia_directa(self):
    response = self.client.post("/", {
        "glicemia_actual": 71,
        "infusion_activa": "false",
    })
    self.assertNotContains(response, "hipoglucemia")
    
def test_infusion_vacia_mayor_70_muestra_error(self):
    response = self.client.post("/", {
        "glicemia_actual": 150,
        "infusion_activa": "",
    })
    self.assertContains(response, "Debés indicar si tiene infusión activa")


def test_actual_vacia_muestra_error(self):
    response = self.client.post("/", {
        "glicemia_actual": "",
        "infusion_activa": "false",
    })
    self.assertContains(response, "Este campo es obligatorio")
    
def test_hiperglucemia_persistente_sugiere_algoritmo_2(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 240,
        "tercera_medicion": 230,
    })
    self.assertContains(response, "algoritmo 2")


def test_hiperglucemia_simple_con_infusion_sugiere_algoritmo_1(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 210,
    })
    self.assertContains(response, "algoritmo 1")


def test_hiperglucemia_persistente_muestra_tasa_de_algoritmo_2(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 240,
        "tercera_medicion": 230,
    })
    self.assertContains(response, "3,5 ui/h")


def test_hiperglucemia_simple_muestra_tasa_de_algoritmo_1(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 210,
    })
    self.assertContains(response, "2,5 ui/h")


def test_dos_mayores_360_muestran_control_segun_protocolo(self):
    response = self.client.post("/", {
        "glicemia_actual": 380,
        "infusion_activa": "true",
        "glicemia_previa": 370,
    })
    self.assertContains(response, "próximo control")


def test_dos_mayores_200_sin_persistencia_piden_tercera_medicion(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 220,
    })
    self.assertContains(response, "obtener tercera medición")
    
def test_resultado_persistente_no_muestra_texto_de_hiperglucemia_aislada(self):
    response = self.client.post("/", {
        "glicemia_actual": 250,
        "infusion_activa": "true",
        "glicemia_previa": 240,
        "tercera_medicion": 230,
    })
    self.assertNotContains(response, "aislada")


def test_resultado_aislada_no_muestra_texto_de_persistente(self):
    response = self.client.post("/", {
        "glicemia_actual": 185,
        "infusion_activa": "false",
    })
    self.assertNotContains(response, "persistente")