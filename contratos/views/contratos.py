# contratos/views/contratos.py
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, View)

from contratos.forms import ContratoForm, NotaContratoForm
from contratos.models import Contrato, NotaContrato, Obra
from core.mixins import AccessRequiredMixin, ContratoAccessMixin
from medicoes.models import Medicao
from reunioes.models import AtaReuniao, ItemAta


# MENU
class MenuView(AccessRequiredMixin, TemplateView):
    """
    Pagina principal de contratos
    """

    allowed_cargos = []
    template_name = "contratos/menu_contratos.html"
    view_name = "menu_contratos"


# VIEWS DOS CONTRATOS
class ContratoListView(AccessRequiredMixin, ListView):
    """
    Lista de contratos
    """

    allowed_cargos = []
    view_name = "lista_contratos"
    model = Contrato
    template_name = "contratos/contratos/lista_contratos.html"
    context_object_name = "contratos"
    paginate_by = 20
    ordering = ["-data_cadastro"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Contrato.objects.all()
        else:
            queryset = self.request.user.userprofile.contratos.all()

        query = self.request.GET.get("q")
        ativo = self.request.GET.get("ativo")

        if query:
            queryset = queryset.filter(
                Q(numero__icontains=query) | Q(contratante__nome__icontains=query)
            )

        if ativo == "ativos":
            queryset = queryset.filter(ativo=True)
        elif ativo == "inativos":
            queryset = queryset.filter(ativo=False)

        return queryset


class ContratoCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastrar novo contrato
    """

    allowed_cargos = []
    view_name = "criar_contratos"
    no_permission_redirect_url = "lista_contratos"
    model = Contrato
    form_class = ContratoForm
    template_name = "contratos/contratos/cadastrar_contrato.html"
    success_url = reverse_lazy("lista_contratos")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Contrato {self.object.numero} – {self.object.contratante.nome} cadastrado com sucesso!",
        )
        return response


class ContratoDetailView(AccessRequiredMixin, ContratoAccessMixin, DetailView):
    """
    Detalhes de um contrato específico
    """

    model = Contrato
    template_name = "contratos/contratos/detalhes_contrato.html"
    context_object_name = "contrato"
    allowed_cargos = []
    view_name = "detalhe_contrato"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato = self.object

        atas = AtaReuniao.objects.filter(contrato=contrato).prefetch_related("itens")
        total_atas = atas.count()
        total_itens = ItemAta.objects.filter(ata__contrato=contrato).count()
        pendentes = ItemAta.objects.filter(
            ata__contrato=contrato, status="pendente"
        ).count()
        concluidos = ItemAta.objects.filter(
            ata__contrato=contrato, status="concluido"
        ).count()
        medicoes = Medicao.objects.filter(contrato=contrato).order_by("-criado_em")
        total_medicoes = medicoes.aggregate(total=Sum("valor"))["total"] or 0
        ultima_ata = atas.order_by("-data").first()

        context.update(
            {
                "total_atas": total_atas,
                "total_itens": total_itens,
                "pendentes": pendentes,
                "concluidos": concluidos,
                "ultima_ata": ultima_ata,
            }
        )
        context["medicoes"] = medicoes
        context["nota_form"] = NotaContratoForm()
        context["total_medicoes"] = total_medicoes
        return context


class ContratoUpdateView(AccessRequiredMixin, ContratoAccessMixin, UpdateView):
    """
    Atualizar contrato
    """

    allowed_cargos = []
    view_name = "atualizar_contrato"
    no_permission_redirect_url = "lista_contratos"
    model = Contrato
    form_class = ContratoForm
    template_name = "contratos/contratos/editar_contratos.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.info(
            self.request,
            f"Contrato {self.object.numero} – {self.object.contratante.nome} atualizado com sucesso!",
        )
        return response

    def get_success_url(self):
        return reverse_lazy("detalhes_contrato", kwargs={"pk": self.object.pk})


class ContratoDeleteView(AccessRequiredMixin, ContratoAccessMixin, DeleteView):
    """
    Deletar contrato
    """

    allowed_cargos = []
    view_name = "deletar_contrato"
    no_permission_redirect_url = "lista_contratos"
    model = Contrato
    template_name = "contratos/contratos/excluir_contratos.html"
    success_url = reverse_lazy("lista_contratos")

    def form_valid(self, form):
        obj = self.get_object()
        numero = obj.numero
        contratante = obj.contratante.nome
        response = super().form_valid(form)  # deleta
        messages.warning(
            self.request, f"Contrato {numero} – {contratante} excluído com sucesso!"
        )
        return response


class AtasPorContratoView(AccessRequiredMixin, ListView):
    """
    Lista de atas do contrato
    """

    model = AtaReuniao
    template_name = "contratos/contratos/atas_por_contrato.html"
    context_object_name = "atas"
    allowed_cargos = []
    view_name = "atas_por_contrato"
    paginate_by = 20

    def get_queryset(self):
        return (
            AtaReuniao.objects.filter(contrato_id=self.kwargs["pk"])
            .annotate(pendentes=Count("itens", filter=Q(itens__status="pendente")))
            .select_related("contrato")
            .order_by("-data")
        )  # <- aqui está o ajuste que faltava

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contrato"] = get_object_or_404(Contrato, pk=self.kwargs["pk"])
        return context


class ObrasPorContratoView(AccessRequiredMixin, ListView):
    """
    Lista de obras do contrato
    """

    model = Obra
    template_name = "contratos/contratos/obras_por_contrato.html"
    context_object_name = "obras"
    allowed_cargos = []
    view_name = "obras_por_contrato"
    paginate_by = 20

    def get_queryset(self):
        return (
            Obra.objects.filter(contrato_id=self.kwargs["pk"])
            .select_related("contrato")
            .order_by("codigo")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contrato"] = get_object_or_404(Contrato, pk=self.kwargs["pk"])
        return context


# Notas nos contatos
class NotaContratoCreateView(AccessRequiredMixin, View):
    """
    Notas por contrato
    """

    allowed_cargos = []
    view_name = "criar_nota_contrato"
    no_permission_redirect_url = "index"

    def post(self, request, contrato_id):
        contrato = get_object_or_404(Contrato, pk=contrato_id)
        form = NotaContratoForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.contrato = contrato
            nota.criado_por = request.user
            nota.save()
            messages.success(request, "Anotação adicionada com sucesso.")
        else:
            messages.warning(request, "Erro ao adicionar anotação.")
        return HttpResponseRedirect(
            reverse("detalhes_contrato", kwargs={"pk": contrato.pk}) + "#anotacoes"
        )


class NotaContratoUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza a nota do contrato
    """

    allowed_cargos = []
    view_name = "atualizar_nota_contrato"
    model = NotaContrato
    form_class = NotaContratoForm
    template_name = "contratos/contratos/editar_nota.html"

    def form_valid(self, form):
        nota = form.save(commit=False)
        nota.updated_by = self.request.user
        nota.save()
        messages.info(self.request, "Anotação atualizada com sucesso.")
        return redirect("detalhes_contrato", pk=nota.contrato.pk)


class NotaContratoDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta a nota do contrato
    """

    allowed_cargos = []
    view_name = "deletar_nota_contrato"
    model = NotaContrato
    template_name = "contratos/contratos/excluir_nota.html"

    def get_success_url(self):
        messages.warning(self.request, "Anotação excluída com sucesso.")
        return reverse_lazy("detalhes_contrato", kwargs={"pk": self.object.contrato.pk})


def view_com_erro(request):
    x = 1 / 0  # isso vai causar ZeroDivisionError
    return HttpResponse("Isso nunca será exibido.")
