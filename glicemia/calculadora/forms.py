from django import forms


SI_NO_CHOICES = [
    ("si", "Sí"),
    ("no", "No"),
]


class GlucemiaForm(forms.Form):
    """
    Formulario principal para evaluar glucemia.
    """

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

    # 🔴 CAMBIO CLAVE: deja de ser obligatorio SIEMPRE
    infusion_activa = forms.TypedChoiceField(
        label="¿Infusión activa?",
        required=False,
        coerce=lambda x: str(x).lower() in ("true", "1", "si", "sí"),
        choices=(
            ("True", "Sí"),
            ("False", "No"),
        ),
        widget=forms.RadioSelect(attrs={
            "class": "radio-inline",
            "id": "id_infusion_activa",
        }),
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

    hubo_ajuste_insulina = forms.TypedChoiceField(
        label="¿Hubo ajuste de insulina?",
        required=False,
        coerce=lambda x: str(x).lower() in ("true", "1", "si", "sí"),
        choices=(
            ("", "Seleccionar"),
            ("True", "Sí"),
            ("False", "No"),
        ),
        widget=forms.RadioSelect(attrs={
            "class": "radio-inline",
            "id": "id_hubo_ajuste_insulina",
        }),
    )

    tercera_medicion = forms.DecimalField(
        label="Tercera medición",
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
        infusion_activa = cleaned_data.get("infusion_activa")
        tercera_medicion = cleaned_data.get("tercera_medicion")
        hubo_ajuste_insulina = cleaned_data.get("hubo_ajuste_insulina")

        if actual is None:
            return cleaned_data

        # ===============================
        # 🔴 PRIORIDAD ABSOLUTA: HIPOglicemia
        # ===============================
        if actual <= 70:
            # 🔥 No validar nada más
            return cleaned_data

        # ===============================
        # 🔵 VALIDACIONES NORMALES
        # ===============================

        # Si NO es hipo → ahora sí exigir infusión
        if infusion_activa is None:
            self.add_error(
                "infusion_activa",
                "Este campo es obligatorio."
            )
            return cleaned_data

        # Si hay infusión activa → previa obligatoria
        if infusion_activa and previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa."
            )

        # Si se usa tercera → debe haber previa
        if tercera_medicion is not None and previa is None:
            self.add_error(
                "glicemia_previa",
                "Para usar tercera medición, primero necesitás una glicemia previa."
            )

        # Ajuste solo si hay infusión
        if hubo_ajuste_insulina and not infusion_activa:
            self.add_error(
                "hubo_ajuste_insulina",
                "El ajuste de insulina solo aplica si hay infusión activa."
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
        choices=SI_NO_CHOICES,
        required=False,  # 🔴 también opcional acá
        widget=forms.RadioSelect(attrs={"class": "radio-inline"}),
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
        infusion_activa = cleaned_data.get("infusion_activa")
        glicemia_previa = cleaned_data.get("glicemia_previa")

        if actual is None:
            return cleaned_data

        # 🔴 HIPOglicemia → no validar nada
        if actual <= 70:
            return cleaned_data

        # 🔵 Validación normal
        if infusion_activa == "si" and glicemia_previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si hay infusión activa."
            )

        return cleaned_data