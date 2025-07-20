from rest_framework.routers import DefaultRouter

from aplicaciones.api.views import CiudadViews, PersonaViews, ClienteViews, CuentasViews, TransferenciasViews, \
    CambiarEstadoCuentaViews, DepositoViews, RetiroView, MovimientosViews, \
    PersonaUpdateView
from django.urls import path, include

router = DefaultRouter()

router.register(r'Ciudad', CiudadViews)
router.register(r'Persona', PersonaViews)
router.register(r'Cliente', ClienteViews)
router.register(r'Cuentas', CuentasViews)
router.register(r'Movimientos', MovimientosViews)

urlpatterns = [
    path('gestion/', include(router.urls)),
    path('finanzas/transferencias', TransferenciasViews.as_view(), name='realizar-transferencia'),
    path('finanzas/deposito', DepositoViews.as_view(), name='realizar-deposito'),
    path('finanzas/extraccion', RetiroView.as_view(), name='realizar-retiro'),
    path('cuenta/estado', CambiarEstadoCuentaViews.as_view(), name='cambiar_estado'),
    path('cuenta/update', PersonaUpdateView.as_view(), name='actualizar-persona')
]
