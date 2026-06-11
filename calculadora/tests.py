from decimal import Decimal

from django.test import TestCase, Client
from django.contrib.auth.models import User

from .utils.resolver import resolver_glucemia
from .utils.logic.logic_hiper import evaluar_hiperglucemia
from .utils.logic.logic_rango import evaluar_rango_70_180
from .utils.helpers import (
    calcular_proximo_control_insulinizado,
    estan_en_mismo_escalon_200_300,
    estan_en_mismo_escalon_300_400,
)
from .utils.ui.presentation import enriquecer_resultado_ui


# =========================================================
# RESOLVER — casos de integración
# =========================================================

class ResolverGlucemiaTest(TestCase):

    def _r(self, actual, previa=None, infusion=False, ajuste=False, tercera=None, algo="1"):
        return resolver_glucemia(
            actual=Decimal(str(actual)),
            previa=Decimal(str(previa)) if previa is not None else None,
            infusion_activa=infusion,
            hubo_ajuste_insulina=ajuste,
            tercera_medicion=Decimal(str(tercera)) if tercera is not None else None,
            algoritmo_activo=algo,
        )

    # --- Hipoglucemia ---

    def test_hipo_severa(self):
        r = self._r(55)
        self.assertEqual(r["estado"], "Hipoglucemia")
        self.assertIn("dextrosa", r.get("conducta", "").lower())

    def test_hipo_limite(self):
        r = self._r(70)
        self.assertIn("estado", r)

    # --- Rango normal ---

    def test_rango_normal_sin_infusion(self):
        r = self._r(120)
        self.assertIn("estado", r)
        self.assertNotEqual(r["estado"], "Hipoglucemia")
        self.assertNotIn("Hiper", r["estado"])

    def test_rango_borde_bajo_sin_infusion(self):
        r = self._r(75)
        self.assertIn("estado", r)
        self.assertEqual(r.get("en_objetivo"), True)

    # --- Hiperglucemia ---

    def test_hiper_sin_infusion_sin_previa(self):
        r = self._r(210)
        self.assertNotEqual(r["estado"], "Hipoglucemia")
        self.assertIsNone(r.get("tasa_algoritmo"))

    def test_hiper_sostenida_sin_infusion_previa_alta(self):
        r = self._r(180, previa=150)
        self.assertIn("estado", r)
        self.assertIsNone(r.get("bolo_inicial"))
        self.assertIsNone(r.get("tasa_inicial"))
        self.assertIsNone(r.get("tasa_algoritmo"))

    def test_hiper_con_infusion_tasa_asignada(self):
        r = self._r(250, previa=250, infusion=True)
        self.assertIsNotNone(r.get("tasa_algoritmo"))
        self.assertIn("UI/h", r["tasa_algoritmo"])

    def test_hiper_critica_sin_infusion(self):
        r = self._r(420)
        self.assertIn("estado", r)

    def test_hiper_con_ajuste_previo_genera_alerta(self):
        r = self._r(250, previa=250, infusion=True, ajuste=True)
        self.assertTrue(r.get("alerta_ajuste_previo"), "Debe marcarse alerta_ajuste_previo")
        self.assertIn("observacion", r)

    def test_hiper_sin_ajuste_no_genera_alerta(self):
        r = self._r(250, previa=250, infusion=True, ajuste=False)
        self.assertFalse(r.get("alerta_ajuste_previo", False))

    # --- Resultado siempre tiene campos mínimos ---

    def test_resultado_siempre_tiene_estado_y_conducta(self):
        casos = [55, 75, 120, 180, 250, 370, 420]
        for v in casos:
            r = self._r(v)
            self.assertIn("estado", r, f"Sin estado para glucemia {v}")
            self.assertIn("conducta", r, f"Sin conducta para glucemia {v}")


# =========================================================
# HIPERGLUCEMIA — lógica interna
# =========================================================

