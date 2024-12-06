from django.urls import path
from core.views import Fila_EsperaView

urlpatterns = [
    path("", Fila_EsperaView.mostrar_fila_espera, name='mostrar_fila_espera')
]