from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from aplicaciones.cliente.models import Ciudad, Persona, Cliente
from aplicaciones.ordenes.models import Equipo


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

class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class PersonaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['email', 'ciudad_id', 'nombre', 'apellido', 'direccion',
                  'celular']


