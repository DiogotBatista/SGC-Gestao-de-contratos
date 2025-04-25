# propostas/views.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from core.mixins import AccessRequiredMixin
from .models import PropostaOrcamento
from .forms import PropostaOrcamentoForm
from django.contrib import messages
from django.db.models import Q

class PropostaListView(AccessRequiredMixin, ListView):
    """
    Lista de propostas de orçamento
    """
    allowed_roles = []
    view_name = 'lista_propostas'
    model = PropostaOrcamento
    template_name = 'propostas/lista_propostas.html'
    context_object_name = 'propostas'
    ordering = ['-data_cadastro']
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q")
        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")
        situacao = self.request.GET.get("situacao")
        etapa = self.request.GET.get("etapa")

        if q:
            queryset = queryset.filter(
                Q(contratante__nome__icontains=q) |
                Q(local_execucao__icontains=q)
            )

        if data_inicio:
            queryset = queryset.filter(data_recebimento__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(data_recebimento__lte=data_fim)

        if situacao:
            queryset = queryset.filter(situacao=situacao)

        if etapa:
            queryset = queryset.filter(etapa_atual=etapa)

        return queryset

class PropostaCreateView(AccessRequiredMixin, CreateView):
    """
    Cria uma proposta de orçamento
    """
    allowed_roles = []
    view_name = 'criar_proposta'
    model = PropostaOrcamento
    form_class = PropostaOrcamentoForm
    template_name = 'propostas/cadastrar_proposta.html'
    success_url = reverse_lazy('lista_propostas')

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        messages.success(self.request, "Proposta cadastrada com sucesso.")
        return super().form_valid(form)

class PropostaDetailView(AccessRequiredMixin, DetailView):
    """
    Pagina de detalhes de um orçamento
    """
    allowed_roles = []
    view_name = 'detalhe_proposta'
    model = PropostaOrcamento
    template_name = 'propostas/detalhe_proposta.html'
    context_object_name = 'proposta'

class PropostaUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza uma proposta de orçamento
    """
    allowed_roles = []
    view_name = 'atualizar_proposta'
    model = PropostaOrcamento
    form_class = PropostaOrcamentoForm
    template_name = 'propostas/cadastrar_proposta.html'
    success_url = reverse_lazy('lista_propostas')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Proposta atualizada com sucesso.")
        return super().form_valid(form)

class PropostaDeleteView(AccessRequiredMixin, DeleteView):
    """
    Exclui uma proposta de orçamento
    """
    allowed_roles = []
    view_name = 'deletar_proposta'
    model = PropostaOrcamento
    template_name = 'propostas/confirma_exclusao_proposta.html'
    success_url = reverse_lazy('lista_propostas')

    def form_valid(self, form):
        messages.success(self.request, "Proposta excluída com sucesso.")
        return super().form_valid(form)

