from django import forms

MODO_CHOICES = [
    ("inicio", "Inicio / Reinicio"),
    ("alg1", "Seguimiento - Algoritmo 1"),
    ("alg2", "Seguimiento - Algoritmo 2"),
]

INFUSION_CHOICES = [
    ("no", "No"),
    ("si", "Sí"),
]

class GlucemiaForm(forms.Form):
    glucemia = forms.IntegerField(
        min_value=1,
        label="Glucemia actual (mg/dL)",
        widget=forms.NumberInput(attrs={
            "class": "input",
            "placeholder": "Ej: 180"
        })
    )

    glucemia_previa = forms.IntegerField(
        min_value=1,
        required=False,
        label="Glucemia previa (mg/dL)",
        widget=forms.NumberInput(attrs={
            "class": "input",
            "placeholder": "Opcional, ej: 190"
        })
    )

    modo = forms.ChoiceField(
        choices=MODO_CHOICES,
        label="Modo clínico",
        widget=forms.Select(attrs={
            "class": "input"
        })
    )

    infusion_activa = forms.ChoiceField(
        choices=INFUSION_CHOICES,
        label="¿Infusión activa?",
        widget=forms.Select(attrs={
            "class": "input"
        })
    )