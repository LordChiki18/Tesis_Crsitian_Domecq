from django import forms
from aplicaciones.ordenes.models import Equipo

class RegistroEquipo(forms.ModelForm):

    class Meta:
        model = Equipo
        fields = ('tipo_equipo', 'marca', 'modelo', 'descripcion_falla', 'potencia_hp_kw', 'voltaje', 'rpm', 'fase')

class OrdenEquipoForm(forms.ModelForm):
    equipos = forms.ModelMultipleChoiceField(
        queryset=Equipo.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Equipos a incluir"
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Observaciones generales (opcional)"
    )

    class Meta:
        model = Equipo
        fields = []

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)

        if cliente:
            self.fields['equipos'].queryset = Equipo.objects.filter(cliente_id=cliente)

    def clean_equipos(self):
        equipos_seleccionados = self.cleaned_data['equipos']
        equipos_con_orden_activa = [equipo for equipo in equipos_seleccionados if equipo.esta_en_orden_activa()]

        if equipos_con_orden_activa:
            nombres = ", ".join(str(equipo) for equipo in equipos_con_orden_activa)
            raise forms.ValidationError(f"Los siguientes equipos ya están en una orden activa: {nombres}")

        return equipos_seleccionados