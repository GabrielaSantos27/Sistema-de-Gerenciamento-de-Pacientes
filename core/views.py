from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.forms.registroForm import *
from core.models import *
from django.views import View
from django.http import HttpResponse
from datetime import datetime
from django.utils.timezone import now, make_aware, get_current_timezone
from django.views.generic import View
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

class AtendenteView(View):
    def atendenteView(request):
            return render(request, template_name='atendente/atendente.html')

    def atendente_medicoView(request):
            return render(request, template_name='atendente/atendente_medico.html')

    def atendente_pacienteView(request):
            return render (request, template_name='atendente/atendente_paciente.html')


    def cadastro_atendenteView(request):
        if str(request.method) == 'POST':
            atendente_form = AtendenteForm(request.POST)
            usuario_form = UsuarioAtendente(request.POST)

            if atendente_form.is_valid() and usuario_form.is_valid():
                usuario = usuario_form.save(commit=False)
                usuario.save()

                atendente = atendente_form.save(commit=False)
                atendente.usuario = usuario
                atendente.save()
                messages.success(request, 'Cadastro realizado com sucesso.')
                return redirect('cadastro_atendente')
            else:
                messages.error(request, 'Erro ao realizar o cadastro.')
        
        else:
            atendente_form = AtendenteForm()
            usuario_form = UsuarioAtendente()

        context = {
            'atendente_form': atendente_form,
            'usuario_form': usuario_form
        }

        return render(request,'atendente/cadastro_atendente.html', context=context)

    def cadastro_especialidadeView(request):
        if str(request.method) == 'POST':
            especialidade_form = EspecialidadeForm(request.POST)

            if especialidade_form.is_valid():
                especialidade_form.save()
                messages.success(request, 'Cadastro realizado com sucesso.')
                return redirect('cadastro_especialidade')
            else:
                messages.error(request, 'Erro ao realizar o cadastro.')
        
        else:
            especialidade_form = EspecialidadeForm()

        context = {
            'especialidade_form': especialidade_form
        }

        return render(request,'atendente/cadastro_especialidade.html', context=context)


    def mostrar_fila_espera(request):
        if request.method == 'POST':
            fila_espera_form = FilaEsperaForm(request.POST)

            if fila_espera_form.is_valid():
                fila_espera = fila_espera_form.save(commit=False)
                fila_espera.medico = fila_espera.consulta.medico
                fila_espera.paciente = fila_espera.consulta.paciente
                fila_espera.save()
                messages.success(request, 'Inserido na fila.')
                return redirect('atendente_fila_espera')
            else:
                messages.error(request, 'Erro ao inserir na fila de espera.')

        else:
            fila_espera_form = FilaEsperaForm()

        # Preparar contexto com médicos e filas existentes
        medicos = Medico.objects.all()
        contexto = []
        for medico in medicos:
            fila = FilaEspera.objects.filter(medico=medico, estado="Waiting").order_by("created_at")
            contexto.append({"medico": medico, "fila": fila})


        return render(request, 'atendente/filaEspera.html', {
            'contexto': contexto,
            'fila_espera_form': fila_espera_form,
        })


    def inserir_paciente(request):
        medico = get_object_or_404(Medico, id=1)
        paciente = get_object_or_404(Paciente, id=1)
            
        FilaEspera.objects.create(medico=medico, paciente=paciente)

    def cadastro_pacienteView(request):
        if str(request.method) == 'POST':
            paciente_form = PacienteForm(request.POST)
            usuario_form = UsuarioPaciente(request.POST)

            if paciente_form.is_valid() and usuario_form.is_valid():
                usuario = usuario_form.save(commit=False)
                usuario.save()

                paciente = paciente_form.save(commit=False)
                paciente.usuario = usuario
                paciente.save()

                messages.success(request, 'Cadastro realizado com sucesso.')
                return redirect('cadastro_paciente')
            else:
                messages.error(request, 'Erro ao realizar o cadastro.')
        else:
            paciente_form = PacienteForm() 
            usuario_form = UsuarioPaciente()

        context = {
            'paciente_form': paciente_form,
            'usuario_form': usuario_form
        }

        return render(request, 'registro.html', context=context)

    def ver_relatorio(request):
        medicos = Medico.objects.all()
        medicos_dados = []

        for medico in medicos:
            consultas = Consulta.objects.filter(medico=medico)  # Consultas do médico
            pacientes_na_fila = FilaEspera.objects.filter(medico=medico)  # Pacientes na fila de espera

            # Agora, mapear as consultas e a fila de espera
            consultas_e_fila = []
            for consulta in consultas:
                paciente_na_fila = pacientes_na_fila.filter(paciente=consulta.paciente).first()  # Verifica se o paciente está na fila de espera
                consultas_e_fila.append({
                    'consulta': consulta,
                    'updated_at_fila': paciente_na_fila.horario_chamado if paciente_na_fila else None  # Se o paciente estiver na fila, pega o updated_at
                })

            # Adiciona o médico com as consultas e a fila de espera
            medicos_dados.append({
                'medico': medico,
                'consultas_e_fila': consultas_e_fila
            })

        return render(request, 'atendente/medicos_com_consultas_e_fila.html', {
            'medicos_com_dados': medicos_dados,
        })

    def marcar_consulta(request):
        if request.method == "GET":
            especialidades = Especialidade.objects.all()
            context = {
                'especialidades': especialidades
            }
            return render(request, "atendente/atendente_marcar_consulta.html", context=context)

        elif request.method == "POST":
            especialidade_id = request.POST.get("nome")
            paciente_id = request.POST.get("codigo")

            if not Paciente.objects.filter(usuario__codigo=paciente_id).exists():
                messages.error(request, 'O paciente não está cadastrado no sistema')
                return redirect("atendente_marcar_consulta") 

            paciente = Paciente.objects.get(usuario__codigo=paciente_id)
            especialidade = Especialidade.objects.get(id=especialidade_id)
            horarios_disponiveis = HorarioDisponivel.objects.filter(medico__especialidade = especialidade, data_horario__gte=now()).select_related('medico', 'medico__especialidade')
    
                
            context = {
                'especialidade': especialidade,
                'paciente': paciente,
                'horarios_disponiveis': horarios_disponiveis
            }

            if request.POST.get("horario"):
                horario_id = request.POST.get("horario")

                if Consulta.objects.filter(horario_id=horario_id).exists():
                    messages.error(request, 'Este horário já foi marcado.')
                    return redirect("atendente_marcar_consulta") 
                
                horario = HorarioDisponivel.objects.get(id=horario_id)
                medico = horario.medico

                # Criar a consulta
                Consulta.objects.create(paciente=paciente, medico=medico, horario=horario)
                messages.success(request, 'Consulta marcada com sucesso!')
                return redirect("atendente_marcar_consulta") 
            
            return render(request, "atendente/atendente_marcar_consulta_horarios.html", context=context)

          

        
