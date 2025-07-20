from django.urls import path

from aplicaciones.cuentas import views

urlpatterns = [

    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('registro/', views.registro_usuario, name='registro'),
]
