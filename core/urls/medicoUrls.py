from django.urls import path
from core.views import *

urlpatterns = [
    path('fila/', Medico_view.gerenciar_paciente, name='fila_espera_medico'),
    path('filaEspera/<int:fila_id>/chamar/', Medico_view.remover_paciente, name='chamar_paciente'),
    path('consulta/', Medico_view.realizar_consulta, name='medico_consulta'),
    path('definir_horarios/', Medico_view.definir_horarios, name='medico_definir_horario')
]