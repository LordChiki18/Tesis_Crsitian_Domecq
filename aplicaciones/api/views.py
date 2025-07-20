from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from aplicaciones.api.serializers import (CiudadSerializer, PersonaSerializer, ClienteSerializer,
                                          CuentasSerializer, MovimientosSerializer, PersonaUpdateSerializer)
from aplicaciones.cliente.models import Ciudad, Persona, Cliente, Cuentas, Movimientos
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from decimal import InvalidOperation, Decimal


# Create your views here.
class CiudadViews(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CiudadSerializer


class PersonaViews(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = PersonaSerializer


class ClienteViews(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ClienteSerializer


class CuentasViews(viewsets.ModelViewSet):
    queryset = Cuentas.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CuentasSerializer


class MovimientosViews(viewsets.ReadOnlyModelViewSet):
    queryset = Movimientos.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = MovimientosSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'cuenta_id': ['exact'],
    }
    ordering_fields = ['fecha_movimiento', 'monto_movimiento']


class PersonaUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PersonaUpdateSerializer

    def get_object(self):
        # Recupera la persona asociada al usuario autenticado
        return Persona.objects.get(custom_username=self.request.user)

    def perform_update(self, serializer):
        # Realiza la actualización de la persona
        serializer.save()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class TransferenciasViews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nro_cuenta_origen = request.data.get('nro_cuenta_origen')
        nro_cuenta_destino = request.data.get('nro_cuenta_destino')
        monto = request.data.get('monto')

        # Validaciones
        if not all([nro_cuenta_origen, nro_cuenta_destino, monto]):
            return Response({'error': 'La solicitud no contiene los datos necesarios'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            monto = Decimal(monto)
        except InvalidOperation:
            return Response({'error': 'El monto a transferir es inválido'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cuenta_origen = Cuentas.objects.get(nro_cuenta=nro_cuenta_origen)
        except Cuentas.DoesNotExist:
            return Response({'error': 'Cuenta de origen no existe'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cuenta_destino = Cuentas.objects.get(nro_cuenta=nro_cuenta_destino)
        except Cuentas.DoesNotExist:
            return Response({'error': 'Cuenta de destino no existe'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_destino == cuenta_origen:
            return Response({'error': 'La cuenta de destino no puedes ser igual a la de origen'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_origen.estado == 'Bloqueada':
            return Response({'error': 'La cuenta de origen está bloqueada, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_destino.estado == 'Bloqueada':
            return Response({'error': 'La cuenta de destino está bloqueada, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)

        if monto <= 0:
            return Response({'error': 'Monto Invalido'}, status=status.HTTP_400_BAD_REQUEST)

        if cuenta_origen.saldo < monto:
            return Response({'error': 'Saldo Insuficiente'}, status=status.HTTP_400_BAD_REQUEST)

        if cuenta_origen.tipo_cuenta == 'Cuenta Corriente' and cuenta_destino.tipo_cuenta == 'Cuenta de Ahorro':
            return Response({'error': 'La cuenta de destino es de Ahorro, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif cuenta_origen.tipo_cuenta == 'Cuenta de Ahorro' and cuenta_destino.tipo_cuenta == 'Cuenta Corriente':
            return Response({'error': 'La cuenta de destino es Corriente, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_origen.moneda == 'Gs' and cuenta_destino.moneda == 'USD':
            return Response({'error': 'La cuenta de destino esta en Dolares, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif cuenta_origen.moneda == 'USD' and cuenta_destino.moneda == 'Gs':
            return Response({'error': 'La cuenta de destino esta en Guaranies, no se puede realizar la transferencia'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Calcular saldos anteriores y actuales
        saldo_anterior_origen = cuenta_origen.saldo
        saldo_actual_origen = saldo_anterior_origen - monto

        saldo_anterior_destino = cuenta_destino.saldo
        saldo_actual_destino = saldo_anterior_destino + monto

        # Realizar la transferencia
        cuenta_origen.saldo = saldo_actual_origen
        cuenta_destino.saldo = saldo_actual_destino

        cuenta_origen.save()
        cuenta_destino.save()

        # Registrar movimientos
        Movimientos.objects.create(cuenta_id=cuenta_origen,
                                   tipo_movimiento='DEB',
                                   saldo_anterior=saldo_anterior_origen,
                                   saldo_actual=saldo_actual_origen,
                                   monto_movimiento=monto,
                                   cuenta_origen=nro_cuenta_origen,
                                   cuenta_destino=nro_cuenta_destino,
                                   canal='Web')

        Movimientos.objects.create(cuenta_id=cuenta_destino,
                                   tipo_movimiento='CRE',
                                   saldo_anterior=saldo_anterior_destino,
                                   saldo_actual=saldo_actual_destino,
                                   monto_movimiento=monto,
                                   cuenta_origen=nro_cuenta_origen,
                                   cuenta_destino=nro_cuenta_destino,
                                   canal='Web')

        return Response({'message': 'Transferencia realizada con éxito'},
                        status=status.HTTP_200_OK)


class CambiarEstadoCuentaViews(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        nro_cuenta = request.data.get('nro_cuenta')
        estado_nuevo = request.data.get('estado')

        try:
            cuenta = Cuentas.objects.get(nro_cuenta=nro_cuenta)
            cuenta.estado = estado_nuevo
            cuenta.save()
            return Response({'message': f'El estado de la cuenta {nro_cuenta} ha sido cambiado a {estado_nuevo}'},
                            status=status.HTTP_200_OK)
        except Cuentas.DoesNotExist:
            return Response({'error': 'La cuenta no existe'}, status=status.HTTP_404_NOT_FOUND)


class DepositoViews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nro_cuenta_origen = 0
        nro_cuenta_destino = request.data.get('nro_cuenta_destino')
        monto = request.data.get('monto')

        # Validaciones
        if not all([nro_cuenta_destino, monto]):
            return Response({'error': 'La solicitud no contiene los datos necesarios'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            monto = Decimal(monto)
        except InvalidOperation:
            return Response({'error', 'El monto a depositar es inválido'},
                            status=status.HTTP_400_BAD_REQUEST)
        if monto <= 0:
            return Response({'error': 'Monto Invalido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cuenta_destino = Cuentas.objects.get(nro_cuenta=nro_cuenta_destino)
        except Cuentas.DoesNotExist:
            return Response({'error': 'Cuenta de destino no existe'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_destino.estado == 'Bloqueada':
            return Response({'error': 'La cuenta de destino está bloqueada, no se puede realizar el deposito'},
                            status=status.HTTP_400_BAD_REQUEST)

        saldo_anterior_destino = cuenta_destino.saldo
        saldo_actual_destino = saldo_anterior_destino + monto

        # Realizar el deposito
        cuenta_destino.saldo = saldo_actual_destino
        cuenta_destino.save()

        Movimientos.objects.create(cuenta_id=cuenta_destino,
                                   tipo_movimiento='CRE',
                                   saldo_anterior=saldo_anterior_destino,
                                   saldo_actual=saldo_actual_destino,
                                   monto_movimiento=monto,
                                   cuenta_origen=nro_cuenta_origen,
                                   cuenta_destino=nro_cuenta_destino,
                                   canal='Web')

        return Response({'message': 'Deposito realizado con éxito'},
                        status=status.HTTP_200_OK)


class RetiroView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nro_cuenta_origen = request.data.get('nro_cuenta_origen')
        nro_cuenta_destino = 0
        monto = request.data.get('monto')

        # Validaciones
        if not all([nro_cuenta_origen, monto]):
            return Response({'error': 'La solicitud no contiene los datos necesarios'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            monto = Decimal(monto)
        except InvalidOperation:
            return Response({'error', 'El monto a extraer es inválido'},
                            status=status.HTTP_400_BAD_REQUEST)
        if monto <= 0:
            return Response({'error': 'Monto Invalido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cuenta_origen = Cuentas.objects.get(nro_cuenta=nro_cuenta_origen)
        except Cuentas.DoesNotExist:
            return Response({'error': 'Cuenta de origen no existe'},
                            status=status.HTTP_400_BAD_REQUEST)

        if cuenta_origen.estado == 'Bloqueada':
            return Response({'error': 'La cuenta de origen está bloqueada, no se puede realizar la extracción'},
                            status=status.HTTP_400_BAD_REQUEST)

        saldo_anterior_origen = cuenta_origen.saldo
        saldo_actual_origen = saldo_anterior_origen - monto

        # Realizar la extraccion
        cuenta_origen.saldo = saldo_actual_origen

        cuenta_origen.save()

        # Registrar el movimiento
        Movimientos.objects.create(cuenta_id=cuenta_origen,
                                   tipo_movimiento='DEB',
                                   saldo_anterior=saldo_anterior_origen,
                                   saldo_actual=saldo_actual_origen,
                                   monto_movimiento=monto,
                                   cuenta_origen=nro_cuenta_origen,
                                   cuenta_destino=nro_cuenta_destino,
                                   canal='Web')

        return Response({'message': 'Extracción realizada con éxito'},
                        status=status.HTTP_200_OK)
