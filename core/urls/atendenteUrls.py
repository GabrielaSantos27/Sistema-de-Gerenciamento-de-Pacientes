from django.urls import path
from core.views import AtendenteView
from core.views import Medico_view

urlpatterns = [
    path("", AtendenteView.atendenteView, name='atendente'),
    path("medico/", AtendenteView.atendente_medicoView, name='atendente_medico'),
    path("paciente/", AtendenteView.atendente_pacienteView, name='atendente_paciente'),
    path("cadastro/",AtendenteView.cadastro_atendenteView, name='cadastro_atendente'),
    path("medico/cadastroMedico/", Medico_view.cadastro_MedicoView, name='cadastro_medico'),
    path("paciente/cadastroPaciente/",AtendenteView.cadastro_pacienteView, name='cadastro_paciente'),
    path("medico/cadastroEspecialidade/", AtendenteView.cadastro_especialidadeView, name='cadastro_especialidade'),
    path("filaEspera/",AtendenteView.mostrar_fila_espera, name='atendente_fila_espera'),
    path("relatorio/", AtendenteView.ver_relatorio, name='relatorio'),
    path("paciente/marcarConsulta/", AtendenteView.marcar_consulta, name='atendente_marcar_consulta')
]
