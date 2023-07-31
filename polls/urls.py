from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('register_user/', views.RegisterUser.as_view(), name='register-user'),
    path('change_password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('reset_password/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('poll/create/<int:pk>/', views.PollCreateView.as_view(), name='poll-create'),
    path('poll/<int:pk>/update/', views.PollUpdateView.as_view(), name='poll-update'),
    path('poll/<int:pk>/delete/', views.PollDeleteView.as_view(), name='poll-delete'),
]