class EvaluarHiperglucemiaTest(TestCase):

    def _h(self, actual, previa=None, infusion=False, ajuste=False, tercera=None, algo=1):
        return evaluar_hiperglucemia(
            actual=Decimal(str(actual)),
            previa=Decimal(str(previa)) if previa is not None else None,
            infusion_activa=infusion,
            hubo_ajuste_insulina=ajuste,
            tercera_medicion=Decimal(str(tercera)) if tercera is not None else None,
            algoritmo_activo=algo,
        )

    def test_360_con_infusion_sin_previa_estado_marcada(self):
        r = self._h(360, infusion=True)
        self.assertEqual(r["estado"], "Hiperglucemia Marcada")

    def test_hiper_300_400_mismo_escalon_pide_tercera(self):
        r = self._h(320, previa=310, infusion=True)
        self.assertTrue(r.get("requiere_tercera_medicion") or r.get("requiere_recontrol"))

    def test_hiper_leve_sin_infusion_retorna_resultado(self):
        r = self._h(200)
        self.assertIn("estado", r)
        self.assertIsNotNone(r)

    def test_resultado_siempre_tiene_estado(self):
        for v in [190, 250, 310, 370, 420]:
            r = self._h(v)
            self.assertIsNotNone(r, f"None para glucemia {v}")
            if r:
                self.assertIn("estado", r, f"Sin estado para glucemia {v}")


# =========================================================
# RANGO 70–180 — lógica interna
# =========================================================

class EvaluarRango70_180Test(TestCase):

    def _rango(self, actual, previa=None, infusion=False, algo="1", horas=None, estable=False):
        return evaluar_rango_70_180(
            actual=Decimal(str(actual)),
            previa=Decimal(str(previa)) if previa is not None else None,
            infusion_activa=infusion,
            algoritmo_activo=algo,
            horas_desde_inicio=horas,
            estable=estable,
        )

    def test_fuera_de_rango_retorna_none(self):
        self.assertIsNone(self._rango(55))
        self.assertIsNone(self._rango(185))

    def test_rango_normal_con_infusion_tiene_tasa(self):
        r = self._rango(120, previa=115, infusion=True)
        self.assertIsNotNone(r)
        self.assertIsNotNone(r.get("tasa_algoritmo"))

    def test_borde_hipo_tiene_alerta(self):
        r = self._rango(75)
        self.assertIsNotNone(r)
        self.assertTrue(r.get("alerta_borde_hipo"))

    def test_objetivo_cumplido(self):
        r = self._rango(120)
        self.assertIsNotNone(r)
        self.assertTrue(r.get("en_objetivo"))

    def test_proximo_control_no_es_vacio(self):
        r = self._rango(120)
        self.assertIsNotNone(r)
        self.assertTrue(r.get("proximo_control"), "proximo_control vacío para glucemia en rango")


# =========================================================
# HELPERS — funciones de escalón y control
# =========================================================

class EscalonTest(TestCase):

    def test_mismo_escalon_200_300_mismo(self):
        self.assertTrue(estan_en_mismo_escalon_200_300(Decimal("210"), Decimal("220")))

    def test_mismo_escalon_200_300_distinto(self):
        self.assertFalse(estan_en_mismo_escalon_200_300(Decimal("205"), Decimal("260")))

    def test_mismo_escalon_200_300_fuera_rango(self):
        self.assertFalse(estan_en_mismo_escalon_200_300(Decimal("150"), Decimal("210")))

    def test_mismo_escalon_200_300_con_none(self):
        self.assertFalse(estan_en_mismo_escalon_200_300(None, Decimal("210")))

    def test_mismo_escalon_300_400_mismo(self):
        self.assertTrue(estan_en_mismo_escalon_300_400(Decimal("310"), Decimal("320")))

    def test_mismo_escalon_300_400_fuera_rango(self):
        self.assertFalse(estan_en_mismo_escalon_300_400(Decimal("250"), Decimal("310")))

    def test_mismo_escalon_300_400_con_none(self):
        self.assertFalse(estan_en_mismo_escalon_300_400(None, None))


