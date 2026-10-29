from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), path('index.html', views.home),
    path('ENEM.html', views.enem, name='enem'), path('exercicio.html', views.exercises, name='exercises'),
    path('tecnicas.html', views.techniques, name='techniques'),
    path('entrar/', views.EnterView.as_view(), name='login'), path('cadastrar/', views.signup, name='signup'),
    path('sair/', views.ExitView.as_view(), name='logout'), path('pesquisa/', views.search, name='search'),
    path('enem/area/<slug:slug>/', views.area, name='area'), path('enem/materia/<slug:slug>/', views.subject, name='subject'),
    path('enem/conteudo/<slug:slug>/', views.topic, name='topic'),
    path('enem/conteudo/<slug:slug>/estudado/', views.mark_studied, name='mark_studied'),
    path('exercicios/conteudo/<slug:slug>/', views.exercise_topic, name='exercise_topic'),
    path('exercicios/conteudo/<slug:slug>/iniciar/', views.start_attempt, name='start_attempt'),
    path('exercicios/tentativa/<int:pk>/', views.attempt, name='attempt'),
    path('organizacao/adicionar/', views.add_plan, name='add_plan'),
    path('organizacao/<int:pk>/', views.update_plan, name='update_plan'),
    path('organizacao/lembretes/', views.reminder_status, name='reminder_status'),
]
