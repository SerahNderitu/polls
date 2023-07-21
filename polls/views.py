from django.http import HttpResponseRedirect
from .models import Question, Choice
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone


class IndexView(generic.ListView):
    # (ListView) a generic view for displaying a list of objects.
    # in this case - a list of recent questions
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'  # pass the list of questions to the template

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]
        #  returns a queryset containing Questions whose pub_date is less than or equal to
        #  that is, earlier than or equal to - timezone.now.


class DetailView(generic.DetailView):
    # (DetailView) a generic view for displaying the details of a single object.
    # in this case - individual question details
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):  # (results of a specific question)
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))