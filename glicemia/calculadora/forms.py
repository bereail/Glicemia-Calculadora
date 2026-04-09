from django import forms


SI_NO_CHOICES = [
    ("true", "Sí"),
    ("false", "No"),
]


class GlucemiaForm(forms.Form):
    glicemia_actual = forms.DecimalField(
        label="Glicemia actual",
        required=True,
        min_value=0,
        decimal_places=0,
        max_digits=6,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 185",
            "id": "id_glicemia_actual",
            "inputmode": "numeric",
        }),
    )

    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "radio-inline",
        }),
        error_messages={
            "required": "Debés indicar si tiene infusión activa.",
            "invalid_choice": "Seleccione una opción válida.",
        },
    )

    glicemia_previa = forms.DecimalField(
        label="Glicemia previa",
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=6,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 160",
            "id": "id_glicemia_previa",
            "inputmode": "numeric",
        }),
    )

    tercera_medicion = forms.DecimalField(
        label="Glicemia anterior",
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=6,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 210",
            "id": "id_tercera_medicion",
            "inputmode": "numeric",
        }),
    )

    hubo_ajuste_insulina = forms.ChoiceField(
        label="¿Hubo ajuste de insulina?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "radio-inline",
        }),
    )

    modo = forms.ChoiceField(
        label="Modo",
        required=False,
        choices=(
            ("inicio", "Inicio / Reinicio"),
            ("seguimiento", "Seguimiento"),
        ),
        initial="seguimiento",
        widget=forms.Select(attrs={
            "class": "input-control",
            "id": "id_modo",
        }),
    )

    def clean(self):
        cleaned_data = super().clean()

        actual = cleaned_data.get("glicemia_actual")
        previa = cleaned_data.get("glicemia_previa")
        tercera_medicion = cleaned_data.get("tercera_medicion")

        infusion_raw = cleaned_data.get("infusion_activa")
        if infusion_raw in (None, ""):
            infusion_activa = None
        else:
            infusion_activa = infusion_raw == "true"
        cleaned_data["infusion_activa"] = infusion_activa

        ajuste_raw = cleaned_data.get("hubo_ajuste_insulina")
        if ajuste_raw in (None, ""):
            hubo_ajuste_insulina = None
        else:
            hubo_ajuste_insulina = ajuste_raw == "true"
        cleaned_data["hubo_ajuste_insulina"] = hubo_ajuste_insulina

        if actual is None:
            return cleaned_data

        # <= 70: hipoglucemia directa, no pedir nada más
        if actual <= 70:
            return cleaned_data

        # > 70: preguntar infusión sí o sí
        if infusion_activa is None:
            self.add_error(
                "infusion_activa",
                "Debés indicar si tiene infusión activa."
            )
            return cleaned_data

        # Si hay tercera medición, primero debe haber previa
        if tercera_medicion is not None and previa is None:
            self.add_error(
                "glicemia_previa",
                "Para usar la tercera medición, primero necesitás una glicemia previa."
            )

        # Ajuste solo aplica si hay infusión activa
        if hubo_ajuste_insulina is not None and not infusion_activa:
            self.add_error(
                "hubo_ajuste_insulina",
                "El ajuste de insulina solo aplica si hay infusión activa."
            )

        # Con infusión activa, la previa es obligatoria
        if infusion_activa and previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa."
            )

        return cleaned_data


class PasoInicialForm(forms.Form):
    glicemia_actual = forms.IntegerField(
        label="Glicemia actual",
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 180",
            "inputmode": "numeric",
        }),
    )

    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        required=False,
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "radio-inline",
        }),
        error_messages={
            "required": "Debés indicar si tiene infusión activa.",
            "invalid_choice": "Seleccione una opción válida.",
        },
    )

    glicemia_previa = forms.IntegerField(
        label="Glicemia previa",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 160",
            "inputmode": "numeric",
        }),
    )

    def clean(self):
        cleaned_data = super().clean()

        actual = cleaned_data.get("glicemia_actual")
        glicemia_previa = cleaned_data.get("glicemia_previa")

        infusion_raw = cleaned_data.get("infusion_activa")
        if infusion_raw in (None, ""):
            infusion_activa = None
        else:
            infusion_activa = infusion_raw == "true"
        cleaned_data["infusion_activa"] = infusion_activa

        if actual is None:
            return cleaned_data

        if actual <= 70:
            return cleaned_data

        if infusion_activa is None:
            self.add_error(
                "infusion_activa",
                "Debés indicar si tiene infusión activa."
            )
            return cleaned_data

        if infusion_activa and glicemia_previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa."
            )

        return cleaned_data