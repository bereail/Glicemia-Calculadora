from django import forms

MOMENTO_CHOICES = [
    ("", "— Seleccionar (opcional) —"),
    ("ayunas", "Ayunas"),
    ("post", "Postprandial"),
    ("nocturna", "Nocturna"),
]

class GlucemiaForm(forms.Form):
    glucemia = forms.IntegerField(
        label="Glucemia (mg/dL)",
        min_value=20,
        max_value=600,
        widget=forms.NumberInput(attrs={
            "placeholder": "Ej: 140",
            "class": "input",
            "required": True,
        })
    )
    momento = forms.ChoiceField(
        label="Momento (opcional)",
        required=False,
        choices=MOMENTO_CHOICES,
        widget=forms.Select(attrs={"class": "input"})
    )