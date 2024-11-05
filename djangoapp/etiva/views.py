# participantes/views.py
from django.shortcuts import render, get_object_or_404
from .models import Participant, Activity
from .forms import ParticipantSearchForm

def participant_card(request, slug):
    participant = get_object_or_404(Participant, slug=slug)
    return render(request, 'etiva/participant_card.html', {'participant': participant})

def activity_list(request):
    activities = []
    form = ParticipantSearchForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            cpf = form.cleaned_data['cpf']

            print('------------')
            print(cpf)
            # Tente buscar o participante pelo email e CPF
            try:
                participant = Participant.objects.get(email=email, cpf=cpf)
                # Obtenha as atividades relacionadas a este participante
                activities = participant.activities.all()  # Supondo que há uma relação ManyToMany com Activities
            except Participant.DoesNotExist:
                form.add_error(None, "Participante não encontrado.")
        else:
            # Aqui, você pode adicionar uma mensagem de erro genérica se o formulário não for válido
            form.add_error(None, "Por favor, corrija os erros no formulário.")

    return render(request, 'etiva/activity_list.html', {'form': form, 'activities': activities})


def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug)  # Busca a atividade pela slug
    return render(request, 'etiva/activity_detail.html', {'activity': activity})