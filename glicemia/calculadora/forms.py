from django import forms

SI_NO_CHOICES = [
    ("true", "Sí"),
    ("false", "No"),
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
        label="¿Infusión activa?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(
            attrs={"class": "radio-inline"}
        ),
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
        label="¿Hubo ajuste de insulina?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(
            attrs={"class": "radio-inline"}
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

        if actual is None:
          return cleaned_data

        if actual <= 70:
            cleaned_data["glicemia_previa"] = None
            cleaned_data["tercera_medicion"] = None
            cleaned_data["hubo_ajuste_insulina"] = None
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

        if infusion_activa and previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa.",
            )

        return cleaned_data