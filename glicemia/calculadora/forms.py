from django import forms


MODO_CHOICES = [
    ("inicio", "Inicio / Reinicio (Algoritmo 1)"),
    ("alg2", "Seguimiento - Algoritmo 2"),
]

INFUSION_CHOICES = [
    ("no", "No"),
    ("si", "Sí"),
]


class GlucemiaForm(forms.Form):
    glucemia = forms.IntegerField(
        label="Glucemia actual (mg/dL)",
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "Ej: 180",
            }
        ),
        error_messages={
            "required": "Ingresá la glucemia actual.",
            "invalid": "La glucemia debe ser un número entero.",
            "min_value": "La glucemia debe ser mayor a 0.",
            "max_value": "La glucemia no puede ser mayor a 1000 mg/dL.",
        },
    )

    glucemia_previa = forms.IntegerField(
        label="Glucemia previa (mg/dL)",
        required=False,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "Opcional, ej: 190",
            }
        ),
        error_messages={
            "invalid": "La glucemia previa debe ser un número entero.",
            "min_value": "La glucemia previa debe ser mayor a 0.",
            "max_value": "La glucemia previa no puede ser mayor a 1000 mg/dL.",
        },
    )

    modo = forms.ChoiceField(
        label="Modo clínico",
        choices=MODO_CHOICES,
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Seleccioná un modo clínico.",
        },
    )

    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        choices=INFUSION_CHOICES,
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Indicá si la infusión está activa.",
        },
    )

    def clean_glucemia(self):
        g = self.cleaned_data["glucemia"]
        if g <= 0:
            raise forms.ValidationError("La glucemia debe ser mayor a 0.")
        return g

    def clean(self):
        cleaned_data = super().clean()
        g = cleaned_data.get("glucemia")
        previa = cleaned_data.get("glucemia_previa")

        if previa is not None and g is not None:
            if previa == g:
                # No es un error clínico, pero sí una señal. Lo dejamos pasar.
                pass

        return cleaned_data