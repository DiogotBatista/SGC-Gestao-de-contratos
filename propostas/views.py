# propostas/views.py

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from core.mixins import AccessRequiredMixin

from .forms import PropostaOrcamentoForm
# from teste_openrouter import response
from .models import PropostaOrcamento


class PropostaListView(AccessRequiredMixin, ListView):
    """
    Lista de propostas de orçamento
    """

    allowed_cargos = []
    view_name = "lista_propostas"
    model = PropostaOrcamento
    template_name = "propostas/lista_propostas.html"
    context_object_name = "propostas"
    ordering = ["-data_alteracao"]
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        q = request.GET.get("q")
        data_inicio = request.GET.get("data_inicio")
        data_fim = request.GET.get("data_fim")
        situacao = request.GET.get("situacao")
        etapa = request.GET.get("etapa")

        if q:
            queryset = queryset.filter(
                Q(contratante__nome__icontains=q) | Q(local_execucao__icontains=q)
            )

        if data_inicio:
            queryset = queryset.filter(data_recebimento__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(data_recebimento__lte=data_fim)

        if situacao:
            queryset = queryset.filter(situacao=situacao)

        if etapa:
            queryset = queryset.filter(etapa_atual=etapa)

        # Ordenação
        sort = request.GET.get("sort", "data_cadastro")
        dir = request.GET.get("dir", "desc")

        # Mapeia os nomes amigáveis para os campos reais
        sort_map = {
            "titulo": "titulo",
            "contratante": "contratante__nome",
            "local": "local_execucao",
            "valor": "valor_estimado",
            "recebido": "data_recebimento",
            "situacao": "situacao",
            "etapa": "etapa_atual",
            "criado": "data_cadastro",
            "atualizado": "data_alteracao",
        }

        sort_field = sort_map.get(sort, "data_cadastro")
        if dir == "desc":
            sort_field = f"-{sort_field}"

        return queryset.order_by(sort_field)


class PropostaCreateView(AccessRequiredMixin, CreateView):
    """
    Cria uma proposta de orçamento
    """

    allowed_cargos = []
    view_name = "criar_proposta"
    model = PropostaOrcamento
    form_class = PropostaOrcamentoForm
    template_name = "propostas/cadastrar_proposta.html"
    success_url = reverse_lazy("lista_propostas")

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Proposta {self.object.titulo} - {self.object.contratante} cadastrada!",
        )
        return response


class PropostaDetailView(AccessRequiredMixin, DetailView):
    """
    Pagina de detalhes de um orçamento
    """

    allowed_cargos = []
    view_name = "detalhe_proposta"
    model = PropostaOrcamento
    template_name = "propostas/detalhe_proposta.html"
    context_object_name = "proposta"


class PropostaUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza uma proposta de orçamento
    """

    allowed_cargos = []
    view_name = "atualizar_proposta"
    model = PropostaOrcamento
    form_class = PropostaOrcamentoForm
    template_name = "propostas/cadastrar_proposta.html"
    success_url = reverse_lazy("lista_propostas")

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.info(
            self.request,
            f"Proposta {self.object.titulo} - {self.object.contratante} atualizada!",
        )
        return response


class PropostaDeleteView(AccessRequiredMixin, DeleteView):
    """
    Exclui uma proposta de orçamento
    """

    allowed_cargos = []
    view_name = "deletar_proposta"
    model = PropostaOrcamento
    template_name = "propostas/confirma_exclusao_proposta.html"
    success_url = reverse_lazy("lista_propostas")

    def form_valid(self, form):
        titulo = self.object.titulo
        contratante = self.object.contratante
        response = super().form_valid(form)
        messages.warning(self.request, f"Proposta {titulo} - {contratante} excluída!")
        return response
