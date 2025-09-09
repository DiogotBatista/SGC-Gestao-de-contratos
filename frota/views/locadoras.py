# frota/views/locadoras.py
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from core.mixins import AccessRequiredMixin

from ..forms import FornecedorForm
from ..models import Fornecedor


class FornecedorListView(AccessRequiredMixin, ListView):
    model = Fornecedor
    template_name = "frota/locadoras/lista_locadoras.html"
    context_object_name = "locadoras"
    paginate_by = 20
    allowed_cargos = []
    view_name = "lista_locadoras"

    def get_queryset(self):
        qs = Fornecedor.objects.all().order_by("nome")
        params = self.request.GET.copy()
        q = (params.get("q") or "").strip()

        if not q:
            ativo = params.get("ativo", "sim")
            if ativo == "nao":
                qs = qs.filter(ativo=False)
            elif ativo == "todos":
                pass
            else:
                qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(nome__icontains=q)

        self.params = params
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["params"] = self.params
        return ctx


class FornecedorCreateView(AccessRequiredMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "frota/locadoras/cadastrar_locadora.html"
    success_url = reverse_lazy("frota:lista_locadoras")
    allowed_cargos = []
    view_name = "cadastrar_locadora"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        messages.success(self.request, "Locadora cadastrada com sucesso!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errs in form.errors.items():
            for e in errs:
                messages.warning(
                    self.request, e if field == "__all__" else f"{field}: {e}"
                )
        return self.render_to_response(self.get_context_data(form=form))


class FornecedorUpdateView(AccessRequiredMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "frota/locadoras/editar_locadora.html"
    success_url = reverse_lazy("frota:lista_locadoras")
    allowed_cargos = []
    view_name = "editar_locadora"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        messages.info(self.request, "Locadora atualizada com sucesso!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errs in form.errors.items():
            for e in errs:
                messages.warning(
                    self.request, e if field == "__all__" else f"{field}: {e}"
                )
        return self.render_to_response(self.get_context_data(form=form))


class FornecedorDesativarView(AccessRequiredMixin, View):
    allowed_cargos = []
    view_name = "desativar_locadora"
    no_permission_redirect_url = "frota:lista_locadoras"

    def post(self, request, pk):
        f = get_object_or_404(Fornecedor, pk=pk, ativo=True)
        f.ativo = False
        f.updated_by = request.user
        f.save(update_fields=["ativo", "updated_by", "data_alteracao"])
        messages.warning(request, f"Locadora {f.nome} desativada.")
        return redirect("frota:lista_locadoras")


class FornecedorReativarView(AccessRequiredMixin, View):
    allowed_cargos = []
    view_name = "reativar_locadora"
    no_permission_redirect_url = "frota:lista_locadoras"

    def post(self, request, pk):
        f = get_object_or_404(Fornecedor, pk=pk, ativo=False)
        f.ativo = True
        f.updated_by = request.user
        f.save(update_fields=["ativo", "updated_by", "data_alteracao"])
        messages.success(request, f"Locadora {f.nome} reativada.")
        return redirect("frota:lista_locadoras")
