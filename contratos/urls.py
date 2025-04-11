from django.urls import path
from .views import (
    MenuView,
    ContratoListView,
    ContratoCreateView,
    ContratoDetailView,
    ContratoUpdateView,
    ContratoDeleteView,
    ContratanteListView,
    ContratanteCreateView,
    ContratanteUpdateView,
    ContratanteDeleteView,
    ObraListView,
    ObraCreateView,
    ObraUpdateView,
    ObraDeleteView,
    ObraDetailView,
    AtasPorContratoView,
    ObrasPorContratoView,
    NotaContratoCreateView,
    NotaContratoUpdateView,
    NotaContratoDeleteView,
)

urlpatterns = [
    #Contratos
    path('contratos/', MenuView.as_view(), name='menu_contratos'),
    path('contratos/lista/', ContratoListView.as_view(), name='lista_contratos'),
    path('contratos/novo/', ContratoCreateView.as_view(), name='criar_contrato'),
    path('contratos/<int:pk>/editar/', ContratoUpdateView.as_view(), name='editar_contrato'),
    path('contratos/<int:pk>/excluir/', ContratoDeleteView.as_view(), name='excluir_contrato'),
    path('contratos/<int:pk>/detalhes/', ContratoDetailView.as_view(), name='detalhes_contrato'),
    path('contrato/<int:pk>/atas/', AtasPorContratoView.as_view(), name='atas_por_contrato'),
    path('contrato/<int:pk>/obras/', ObrasPorContratoView.as_view(), name='obras_por_contrato'),
    path('contratos/<int:contrato_id>/nota/adicionar/', NotaContratoCreateView.as_view(), name='adicionar_nota'),
    path('contratos/nota/<int:pk>/editar/', NotaContratoUpdateView.as_view(), name='editar_nota_contrato'),
    path('contratos/nota/<int:pk>/excluir/', NotaContratoDeleteView.as_view(), name='excluir_nota_contrato'),

    # Obras
    path('obras/lista/', ObraListView.as_view(), name='lista_obras'),
    path('obras/<int:pk>/detalhes/', ObraDetailView.as_view(), name='detalhes_obra'),
    path('obras/novo/', ObraCreateView.as_view(), name='criar_obra'),
    path('obras/<int:pk>/editar/', ObraUpdateView.as_view(), name='editar_obra'),
    path('obras/<int:pk>/excluir/', ObraDeleteView.as_view(), name='excluir_obra'),

    #Contratantes
    path('contratantes/', ContratanteListView.as_view(), name='lista_contratantes'),
    path('contratante/novo/', ContratanteCreateView.as_view(), name='criar_contratante'),
    path('contratante/<int:pk>/editar/', ContratanteUpdateView.as_view(), name='editar_contratante'),
    path('contratante/<int:pk>/excluir/', ContratanteDeleteView.as_view(), name='excluir_contratante'),

    # futuramente: path('contratos/novo/', views.criar_contrato, name='criar_contrato'),
]
