from django.urls import path
from .views import (
    MedicaoListView,
    MedicaoCreateView,
    MedicaoUpdateView,
    MedicaoDeleteView,
    api_powerbi_medicoes,
)

urlpatterns = [
    path('', MedicaoListView.as_view(), name='lista_medicoes'),
    path('nova/', MedicaoCreateView.as_view(), name='criar_medicao'),
    path('<int:pk>/editar/', MedicaoUpdateView.as_view(), name='atualizar_medicao'),
    path('<int:pk>/excluir/', MedicaoDeleteView.as_view(), name='deletar_medicao'),
    path('api/powerbi/medicoes/', api_powerbi_medicoes, name='api_powerbi_medicoes'),
    path('exportar-bi/', api_powerbi_medicoes, name='exportar_bi_alias'),
]
