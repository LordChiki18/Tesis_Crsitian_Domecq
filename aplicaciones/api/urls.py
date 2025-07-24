from rest_framework.routers import DefaultRouter
from . import views
from aplicaciones.api.views import CiudadViews, PersonaViews, ClienteViews, PersonaUpdateView, EquipoViews
from django.urls import path, include

router = DefaultRouter()

router.register(r'Ciudad', CiudadViews)
router.register(r'Persona', PersonaViews)
router.register(r'Cliente', ClienteViews)
router.register(r'Equipo', EquipoViews)

urlpatterns = [
    path('gestion/', include(router.urls)),

    path('cuenta/update', PersonaUpdateView.as_view(), name='actualizar-persona')
]