class Fila_EsperaView(View):

    def mostrar_fila_espera(request):
        medico = get_object_or_404(Medico, id=1)
        fila = FilaEspera.objects.filter(medico=medico, estado="Waiting").order_by("created_at")

        return render(request, 'fila_espera.html', {'medico': medico, 'fila': fila}) 

    def inserir_paciente(request):
        medico = get_object_or_404(Medico, id=1)
        paciente = get_object_or_404(Paciente, id=1)
        
        FilaEspera.objects.create(medico=medico, paciente=paciente)

    def remover_paciente(request):
        fila = get_object_or_404(FilaEspera, id=1, estado="Waiting")
        fila.estado = "Attended"
        fila.save()

    def posicao(request):
        paciente = get_object_or_404(Paciente, id=1)
        medico = get_object_or_404(Medico, id=1)
        FilaEspera.objects.filter(medico=medico, estado="Waiting", paciente=paciente).order_by("created_at")

class Home_view(View):
    def home_view(request):
        if request.user.is_authenticated:
            if request.user.tipo == 'paciente':
                return render(request, template_name='paciente/paciente.html')
            elif request.user.tipo == 'medico':
                return render(request, template_name='medico/medico.html')
            elif request.user.tipo == 'atendente':
                return render(request, template_name='atendente/atendenteHome.html')
        else:
            return render(request, template_name='home/home.html')

