import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

from aplicaciones.cliente.models import Persona
from aplicaciones.cuentas.forms import RegistroForm
import string


# Create your views here.
def generate_secure_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(characters) for _ in range(length))
        if (
                len(password) >= 8 and  # Cumple con la longitud mínima
                any(char.isdigit() for char in password)  # Contiene al menos un carácter numérico
        ):
            return password


def enviar_correo(to_email, subject, message):
    from_email = 'proyectodocap@gmail.com'

    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        fail_silently=False,
    )


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            ci = form.cleaned_data.get('numero_documento')
            email = form.cleaned_data.get('email')

            if Persona.objects.filter(numero_documento=ci).exists():
                form.add_error('Numero de Documento', 'Ya existe una cuenta con ese numero de documento')
            elif Persona.objects.filter(email=email).exists():
                form.add_error('Email', 'Ya existe una cuenta con ese email')
            else:
                user = form.save(commit=False)  # No guardes el usuario en la base de datos todavía
                user.is_staff = False
                user.is_superuser = False
                generated_password = generate_secure_password()  # Genera una contraseña aleatoria
                user.set_password(generated_password)  # Configura la contraseña generada
                user.save()  # Ahora guarda el usuario en la base de datos
                login(request, user)

            # Obtén los datos del usuario
                nombre = form.cleaned_data.get('nombre')
                apellido = form.cleaned_data.get('apellido')
                email = form.cleaned_data.get('email')

            # Envía el correo electrónico
                subject = 'Registro exitoso'
                message = (f'Hola, {nombre} {apellido}!\nTe hemos registrado satisfactoriamente.'
                       f'\nTu id de sesion es tu CI: {user.custom_username}'
                       f'\nTu contraseña generica es: {generated_password}')

                enviar_correo(email, subject, message)

                return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, custom_username=username, password=password)

        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('inicio')  # Redirige al usuario a la vista de cuentas

        else:
            error_message = "Usuario o contraseña incorrectos"
            return render(request, 'registration/login.html', {'error_message': error_message})

    return render(request, 'registration/login.html')


def cerrar_sesion(request):
    logout(request)  # Cierra la sesión del usuario actual
    return redirect('inicio')  # Redirige al usuario a la página de inicio u otra página de tu elección
