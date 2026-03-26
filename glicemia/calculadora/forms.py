from django import forms

SI_NO_CHOICES = [
    ("si", "Sí"),
    ("no", "No"),
]

from django import forms

class GlucemiaForm(forms.Form):
    glicemia_actual = forms.DecimalField(
        label="Glicemia actual",
        min_value=0,
        decimal_places=0,
        max_digits=5,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej: 185",
                "inputmode": "numeric",
                "autocomplete": "off",
                "class": "input-number",
            }
        ),
    )

    paciente_insulinizado = forms.ChoiceField(
        required=True,
        choices=[
            ("", "Seleccionar"),
            ("si", "Sí"),
            ("no", "No"),
        ],
        widget=forms.HiddenInput(),
    )

    glicemia_previa = forms.DecimalField(
        label="Glicemia previa",
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=5,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej: 190",
                "inputmode": "numeric",
                "autocomplete": "off",
                "class": "input-number",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        insulinizado = cleaned_data.get("paciente_insulinizado")
        previa = cleaned_data.get("glicemia_previa")

        if insulinizado not in ["si", "no"]:
            self.add_error(
                "paciente_insulinizado",
                "Debe indicar si el paciente está insulinizado."
            )

        if insulinizado == "si" and previa is None:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si el paciente está insulinizado."
            )

        return cleaned_data

class GlucemiaGuiadaForm(forms.Form):
    glicemia_actual = forms.DecimalField(
        label="Glicemia actual",
        min_value=0,
        decimal_places=0,
        max_digits=5,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 185",
            "inputmode": "numeric",
        })
    )

    insulinizacion_activa = forms.ChoiceField(
        label="Insulinización activa",
        choices=(
            ("", "Seleccionar"),
            ("si", "Sí"),
            ("no", "No"),
        ),
        widget=forms.RadioSelect(attrs={"class": "radio-inline"})
    )

    usar_previa_opcional = forms.BooleanField(
        required=False,
        label="Agregar glicemia previa"
    )

    glicemia_previa = forms.DecimalField(
        label="Glicemia previa",
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=5,
        widget=forms.NumberInput(attrs={
            "class": "input-control",
            "placeholder": "Ej: 160",
            "inputmode": "numeric",
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        insulinizacion = cleaned_data.get("insulinizacion_activa")
        glicemia_previa = cleaned_data.get("glicemia_previa")

        if insulinizacion == "si" and glicemia_previa is None:
            self.add_error("glicemia_previa", "La glicemia previa es obligatoria si hay insulinización activa.")

        return cleaned_data

class PasoInicialForm(forms.Form):
    glicemia_actual = forms.IntegerField(
        label="Glicemia actual",
        min_value=1,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej: 180"
        })
    )

    insulinizado = forms.ChoiceField(
        label="¿Paciente insulinizado?",
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect
    )

    glicemia_previa = forms.IntegerField(
        label="Glicemia previa",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej: 190"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        insulinizado = cleaned_data.get("insulinizado")
        glicemia_previa = cleaned_data.get("glicemia_previa")

        if insulinizado == "si" and not glicemia_previa:
            self.add_error(
                "glicemia_previa",
                "La glicemia previa es obligatoria si el paciente está insulinizado."
            )

        return cleaned_data


class ConfirmarPreviaForm(forms.Form):
    tiene_previa = forms.ChoiceField(
        label="¿Tenés una glicemia previa para comparar?",
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "form-check-input"
        })
    )


class GlicemiaPreviaOpcionalForm(forms.Form):
    glicemia_previa = forms.IntegerField(
        label="Glicemia previa",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 185"
        })
    )


class CriteriosHGPForm(forms.Form):
    ultimo_escalon = forms.ChoiceField(
        label="¿Está en el último escalón?",
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "form-check-input"
        })
    )

    subio_ultimas_2 = forms.ChoiceField(
        label="¿Subió de escalón en las últimas 2 mediciones?",
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "form-check-input"
        })
    )

    mismo_escalon_3_controles = forms.ChoiceField(
        label="¿Permanece en el mismo escalón en 3 controles consecutivos?",
        choices=SI_NO_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "form-check-input"
        })
    )


class AlgoritmoActualForm(forms.Form):
    algoritmo_actual = forms.ChoiceField(
        label="Algoritmo actual",
        choices=[
            ("alg1", "Algoritmo 1"),
            ("alg2", "Algoritmo 2"),
        ],
        widget=forms.RadioSelect(attrs={
            "class": "form-check-input"
        })
    )