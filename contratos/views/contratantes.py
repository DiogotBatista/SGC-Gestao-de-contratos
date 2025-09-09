# contratos/views/contratantes.py

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from contratos.forms import ContratanteForm
from contratos.models import Contratante
from core.mixins import AccessRequiredMixin


# VIEWS DOS CONTRATANTES
class ContratanteListView(AccessRequiredMixin, ListView):
    """
    Lista das empresas contratantes
    """

    allowed_cargos = []
    view_name = "lista_contratantes"
    model = Contratante
    template_name = "contratos/contratantes/lista_contratantes.html"
    context_object_name = "contratantes"
    paginate_by = 20
    ordering = ["nome"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) | Q(cnpj__icontains=query)
            )
        return queryset


class ContratanteCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastro das empresas contratantes
    """

    allowed_cargos = []
    view_name = "criar_contratante"
    no_permission_redirect_url = "lista_contratantes"
    model = Contratante
    form_class = ContratanteForm
    template_name = "contratos/contratantes/cadastrar_contratante.html"
    success_url = reverse_lazy("lista_contratantes")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, f"Empresa {self.object.nome} cadastrada com sucesso!"
        )
        return response


class ContratanteUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualização da empresa contratante
    """

    allowed_cargos = []
    view_name = "atualizar_contratante"
    no_permission_redirect_url = "lista_contratantes"
    model = Contratante
    form_class = ContratanteForm
    template_name = "contratos/contratantes/editar_contratante.html"
    success_url = reverse_lazy("lista_contratantes")

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.info(
            self.request, f"Empresa {self.object.nome} atualizada com sucesso!"
        )
        return response


class ContratanteDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta uma empresa contratante
    """

    allowed_cargos = []
    view_name = "deletar_contratante"
    no_permission_redirect_url = "lista_contratantes"
    model = Contratante
    template_name = "contratos/contratantes/excluir_contratante.html"
    success_url = reverse_lazy("lista_contratantes")

    def form_valid(self, form):
        obj = self.get_object()
        nome = obj.nome
        response = super().form_valid(form)
        messages.warning(self.request, f"Empresa {nome} excluída com sucesso!")
        return response