class Medico_view(View):
   def cadastro_MedicoView(request):
      if str(request.method) == 'POST':
         medico_form = MedicoForm(request.POST)
         usuario_form = UsuarioMedico(request.POST)

         if medico_form.is_valid() and usuario_form.is_valid():
            usuario = usuario_form.save(commit=False)
            usuario.save()

            medico = medico_form.save(commit=False)
            medico.usuario = usuario
            medico.save()
            messages.success(request, 'Cadastro realizado com sucesso.')
            return redirect('cadastro_medico')
         else:
            messages.error(request, 'Erro ao realizar o cadastro.')
   
      else:
         medico_form = MedicoForm()
         usuario_form = UsuarioMedico()

      context = {
         'medico_form': medico_form,
         'usuario_form': usuario_form
      }

      return render(request,'atendente/cadastro_medico.html', context=context)


   def remover_paciente(request, fila_id):
      medico=request.user.medico
      if not FilaEspera.objects.filter(medico=medico, estado="Being_Attended_to").exists():
         fila = get_object_or_404(FilaEspera, id=fila_id, estado="Waiting")
         fila.estado = "Being_Attended_to"
         fila.save()
      return redirect('fila_espera_medico')

   def gerenciar_paciente(request):
      medico=request.user.medico
      fila = FilaEspera.objects.filter(medico=medico, estado="Waiting").order_by("created_at")
      return render(request, 'medico/fila_espera.html', {'fila': fila})

   def realizar_consulta(request):
      medico=request.user.medico
      fila =  FilaEspera.objects.filter(estado="Being_Attended_to").first()

      if (fila==None):
         messages.warning(request, "Nenhum paciente encontrado.")
         return redirect("home")
      
      paciente = fila.paciente
      if str(request.method) == 'POST':
         funcionalidades_consulta = Funcionalidades_de_ConsultaForm(request.POST)
         


         if funcionalidades_consulta.is_valid():
            sintomas_apresentados = funcionalidades_consulta.cleaned_data["sintomas_apresentados"]
            remedio = funcionalidades_consulta.cleaned_data["remedio"]
            dosagem = funcionalidades_consulta.cleaned_data["dosagem"]
            qtd_de_dias  = funcionalidades_consulta.cleaned_data["qtd_de_dias"]
            qtd_por_dia  = funcionalidades_consulta.cleaned_data["qtd_por_dia"]

            # Criar Receita médica
            ReceitaMedica.objects.create(
               medico=medico,
               paciente=paciente,
               sintomas_apresentados=sintomas_apresentados,
               remedio=remedio,
               dosagem=dosagem,
               qtd_de_dias=qtd_de_dias,
               qtd_por_dia= qtd_por_dia                
               )


               # Alterar estado do Paciente
            fila.estado = "Attended"
            fila.horario_chamado = now()
            fila.save()
            
            
            return redirect('home')
         else:
            messages.error(request, 'Erro ao realizar o cadastro.')
   
      else:
         funcionalidades_consulta = Funcionalidades_de_ConsultaForm()

      ficha_medica =  FichaMedica.objects.filter(paciente=paciente).first()
      receitas = ReceitaMedica.objects.filter(paciente=paciente)

      context = {
         'funcionalidades_consulta': funcionalidades_consulta,
         'ficha_medica': ficha_medica,
         'receitas': receitas
      }

      return render(request,'medico/funcionalidades_consulta.html', context=context)

   def definir_horarios(request):
      medico = Medico.objects.get(usuario=request.user)

      if request.method == "POST":
         data_horario = request.POST.get("data_horario")
         # Converter para datetime
         data_horario = datetime.strptime(data_horario, "%Y-%m-%dT%H:%M")
         #data_horario = make_aware(data_horario, get_current_timezone())

         if data_horario >= now():
               HorarioDisponivel.objects.create(medico=medico, data_horario=data_horario)
               return redirect("medico_definir_horario")

      horarios = HorarioDisponivel.objects.filter(medico=medico)
      return render(request, "medico/definir_horarios.html", {"horarios": horarios})

