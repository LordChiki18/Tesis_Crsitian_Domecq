from django.urls import path

from aplicaciones.front import views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('cuentas/', views.nav_cuentas, name='cuentas_desc'),
    path('about/', views.nav_about, name='about_desc'),
    path('contacto/', views.nav_contact, name='contact_desc'),
    path('politicas/', views.foo_policitas, name='politicas_desc'),
    path('terminos/', views.foo_terminos, name='terminos_desc'),
]
