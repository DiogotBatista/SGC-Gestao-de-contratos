from django.urls import path

from .views.alocacoes import AlocacaoListView
from .views.exportacoes import exportar_excel_veiculos
from .views.locadoras import (FornecedorCreateView, FornecedorDesativarView,
                              FornecedorListView, FornecedorReativarView,
                              FornecedorUpdateView)
from .views.veiculos import (VeiculoAlocarView, VeiculoCreateView,
                             VeiculoDeleteView, VeiculoDesativarView,
                             VeiculoDetailView, VeiculoEncerrarAlocacaoView,
                             VeiculoListView, VeiculoReativarView,
                             VeiculoUpdateView)

app_name = "frota"

urlpatterns = [
    # Veículos
    path("veiculos/", VeiculoListView.as_view(), name="lista_veiculos"),
    path("veiculos/cadastrar/", VeiculoCreateView.as_view(), name="cadastrar_veiculo"),
    path("veiculos/<int:pk>/", VeiculoDetailView.as_view(), name="detalhe_veiculo"),
    path(
        "veiculos/<int:pk>/editar/", VeiculoUpdateView.as_view(), name="editar_veiculo"
    ),
    path(
        "veiculos/<int:pk>/excluir/",
        VeiculoDeleteView.as_view(),
        name="excluir_veiculo",
    ),
    # Ações
    path(
        "veiculos/<int:pk>/alocar/", VeiculoAlocarView.as_view(), name="alocar_veiculo"
    ),
    path(
        "veiculos/<int:pk>/encerrar-alocacao/",
        VeiculoEncerrarAlocacaoView.as_view(),
        name="encerrar_alocacao",
    ),
    # Alocações
    path("alocacoes/", AlocacaoListView.as_view(), name="lista_alocacoes"),
    path(
        "veiculos/<int:pk>/encerrar/",
        VeiculoEncerrarAlocacaoView.as_view(),
        name="encerrar_alocacao",
    ),
    path(
        "veiculos/<int:pk>/desativar/",
        VeiculoDesativarView.as_view(),
        name="desativar_veiculo",
    ),
    path(
        "veiculos/<int:pk>/reativar/",
        VeiculoReativarView.as_view(),
        name="reativar_veiculo",
    ),
    # Locadoras
    path("locadoras/", FornecedorListView.as_view(), name="lista_locadoras"),
    path(
        "locadoras/cadastrar/",
        FornecedorCreateView.as_view(),
        name="cadastrar_locadora",
    ),
    path(
        "locadoras/<int:pk>/editar/",
        FornecedorUpdateView.as_view(),
        name="editar_locadora",
    ),
    path(
        "locadoras/<int:pk>/desativar/",
        FornecedorDesativarView.as_view(),
        name="desativar_locadora",
    ),
    path(
        "locadoras/<int:pk>/reativar/",
        FornecedorReativarView.as_view(),
        name="reativar_locadora",
    ),
    # Exportacoes
    path(
        "veiculos/exportar-excel/",
        exportar_excel_veiculos,
        name="exportar_excel_veiculos",
    ),
]
