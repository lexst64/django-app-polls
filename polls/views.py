from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone
from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'all_question_objects'
    extra_context = {
        'waiting_polls_number': len(Question.objects.filter(pub_date__gt=timezone.now()))
    }

    def update_extra_content(self):
        future_polls = Question.objects.filter(pub_date__gt=timezone.now())
        waiting_polls_number = len(future_polls)
        self.extra_context['waiting_polls_number'] = waiting_polls_number

    def get_queryset(self):
        self.update_extra_content()
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def index(request: HttpRequest):
#     context = {'all_question_objects': Question.objects.all()}
#     return render(request, 'polls/index.html', context)
#
#
# def detail(request: HttpRequest, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
#
# def results(request: HttpRequest, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})


def vote(request: HttpRequest, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = Choice.objects.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You didn\'t select a choice.'
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=[question_id]))
