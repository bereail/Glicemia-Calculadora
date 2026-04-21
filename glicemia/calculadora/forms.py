from django import forms

SI_NO_CHOICES = [
    ("true", "Sí"),
    ("false", "No"),
]

ALGORITMO_CHOICES = [
    ("1", "Algoritmo 1"),
    ("2", "Algoritmo 2"),
]


class GlucemiaForm(forms.Form):
    glicemia_actual = forms.IntegerField(
        label="Glicemia actual",
        required=True,
        min_value=0,
        max_value=999,
        widget=forms.NumberInput(
            attrs={
                "class": "input-control",
                "placeholder": "Ej: 185",
                "id": "id_glicemia_actual",
                "inputmode": "numeric",
                "min": "0",
                "max": "999",
                "step": "1",
            }
        ),
    )

    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa de insulina?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio-inline"}),
        error_messages={
            "required": "Debés indicar si tiene infusión activa.",
            "invalid_choice": "Seleccioná una opción válida.",
        },
    )

    glicemia_previa = forms.IntegerField(
        label="Glicemia previa",
        required=False,
        min_value=0,
        max_value=999,
        widget=forms.NumberInput(
            attrs={
                "class": "input-control",
                "placeholder": "Ej: 160",
                "id": "id_glicemia_previa",
                "inputmode": "numeric",
                "min": "0",
                "max": "999",
                "step": "1",
            }
        ),
    )

    tercera_medicion = forms.IntegerField(
        label="Glicemia anterior",
        required=False,
        min_value=0,
        max_value=999,
        widget=forms.NumberInput(
            attrs={
                "class": "input-control",
                "placeholder": "Ej: 210",
                "id": "id_tercera_medicion",
                "inputmode": "numeric",
                "min": "0",
                "max": "999",
                "step": "1",
            }
        ),
    )

    hubo_ajuste_insulina = forms.ChoiceField(
        label="¿Hubo ajuste de +0,5 UI/h?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio-inline"}),
    )

    algoritmo_activo = forms.ChoiceField(
        label="¿Algoritmo en uso?",
        required=False,
        choices=ALGORITMO_CHOICES,
        initial="1",
        widget=forms.RadioSelect(
            attrs={
                "class": "radio-inline",
                "id": "id_algoritmo_activo",
            }
        ),
    )

    modo = forms.ChoiceField(
        label="Modo",
        required=False,
        choices=(
            ("inicio", "Inicio / Reinicio"),
            ("seguimiento", "Seguimiento"),
        ),
        initial="seguimiento",
        widget=forms.Select(
            attrs={
                "class": "input-control",
                "id": "id_modo",
            }
        ),
    )

    horas_desde_inicio = forms.IntegerField(
        label="Horas desde inicio de insulinización",
        required=False,
        min_value=0,
        max_value=999,
        widget=forms.NumberInput(
            attrs={
                "class": "input-control",
                "placeholder": "Ej: 26",
                "id": "id_horas_desde_inicio",
                "inputmode": "numeric",
                "min": "0",
                "max": "999",
                "step": "1",
            }
        ),
    )

    estable = forms.ChoiceField(
        label="¿Permanece estable?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio-inline"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        actual = cleaned_data.get("glicemia_actual")
        previa = cleaned_data.get("glicemia_previa")
        tercera = cleaned_data.get("tercera_medicion")

        infusion_raw = cleaned_data.get("infusion_activa")
        infusion_activa = None if infusion_raw in (None, "") else infusion_raw == "true"
        cleaned_data["infusion_activa"] = infusion_activa

        ajuste_raw = cleaned_data.get("hubo_ajuste_insulina")
        hubo_ajuste = None if ajuste_raw in (None, "") else ajuste_raw == "true"
        cleaned_data["hubo_ajuste_insulina"] = hubo_ajuste

        estable_raw = cleaned_data.get("estable")
        estable = None if estable_raw in (None, "") else estable_raw == "true"
        cleaned_data["estable"] = estable

        algoritmo_activo = cleaned_data.get("algoritmo_activo") or "1"
        cleaned_data["algoritmo_activo"] = algoritmo_activo

        if actual is None:
            return cleaned_data

        # Hipoglucemia: no pedir más contexto para clasificar
        if actual < 70:
            cleaned_data["glicemia_previa"] = None
            cleaned_data["tercera_medicion"] = None
            cleaned_data["hubo_ajuste_insulina"] = None
            cleaned_data["algoritmo_activo"] = "1"
            cleaned_data["horas_desde_inicio"] = None
            cleaned_data["estable"] = None
            return cleaned_data

        if infusion_activa is None:
            self.add_error("infusion_activa", "Debés indicar si tiene infusión activa.")
            return cleaned_data

        if tercera is not None and previa is None:
            self.add_error(
                "glicemia_previa",
                "Para usar la glicemia anterior, primero debés cargar la glicemia previa.",
            )

        if hubo_ajuste is not None and not infusion_activa:
            self.add_error(
                "hubo_ajuste_insulina",
                "El ajuste de insulina solo aplica si hay infusión activa.",
            )

        # Si hay infusión, la previa es obligatoria
        if infusion_activa and previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa.",
            )

        # Si no hay infusión, limpiar campos que no aplican clínicamente
        if not infusion_activa:
            cleaned_data["hubo_ajuste_insulina"] = None
            cleaned_data["algoritmo_activo"] = "1"
            cleaned_data["horas_desde_inicio"] = None
            cleaned_data["estable"] = None

        # El algoritmo se usa clínicamente con infusión activa.
        # Para cálculo de tasa, recién importa desde 120 mg/dL.
        if infusion_activa and actual < 120:
            cleaned_data["algoritmo_activo"] = "1"

        return cleaned_data