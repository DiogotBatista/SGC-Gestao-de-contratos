from django.urls import path
from . import views

urlpatterns = [
    path('', views.PropostaListView.as_view(), name='lista_propostas'),
    path('nova/', views.PropostaCreateView.as_view(), name='cadastrar_proposta'),
    path('<int:pk>/', views.PropostaDetailView.as_view(), name='detalhe_proposta'),
    path('<int:pk>/editar/', views.PropostaUpdateView.as_view(), name='editar_proposta'),
    path('<int:pk>/excluir/', views.PropostaDeleteView.as_view(), name='excluir_proposta'),
]