class ProximoControlInsulTest(TestCase):

    def _ctrl(self, v):
        return calcular_proximo_control_insulinizado(glicemia=Decimal(str(v)))

    def test_muy_alta_da_1_hora(self):
        r = self._ctrl(410)
        self.assertIn("1 hora", r["proximo_control"])

    def test_rango_120_140_da_2_horas(self):
        r = self._ctrl(130)
        self.assertIn("2 hora", r["proximo_control"])

    def test_alta_da_4_horas(self):
        r = self._ctrl(250)
        self.assertIn("4 hora", r["proximo_control"])

    def test_borde_bajo_da_1_hora(self):
        r = self._ctrl(75)
        self.assertIn("1 hora", r["proximo_control"])

    def test_hipo_da_30_minutos(self):
        r = self._ctrl(65)
        self.assertIn("30 minutos", r["proximo_control"])

    def test_retorna_comentario_control(self):
        r = self._ctrl(150)
        self.assertIn("comentario_control", r)


# =========================================================
# PRESENTATION — enriquecer_resultado_ui
# =========================================================

class EnriquecerResultadoUITest(TestCase):

    def test_no_sobreescribe_tasa_calculada_existente(self):
        resultado = {
            "estado": "En objetivo",
            "tasa_calculada": "1.50",
            "bolo_calculado": "1.50",
        }
        r = enriquecer_resultado_ui(resultado, actual=Decimal("150"), infusion_activa=True)
        self.assertEqual(r["tasa_calculada"], "1.50")
        self.assertEqual(r["bolo_calculado"], "1.50")

    def test_asigna_tasa_si_no_existia(self):
        resultado = {"estado": "En objetivo"}
        r = enriquecer_resultado_ui(resultado, actual=Decimal("200"), infusion_activa=True)
        self.assertIsNotNone(r.get("tasa_calculada"))
        self.assertEqual(r["tasa_calculada"], "2")

    def test_sin_infusion_tasa_calculada_es_vacia(self):
        resultado = {"estado": "En objetivo"}
        r = enriquecer_resultado_ui(resultado, actual=Decimal("120"), infusion_activa=False)
        # sin infusión, el campo se limpia a "" pero no se asigna valor numérico
        self.assertFalse(r.get("tasa_calculada"))


# =========================================================
# VISTAS — smoke tests HTTP
# =========================================================

class VistasSmokeTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="testenfermera", email="test@test.com", password="testpass123"
        )
        self.client = Client()
        self.client.login(username="testenfermera", password="testpass123")

    def test_login_page_accesible(self):
        c = Client()
        resp = c.get("/login/")
        self.assertEqual(resp.status_code, 200)

    def test_home_requiere_login(self):
        c = Client()
        resp = c.get("/")
        self.assertIn(resp.status_code, [302, 403])

    def test_control_glicemia_get(self):
        resp = self.client.get("/")
        self.assertIn(resp.status_code, [200, 302])

    def test_evaluar_glucemia_post_valido(self):
        resp = self.client.post("/", {
            "glicemia_actual": "180",
            "modo": "seguimiento",
            "infusion_activa": "False",
            "hubo_ajuste_insulina": "False",
            "algoritmo_activo": "1",
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_dos_180_sin_infusion_no_da_error_validacion(self):
        """Bug: hubo_ajuste_insulina=false sin infusión no debe generar error de validación."""
        resp = self.client.post("/", {
            "glicemia_actual": "180",
            "glicemia_previa": "180",
            "modo": "seguimiento",
            "infusion_activa": "false",
            "hubo_ajuste_insulina": "false",
            "algoritmo_activo": "1",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "ajuste de insulina solo aplica")

    def test_evaluar_glucemia_post_hipo(self):
        resp = self.client.post("/", {
            "glicemia_actual": "60",
            "modo": "seguimiento",
            "infusion_activa": "False",
            "hubo_ajuste_insulina": "False",
            "algoritmo_activo": "1",
        })
        self.assertIn(resp.status_code, [200, 302])
