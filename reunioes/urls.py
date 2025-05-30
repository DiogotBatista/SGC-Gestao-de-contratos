#reunioes/urls.py

from django.urls import path
from .views import (AtaReuniaoCreateView,
                    AtaReuniaoListView,
                    AtaReuniaoDetailView,
                    AtaReuniaoUpdateView,
                    AtaReuniaoDeleteView,
                    AtasAgrupadasView,
                    MenuAtasView,
                    excluir_arquivo_ata,
                    adicionar_arquivos_ata,
                    )

urlpatterns = [
    path('atas/', MenuAtasView.as_view(), name='menu_atas'),
    path('atas/lista/', AtaReuniaoListView.as_view(), name='lista_atas'),
    path('atas/agrupadas/', AtasAgrupadasView.as_view(), name='atas_agrupadas'),
    path('atas/nova/', AtaReuniaoCreateView.as_view(), name='cadastrar_ata'),
    path('atas/<int:pk>/', AtaReuniaoDetailView.as_view(), name='detalhe_ata'),
    path('atas/<int:pk>/editar/', AtaReuniaoUpdateView.as_view(), name='editar_ata'),
    path('atas/<int:pk>/excluir/', AtaReuniaoDeleteView.as_view(), name='excluir_ata'),
    path('excluir-arquivo/<int:pk>/', excluir_arquivo_ata, name='excluir_arquivo_ata'),
    path('adicionar-arquivos/<int:pk>/', adicionar_arquivos_ata, name='adicionar_arquivos_ata'),

]