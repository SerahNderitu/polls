
from django import forms
from django.contrib.auth.models import User
from .models import Poll,Choice


class RegisterUserForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        email = self.cleaned_data['email']
        if password1 != password2:
            self.add_error('password1', 'Passwords Not the Same')
            self.add_error('password2', 'Passwords Not the Same')
        if User.objects.filter(email=email).exists():
            User.objects.filter(email=email).delete()
            self.add_error('email', 'Email Already Registered')


class PollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = ['choice', 'comment']

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop("question")
        super().__init__(*args, **kwargs)
        self.fields['choice'] = forms.ModelChoiceField(
            queryset=Choice.objects.filter(question=self.question))


