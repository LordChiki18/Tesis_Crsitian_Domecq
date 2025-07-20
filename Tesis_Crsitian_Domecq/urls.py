from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class Protegida(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"content": "Esta vista está protegida"}, status=status.HTTP_200_OK)


urlpatterns = [
    path('', RedirectView.as_view(url='home/', permanent=True)),
    path('home/', include('aplicaciones.front.urls')),
    path('cliente/', include('aplicaciones.cliente.urls')),
    path('cuentas/', include('aplicaciones.cuentas.urls')),
    path('api/', include('aplicaciones.api.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protegida/', Protegida.as_view(), name='protegida'),
    path('admin/', admin.site.urls),
]
