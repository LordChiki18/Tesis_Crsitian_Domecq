from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroEquipo, OrdenEquipoForm
from .models import Equipo, OrdenTrabajoManager, OrdenTrabajo
from ..cliente.models import Cliente, Persona

# Funciones
def get_cliente_from_user(user):
    persona = Persona.objects.get(custom_username=user)
    return Cliente.objects.get(persona_id=persona)
# Vistas
# Listar Equipos
@login_required(login_url='login')
def listar_equipos(request):
    equipos_lista  = Equipo.objects.all()
    paginator = Paginator(equipos_lista , 5)

    page_number = request.GET.get('page')
    equipos = paginator.get_page(page_number)

    context = {
        'equipos': equipos,
    }
    return render(request, 'ordenes/lista_equipo.html', context)
# Listar Ordenes
@login_required(login_url='login')
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all()
    context = {
        'ordenes': ordenes
    }
    return render(request, 'ordenes/lista_orden.html', context)
# Registar Equipo/s
@login_required(login_url='login')
def registro_equipo(request):
    if request.method == "POST":
        form = RegistroEquipo(request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            try:

                cliente = get_cliente_from_user(request.user)
                equipo.cliente_id = cliente
                equipo.save()
                messages.success(request, 'Equipo registrado correctamente')
                return redirect('listar_equipos')
            except Cliente.DoesNotExist:
                messages.error(request, 'No se encontro un cliente vinculado al usuario')
        else:
            messages.error(request, 'El registro no es valido, verifique los datos')
    else:
        form = RegistroEquipo()

    return render(request, 'ordenes/equipo_Form.html', context={'form': form})
# Editar Equipo/s
@login_required(login_url='login')
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, pk=id)

    # Verifica si el equipo pertenece al cliente del usuario logueado
    try:
        cliente = get_cliente_from_user(request.user)
        if equipo.cliente_id != cliente:
            messages.error(request, "No tienes permiso para editar este equipo.")
            return redirect('listar_equipos')
    except Cliente.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect('listar_equipos')

    if request.method == "POST":
        form = RegistroEquipo(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipo actualizado correctamente.")
            return redirect('listar_equipos')
        else:
            messages.error(request, "Por favor revisá los datos ingresados.")
    else:
        form = RegistroEquipo(instance=equipo)

    return render(request, 'ordenes/equipo_Form.html', {'form': form, 'editar': True, 'equipo': equipo})
# Crear Orden de Trabajo
@login_required(login_url='login')
def crear_orden_trabajo(request):
    try:
        persona = Persona.objects.get(custom_username=request.user)
        cliente = Cliente.objects.get(persona_id=persona)
    except Cliente.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect('home')

    if request.method == "POST":
        form = OrdenEquipoForm(request.POST)
        form.fields['equipos'].queryset = Equipo.objects.filter(cliente_id=cliente)

        if form.is_valid():
            equipos = form.cleaned_data['equipos']
            observaciones_generales = form.cleaned_data['observaciones']

            equipos_data = [{'equipo': equipo, 'observaciones': observaciones_generales} for equipo in equipos]

            try:
                orden = OrdenTrabajoManager.crear_orden_con_equipos(cliente, equipos_data)
                messages.success(request, f"Orden creada con código {orden.cod_trabajo}")
                return redirect('listar_ordenes')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Revisá los campos del formulario.")
    else:
        form = OrdenEquipoForm()
        form.fields['equipos'].queryset = Equipo.objects.filter(cliente_id=cliente)

    return render(request, 'ordenes/orden_crear.html', {'form': form})
# Ver Equipo
@login_required(login_url='login')
def ver_equipo(request, id):
    equipo = get_object_or_404(Equipo, pk=id)
    orden = OrdenTrabajo.objects.filter(equipos=equipo)
    context = {
        'equipo': equipo,
        'orden': orden,
    }
    return render(request, 'ordenes/ver_equipo.html', context)
# Ver Orden
@login_required(login_url='login')
def ver_orden(request, id):
    return