class Paciente_view(View):
    def pacienteRegistro(request):
        if str(request.method) == 'POST':
            paciente_form = PacienteForm(request.POST)
            usuario_form = UsuarioPaciente(request.POST)

            if paciente_form.is_valid() and usuario_form.is_valid():
                usuario = usuario_form.save(commit=False)
                usuario.save()

                paciente = paciente_form.save(commit=False)
                paciente.usuario = usuario
                paciente.save()

                messages.success(request, 'Cadastro realizado com sucesso.')
                return redirect('pacienteRegistro')
            else:
                messages.error(request, 'Erro ao realizar o cadastro.')
        else:
            paciente_form = PacienteForm() 
            usuario_form = UsuarioPaciente()

        context = {
            'paciente_form': paciente_form,
            'usuario_form': usuario_form
        }

        return render(request, 'registro.html', context=context)


    def cadastrar_ficha_medica(request):
        paciente=request.user.paciente
        
        if str(request.method) == 'POST':
                ficha_medica = FichaMedicaForm(request.POST)
            


                if ficha_medica.is_valid():
                    especialidade = ficha_medica.cleaned_data["especialidade"]
                    alergias = ficha_medica.cleaned_data["alergias"]
                    medicamentos_em_uso = ficha_medica.cleaned_data["medicamentos_em_uso"]
                    observacoes = ficha_medica.cleaned_data["observacoes"]
                    

                    FichaMedica.objects.create(
                        especialidade=especialidade,
                        alergias=alergias,
                        medicamentos_em_uso=medicamentos_em_uso,
                        observacoes=observacoes,
                        paciente=paciente
                        )
                    return redirect('home')
                else:
                    messages.error(request, 'Erro ao realizar o cadastro.')
        
        else:
            ficha_medica = FichaMedicaForm()
            

        context = {
            'ficha_medica': ficha_medica
        }

        return render(request,'paciente/ficha_medica.html', context=context)


    def marcar_consulta(request):
        if request.method == "GET":
            especialidades = Especialidade.objects.all()
            context = {
                'especialidades': especialidades
            }
            return render(request, "paciente/marcar_consulta.html", context=context)
        
        elif request.method == "POST":
            especialidade_id = request.POST.get("nome")
            especialidade = Especialidade.objects.get(id=especialidade_id)
            horarios_disponiveis = HorarioDisponivel.objects.filter(medico__especialidade = especialidade, data_horario__gte=now()).select_related('medico', 'medico__especialidade')
                 
            context = {
                'especialidade': especialidade,
                'horarios_disponiveis': horarios_disponiveis
            }

            if request.POST.get("horario"):
                horario_id = request.POST.get("horario")

                if Consulta.objects.filter(horario_id=horario_id).exists():
                    messages.error(request, 'Este horário já foi marcado.')
                    return redirect("atendente_marcar_consulta") 
                
                horario = HorarioDisponivel.objects.get(id=horario_id)
                medico = horario.medico

                # Criar a consulta
                Consulta.objects.create(paciente=request.user.paciente, medico=medico, horario=horario)
                messages.success(request, 'Consulta marcada com sucesso!')
                return redirect("marcar_consulta") 

            
            return render(request, "paciente/marcar_consulta_horario.html", context=context) 


    def historicoPaciente(request):
        paciente = request.user.paciente
        receitas = ReceitaMedica.objects.filter(paciente=paciente)
        consultas = Consulta.objects.filter(paciente=paciente)

        context = {
            'receitas': receitas,
            'consultas': consultas
        }

        return render(request, 'paciente/historico_paciente.html', context=context)

    def gerar_receita(request, receita_id):
        receita = ReceitaMedica.objects.get(id=receita_id)
        paciente = receita.paciente

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receita_{receita.id}.pdf"'

        pdf = canvas.Canvas(response, pagesize=letter)
        logo = "core/static/img/logocuidarmais.jpg"
        pdf.drawImage(logo, 20, 685, width=80, height=80)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(200, 700, 'Receita médica')
        
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(20, 600, f'Nome do paciente: {paciente.usuario.first_name} {paciente.usuario.last_name}')

        pdf.setFont("Helvetica", 12)
        pdf.drawString(20, 530, f'{receita.remedio}')
        pdf.setDash(3,2)
        pdf.line(120, 530, 500, 530)
        pdf.drawString(520, 530, f'{receita.dosagem}')
        pdf.drawString(20,490, f"Tomar {receita.qtd_por_dia} comprimidos, por {receita.qtd_de_dias} dias")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(250,390, f'Dr. {receita.medico.usuario.first_name} {receita.medico.usuario.last_name}') 
        pdf.drawString(250,370, f'CRM: {receita.medico.usuario.codigo}') 

        pdf.showPage()
        pdf.save()

        return response