from django import forms
from aplicaciones.cliente.models import Ciudad, Persona


class RegistroForm(forms.ModelForm):
    ciudad_id = forms.ModelChoiceField(queryset=Ciudad.objects.all(),
                                       widget=forms.Select(attrs={'placeholder': 'Ciudad'}),
                                       empty_label='Seleccione una Ciudad')
    nombre = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellido = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Apellido'}))
    tipo_documento = forms.ChoiceField(choices=(
        ('', 'Tipo de Documento'),
        ('Pasaporte', 'Pasaporte'),
        ('RUC', 'RUC'),
        ('CI', 'CI'),
    ), widget=forms.Select(attrs={'placeholder': 'Tipo de Documento'}))
    numero_documento = forms.CharField(max_length=255,
                                       widget=forms.TextInput(attrs={'placeholder': 'Nro. De Documento'}))
    direccion = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Dirección'}))
    celular = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Celular'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = Persona
        fields = (
            'ciudad_id', 'nombre', 'apellido', 'tipo_documento', 'numero_documento', 'direccion', 'celular', 'email')
