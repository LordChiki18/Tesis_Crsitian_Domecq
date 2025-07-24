from django.urls import path

from aplicaciones.ordenes import views

urlpatterns = [
    # URLS EQUIPOS
    # URL Listar Equipos
    path('equipo/', views.listar_equipos, name='listar_equipos'),
    # URL Ver Equipo
    path('equipo/<int:id>/', views.ver_equipo, name='ver_equipo'),
    # URL Editar Equipo
    path('equipo/<int:id>/edit', views.editar_equipo, name='editar_equipo'),
    # URL Registrar Equipo
    path('registrar_equipo/', views.registro_equipo, name='registro_equipo'),

    # URL ORDENES
    # URL Listar Ordenes
    path('orden/', views.listar_ordenes, name='listar_ordenes'),
    # URL Crear Orden
    path('crear/', views.crear_orden_trabajo, name='crear_orden'),

]
