from django.urls import path
from core.views import Paciente_view

urlpatterns = [
    path("", Paciente_view.pacienteRegistro, name='pacienteRegistro'),
    path("ficha_medica/", Paciente_view.cadastrar_ficha_medica, name='cadastrar_ficha_medica'),
    path('marcar_consulta/', Paciente_view.marcar_consulta, name='marcar_consulta'),
    path('historico/', Paciente_view.historicoPaciente, name='historicoPaciente'),
    path('gerar_pdf/<int:receita_id>/', Paciente_view.gerar_receita, name='receita')
]