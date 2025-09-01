from django.urls import path
from .views import (
    SenhaListView, SenhaCreateView, SenhaDetailView,
    SenhaUpdateView, SenhaDeleteView, RevelarSenhaView
)

urlpatterns = [
    path('', SenhaListView.as_view(), name='lista_senhas'),
    path('nova/', SenhaCreateView.as_view(), name='cadastrar_senha'),
    path('<int:pk>/', SenhaDetailView.as_view(), name='detalhe_senha'),
    path('<int:pk>/editar/', SenhaUpdateView.as_view(), name='editar_senha'),
    path('<int:pk>/excluir/', SenhaDeleteView.as_view(), name='excluir_senha'),
    path('<int:pk>/revelar/', RevelarSenhaView.as_view(), name='revelar_senha'),
]
