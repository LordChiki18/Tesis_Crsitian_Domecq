from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from aplicaciones.cliente.models import Ciudad, Persona, Cliente, Cuentas, Movimientos


class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = '__all__'


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

    def create(self, validated_data):
        # Hashea la contraseña antes de guardarla
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class CuentasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuentas
        fields = '__all__'

    def validate_saldo(self, value):
        if value < 0:
            raise serializers.ValidationError("El saldo no puede ser negativo.")
        return value


class MovimientosSerializer(serializers.ModelSerializer):
    saldo_anterior = serializers.FloatField(required=False)
    saldo_actual = serializers.FloatField(required=False)
    monto_movimiento = serializers.FloatField(required=False)
    cuenta_origen = serializers.CharField(required=False)
    cuenta_destino = serializers.CharField(required=False)

    class Meta:
        model = Movimientos
        fields = '__all__'


class PersonaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['email', 'ciudad_id', 'nombre', 'apellido', 'direccion',
                  'celular']
