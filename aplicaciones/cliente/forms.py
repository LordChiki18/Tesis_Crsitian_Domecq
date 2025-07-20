from django import forms
from aplicaciones.cliente.models import Ciudad, Persona, Cuentas, RelacionCliente


class RegistroCuentasForm(forms.ModelForm):
    class Meta:
        model = Cuentas
        fields = (
            'tipo_cuenta', 'moneda', 'saldo'
        )

    def clean_saldo(self):
        saldo = self.cleaned_data['saldo']
        if saldo < 0:
            raise forms.ValidationError("El saldo no puede ser negativo.")
        return saldo


class RegistroContactoForm(forms.ModelForm):
    # para crear formularios usas la class meta

    class Meta:
        model = RelacionCliente
        fields = (
            'nro_cuenta', 'email', 'nombre', 'apellido', 'tipo_documento', 'numero_documento',
        )
