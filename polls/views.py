from django.http import HttpResponseRedirect
from .models import Question, Choice, Poll
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import RegisterUserForm, PollForm
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RegisterUser(FormView):
    success_url = reverse_lazy('')
    form_class = RegisterUserForm
    template_name = '../templates/account/signup.html'

    def form_valid(self, form):
        # Create User Account
        password = form.cleaned_data['password1']
        username = form.cleaned_data['email']
        username = username.lower()

        user = User.objects.create_user(username=username,
                                        email=form.cleaned_data['email'],
                                        password=password
                                        )
        # Login User Automatically
        EmailAddress.objects.create(user=user, email=user.email, verified=True,
                                    primary=True)
        user_login = authenticate(self.request, username=username,
                                  password=password)
        login(self.request, user_login)

        return super(RegisterUser,
                     self).form_valid(form)

    def form_invalid(self, form):
        return super(RegisterUser,
                     self).form_invalid(form)


class UserPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('password_change_done')
    template_name = 'account/password_change.html'
    form_class = PasswordChangeForm

    def change_user_password(username, new_password):
        try:
            user = User.objects.get(username=username)
            hashed_password = make_password(new_password)
            user.password = hashed_password
            user.save()
            return True, "Password change successful."
        except User.DoesNotExist:
            return False, "User does not exist."


class UserPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('password_reset_done')
    template_name = 'account/password_reset.html'
    form_class = PasswordResetForm
    email_template_name = 'password_reset_email.html'

    def reset_user_password(username, new_password):
        try:
            user = User.objects.get(username=username)
            hashed_password = make_password(new_password)
            user.password = hashed_password
            user.save()
            return True, "Password reset successful."
        except User.DoesNotExist:
            return False, "User does not exist."


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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["polls"] = Poll.objects.filter(choice__question=self.object)
        return context


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


class PollCreateView(LoginRequiredMixin, CreateView):
    form_class = PollForm
    template_name = 'polls/poll_update.html'

    def get_success_url(self):
        return reverse_lazy('polls:detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'question': self.kwargs.get('pk')})
        return kwargs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["question"] = Question.objects.get(id=self.kwargs.get('pk'))
        return context


class PollUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = PollForm
    template_name = 'polls/poll_update.html'
    model = Poll

    def test_func(self):
        poll = self.get_object()
        return self.request.user == poll.created_by

    def get_success_url(self):
        return reverse_lazy('polls:detail', kwargs={'pk': self.object.choice.question_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'question': self.object.choice.question_id})
        return kwargs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["question"] = Question.objects.get(id=self.object.choice.question_id)
        return context


class PollDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Poll
    success_url = reverse_lazy('index')

    def test_func(self):
        poll = self.get_object()
        return self.request.user == poll.created_by or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["question"] = self.get_object()
        return context


def pollformview(request):
    context = {}
    # create object of form
    form = PollForm(request.POST)
    if form.is_valid():
        # save the form data to model
        form.save()

    context['form'] = form
    return render(request, "polls/poll_update.html", context)