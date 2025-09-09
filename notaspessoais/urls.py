from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotaPessoalListView.as_view(), name="lista_notas"),
    path("nova/", views.NotaPessoalCreateView.as_view(), name="criar_nota"),
    path("<int:pk>/", views.NotaPessoalDetailView.as_view(), name="detalhe_nota"),
    path("<int:pk>/editar/", views.NotaPessoalUpdateView.as_view(), name="editar_nota"),
    path(
        "<int:pk>/excluir/", views.NotaPessoalDeleteView.as_view(), name="excluir_nota"
    ),
]
