from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from aplicaciones.cliente.forms import RegistroContactoForm, RegistroCuentasForm
from aplicaciones.cliente.models import Persona, Cliente, Cuentas, RelacionCliente, Movimientos
from datetime import datetime


# Create your views here.
@login_required
def cuentas_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=persona)
    cuenta = Cuentas.objects.filter(cliente_id=cliente)

    context = {
        'persona': persona,
        'cliente': cliente,
        'cuentas': cuenta,
    }

    return render(request, 'clients/cuentas.html', context)


@login_required
def transferencias_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=persona)
    listaCliente = RelacionCliente.objects.filter(cliente_propietario=cliente)
    cuenta = Cuentas.objects.filter(cliente_id=cliente)

    context = {
        'persona': persona,
        'cliente': cliente,
        'relacion': listaCliente,
        'cuenta': cuenta
    }
    return render(request, 'clients/transferencias.html', context)


@login_required
def deposito_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=persona)
    cuenta = Cuentas.objects.filter(cliente_id=cliente)

    context = {
        'persona': persona,
        'cliente': cliente,
        'cuenta': cuenta
    }
    return render(request, 'clients/deposito.html', context)


@login_required
def retiro_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=persona)
    cuenta = Cuentas.objects.filter(cliente_id=cliente)

    context = {
        'persona': persona,
        'cliente': cliente,
        'cuenta': cuenta
    }
    return render(request, 'clients/retiro.html', context)


@login_required
def contactos_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=request.user)
    contactos = RelacionCliente.objects.filter(cliente_propietario=cliente)
    cuentacontacto = Cuentas.objects.filter(cliente_id=cliente)

    context = {
        'persona': persona,
        'cliente': cliente,
        'contactos': contactos,
        'cuentacontacto': cuentacontacto,
    }

    return render(request, 'clients/contactos.html', context)


@login_required
def movimientos_page(request):
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    # Obtén todas las cuentas del usuario
    persona = Persona.objects.get(custom_username=request.user)
    cliente = Cliente.objects.get(persona_id=persona)
    cuentas = Cuentas.objects.filter(cliente_id=cliente)

    # Inicializa la consulta para obtener los movimientos
    movimientos = Movimientos.objects.filter(cuenta_id__in=cuentas)

    if fecha_desde:
        # Analiza la fecha desde la entrada
        fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%dT%H:%M")
        movimientos = movimientos.filter(fecha_movimiento__gte=fecha_desde)

    if fecha_hasta:
        # Analiza la fecha hasta la entrada
        fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%dT%H:%M")
        movimientos = movimientos.filter(fecha_movimiento__lte=fecha_hasta)

    context = {
        'persona': persona,
        'cliente': cliente,
        'movimientos': movimientos,
    }
    return render(request, 'clients/movimientos.html', context)


@login_required
def datos_page(request):
    persona = Persona.objects.get(custom_username=request.user)
    context = {
        'persona': persona
    }
    return render(request, 'clients/datos.html', context)


@login_required
def solicitar_cuenta(request):
    if request.method == 'POST':
        form = RegistroCuentasForm(request.POST)
        if form.is_valid():
            saldo = form.cleaned_data['saldo']
            if saldo < 0:
                return HttpResponse("El saldo no puede ser negativo.")

            cuenta = form.save(commit=False)

            cliente, creado = Cliente.objects.get_or_create(persona_id=request.user)

            # Asigna el cliente a la cuenta
            cuenta.cliente_id = cliente

            # Guarda la cuenta en la base de datos
            cuenta.save()

            return redirect('cuentas_page')
    else:
        form = RegistroCuentasForm()

    return render(request, 'registration/registro_cuentas.html', {'form': form})


@login_required
def registrar_contacto(request):
    if request.method == 'POST':
        form = RegistroContactoForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            nro_cuenta = cleaned_data['nro_cuenta']
            tipo_documento = cleaned_data['tipo_documento']
            numero_documento = cleaned_data['numero_documento']
            email = cleaned_data['email']

            try:
                persona = Persona.objects.get(
                    email=email,
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento
                )

                try:
                    cliente_propietario = Cliente.objects.get(persona_id=request.user)
                    cliente_registrado = Cliente.objects.get(persona_id=persona)
                    cuentas = Cuentas.objects.get(cliente_id=cliente_registrado, nro_cuenta=nro_cuenta)
                    tipo_cuenta = cuentas.tipo_cuenta
                    nro_cuenta = cuentas.nro_cuenta
                    moneda = cuentas.moneda
                    # Si la cuenta existe y coincide, procede
                    contacto = form.save(commit=False)
                    contacto.cliente_propietario = cliente_propietario
                    contacto.cliente_registrado = cliente_registrado
                    contacto.tipo_cuenta = tipo_cuenta
                    contacto.nro_cuenta = nro_cuenta
                    contacto.moneda = moneda
                    contacto.save()

                    return JsonResponse({'success': True})

                except Cuentas.DoesNotExist:
                    # Si la cuenta no coincide, muestra un mensaje de error
                    return JsonResponse({'success': False, 'error': "La cuenta no existe..."})

            except Persona.DoesNotExist:
                # Si la persona no existe, muestra un mensaje de error
                return JsonResponse({'success': False, 'error': "La persona no existe..."})

        else:
            # Si el formulario no es válido, muestra un mensaje de error con los detalles de validación
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})

    form = RegistroContactoForm()
    return render(request, 'registration/registro_contacto.html', {'form': form})


@login_required
def eliminar_contacto(request, nro_cuenta):
    if request.method == 'POST':
        try:
            # Obtener el contacto
            contacto = RelacionCliente.objects.get(nro_cuenta=nro_cuenta)
            cliente = Cliente.objects.get(persona_id=request.user)

            print(contacto.cliente_propietario)
            print(cliente)

            # Verificar si el contacto pertenece al usuario actual
            if contacto.cliente_propietario == cliente:
                contacto.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este contacto.'})

        except RelacionCliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El contacto no existe.'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido.'})
