from django import forms



class PasoInicialForm(forms.Form):
    glucemia_actual = forms.IntegerField(
        label="Glicemia actual",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    glucemia_previa = forms.IntegerField(
        label="Glicemia previa",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )


class InfusionActivaForm(forms.Form):
    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        choices=[
            ("si", "Sí"),
            ("no", "No"),
        ],
        widget=forms.RadioSelect
    )


class AlgoritmoActualForm(forms.Form):
    algoritmo_actual = forms.ChoiceField(
        label="¿Algoritmo actual?",
        choices=[
            ("alg1", "Algoritmo 1"),
            ("alg2", "Algoritmo 2"),
        ],
        widget=forms.RadioSelect
    )


class CriteriosHGPForm(forms.Form):
    ultimo_escalon = forms.ChoiceField(
        label="¿Está en el último escalón?",
        choices=[("si", "Sí"), ("no", "No")],
        widget=forms.RadioSelect
    )
    subio_ultimas_2 = forms.ChoiceField(
        label="¿Subió de escalón en las últimas 2 mediciones?",
        choices=[("si", "Sí"), ("no", "No")],
        widget=forms.RadioSelect
    )
    mismo_escalon_3_controles = forms.ChoiceField(
        label="¿Permanece en el mismo escalón en 3 controles consecutivos?",
        choices=[("si", "Sí"), ("no", "No")],
        widget=forms.RadioSelect
    )


class UltimoEscalonAlg2Form(forms.Form):
    ultimo_escalon = forms.ChoiceField(
        label="¿Está en el último escalón del Algoritmo 2?",
        choices=[("si", "Sí"), ("no", "No")],
        widget=forms.RadioSelect
    )


##################################################################
# 
#     
class CalculadoraGuiadaPaso1Form(forms.Form):
    glucemia_actual = forms.IntegerField(
        label="Glucemia actual (mg/dL)",
        min_value=1
    )
    glucemia_previa = forms.IntegerField(
        label="Glucemia previa (mg/dL)",
        min_value=1
    )

    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        choices=[
            ("", "---------"),
            ("si", "Sí"),
            ("no", "No"),
        ],
        required=False
    )

    algoritmo = forms.ChoiceField(
        label="Algoritmo",
        choices=[
            ("", "---------"),
            ("1", "Algoritmo 1"),
            ("2", "Algoritmo 2"),
        ],
        required=False
    )
    
class GlucemiaForm(forms.Form):
    MODO_CHOICES = [
        ("inicio", "Inicio / Reinicio"),
        ("alg2", "Seguimiento - Algoritmo 2"),
    ]

    SI_NO_CHOICES = [
        ("si", "Sí"),
        ("no", "No"),
    ]

    glucemia = forms.IntegerField(label="Glucemia actual")
    modo = forms.ChoiceField(
        label="Modo",
        choices=MODO_CHOICES
    )
    infusion_activa = forms.ChoiceField(
        label="¿Infusión activa?",
        choices=SI_NO_CHOICES,
        required=False
    )
    glucemia_previa = forms.IntegerField(
        label="Glucemia previa",
        required=False
    )

class GlucemiaGuiadaForm(forms.Form):
    ALGORITMO_CHOICES = (
        ("1", "Algoritmo 1"),
        ("2", "Algoritmo 2"),
    )

    SI_NO_CHOICES = (
        ("si", "Sí"),
        ("no", "No"),
    )

    glicemia_actual = forms.IntegerField(
        label="Glicemia actual (mg/dL)",
        min_value=1
    )
    glicemia_previa = forms.IntegerField(
        label="Glicemia previa (mg/dL)",
        min_value=1
    )

    infusion_activa = forms.ChoiceField(
        label="¿Tiene infusión activa?",
        choices=SI_NO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    algoritmo_actual = forms.ChoiceField(
        label="¿Está en algoritmo 1 o 2?",
        choices=ALGORITMO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    tipo_inicio = forms.ChoiceField(
        label="Tipo",
        choices=(
            ("inicio", "Inicio"),
            ("reinicio", "Reinicio"),
        ),
        required=False,
        widget=forms.RadioSelect
    )

    mismo_escalon_fuera_objetivo = forms.ChoiceField(
        label="¿Hubo 2 controles consecutivos en el mismo escalón y fuera del objetivo?",
        choices=SI_NO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    criterio_hgp_1 = forms.ChoiceField(
        label="¿Está en el último escalón del algoritmo 1 y las 2 últimas mediciones siguen >200 sin cambios?",
        choices=SI_NO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    criterio_hgp_2 = forms.ChoiceField(
        label="¿Permanece en el mismo escalón, >200, en 3 mediciones consecutivas sin cambios?",
        choices=SI_NO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    criterio_hgr = forms.ChoiceField(
        label="¿A pesar de estar en el último escalón del algoritmo 2, las 2 últimas mediciones siguen >360?",
        choices=SI_NO_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )

    def clean(self):
        cleaned_data = super().clean()

        g_actual = cleaned_data.get("glicemia_actual")
        infusion_activa = cleaned_data.get("infusion_activa")
        algoritmo_actual = cleaned_data.get("algoritmo_actual")

        if g_actual is None:
            return cleaned_data

        # Si es >= 120, tiene sentido preguntar por infusión activa
        if g_actual >= 120 and not infusion_activa:
            self.add_error("infusion_activa", "Debés indicar si tiene infusión activa.")

        # Si tiene infusión activa, debe indicar algoritmo
        if infusion_activa == "si" and not algoritmo_actual:
            self.add_error("algoritmo_actual", "Debés indicar si está en algoritmo 1 o 2.")

        return cleaned_data