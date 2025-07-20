from django.urls import path

from aplicaciones.cliente import views

urlpatterns = [
    path('cuentas/', views.cuentas_page, name='cuentas_page'),
    path('contactos/', views.contactos_page, name='contactos_page'),
    path('transferencias/', views.transferencias_page, name='transferencias_page'),
    path('movimientos/', views.movimientos_page, name='movimientos_page'),
    path('deposito/', views.deposito_page, name='deposito_page'),
    path('retiro/', views.retiro_page, name='retiro_page'),
    path('datos/', views.datos_page, name='datos_page'),
    path('solicitar-cuenta/', views.solicitar_cuenta, name='solicitar_cuenta'),
    path('registrar-contacto/', views.registrar_contacto, name='registrar_contacto'),
    path('eliminar-contacto/<int:nro_cuenta>/', views.eliminar_contacto, name='eliminar-contacto'),
]
