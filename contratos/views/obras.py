# contratos/views/obras.py

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from contratos.forms import NotaObraForm, ObraForm
from contratos.models import NotaObra, Obra
from core.mixins import AccessRequiredMixin, ContratoAccessMixin


# VIEWS DAS OBRAS
class ObraListView(AccessRequiredMixin, ListView):
    """
    Lista de obras
    """

    allowed_cargos = []
    view_name = "lista_obras"
    model = Obra
    template_name = "contratos/obras/lista_obras.html"
    context_object_name = "obras"
    paginate_by = 20
    ordering = ["codigo"]

    def get_queryset(self):
        qs = super().get_queryset()

        # ✅ superusuário enxerga todas as obras
        if self.request.user.is_superuser:
            queryset = qs
        else:
            contratos_permitidos = self.request.user.userprofile.contratos.values_list(
                "id", flat=True
            )
            queryset = qs.filter(contrato_id__in=contratos_permitidos)

        # Filtros já existentes
        query = self.request.GET.get("q")
        ativo = self.request.GET.get("ativo")

        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query)
                | Q(contrato__numero__icontains=query)
                | Q(local__icontains=query)
            )
        if ativo == "ativas":
            queryset = queryset.filter(ativo=True)
        elif ativo == "inativas":
            queryset = queryset.filter(ativo=False)

        return queryset


class ObraDetailView(AccessRequiredMixin, ContratoAccessMixin, DetailView):
    """
    Detalher da obra
    """

    allowed_cargos = []
    view_name = "detalhe_obra"
    model = Obra
    template_name = "contratos/obras/detalhes_obra.html"
    context_object_name = "obra"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notas"] = self.object.notas.all()
        context["form_nota"] = NotaObraForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = NotaObraForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.obra = self.object
            nota.autor = request.user
            nota.save()
        return redirect("detalhe_obra", pk=self.object.pk)


class ObraCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastrar nova obra
    """

    allowed_cargos = []
    view_name = "criar_obra"
    no_permission_redirect_url = "lista_obras"
    model = Obra
    form_class = ObraForm
    template_name = "contratos/obras/cadastrar_obra.html"
    success_url = reverse_lazy("lista_obras")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Obra '{self.object.codigo}' cadastrada com sucesso no contrato {self.object.contrato}!",
        )
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ObraUpdateView(AccessRequiredMixin, ContratoAccessMixin, UpdateView):
    """
    Atualizar obra
    """

    allowed_cargos = []
    view_name = "atualizar_obra"
    model = Obra
    form_class = ObraForm
    template_name = "contratos/obras/editar_obra.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.info(
            self.request, f"Obra '{self.object.codigo}' atualizada com sucesso!"
        )
        return response

    def get_success_url(self):
        return reverse_lazy("detalhes_obra", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ObraDeleteView(AccessRequiredMixin, ContratoAccessMixin, DeleteView):
    """
    Deletar obra
    """

    allowed_cargos = []
    view_name = "deletar_obra"
    no_permission_redirect_url = "lista_obras"
    model = Obra
    template_name = "contratos/obras/excluir_obra.html"
    success_url = reverse_lazy("lista_obras")

    def form_valid(self, form):
        obj = self.object
        codigo = obj.codigo
        contrato = obj.contrato
        response = super().form_valid(form)
        messages.warning(
            self.request, f"Obra '{codigo}' removida do contrato {contrato}"
        )
        return response


# Notas na obras
class NotaObraCreateView(AccessRequiredMixin, View):
    """
    Adiciona anotação à obra
    """

    allowed_cargos = []
    view_name = "criar_nota_obra"
    no_permission_redirect_url = "index"

    def post(self, request, obra_id):
        obra = get_object_or_404(Obra, pk=obra_id)
        form = NotaObraForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.obra = obra
            nota.criado_por = request.user
            nota.save()
            messages.success(request, "Anotação adicionada com sucesso!")
        else:
            messages.warning(request, "Erro ao adicionar anotação.")
        return HttpResponseRedirect(
            reverse("detalhes_obra", kwargs={"pk": obra.pk}) + "#anotacoes"
        )


class NotaObraUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza anotação da obra
    """

    allowed_cargos = []
    view_name = "atualizar_obra_nota"
    model = NotaObra
    form_class = NotaObraForm
    template_name = "contratos/obras/editar_nota_obra.html"

    def form_valid(self, form):
        nota = form.save(commit=False)
        nota.save()
        messages.info(self.request, "Anotação atualizada com sucesso!")
        return redirect("detalhes_obra", pk=nota.obra.pk)


class NotaObraDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta anotação da obra
    """

    allowed_cargos = []
    view_name = "deletar_nota_obra"
    model = NotaObra
    template_name = "contratos/obras/excluir_nota_obra.html"

    def get_success_url(self):
        messages.warning(self.request, "Anotação excluída com sucesso!")
        return reverse_lazy("detalhes_obra", kwargs={"pk": self.object.obra.pk})
