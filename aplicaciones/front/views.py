from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def nav_cuentas(request):
    return render(request, 'pages/cuentas_desc.html')


def nav_about(request):
    return render(request, 'pages/about.html')


def nav_contact(request):
    return render(request, 'pages/contact.html')


def foo_policitas(request):
    return render(request, 'pages/politicas.html')


def foo_terminos(request):
    return render(request, 'pages/terminos_condiciones.html')
