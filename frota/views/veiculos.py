from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from core.mixins import AccessRequiredMixin

from ..forms import AlocacaoVeiculoForm, VeiculoForm
from ..models import (AlocacaoVeiculo, Fornecedor, ModalidadeVeiculo,
                      StatusVeiculo, Veiculo)


# ---------- CRUD Veículo ---------
class VeiculoListView(AccessRequiredMixin, ListView):
    """
    Lista de veículos (busca + filtros + paginação)

    """

    allowed_cargos = []
    view_name = "lista_veiculos"
    model = Veiculo
    template_name = "frota/veiculos/lista_veiculos.html"
    context_object_name = "veiculos"
    paginate_by = 20
    ordering = ["modelo", "placa"]

    def get_queryset(self):
        qs = Veiculo.objects.select_related(
            "modalidade", "empresa_locadora", "status", "contrato_atual"
        )
        params = self.request.GET.copy()
        q = self.request.GET.get("q", "").strip()

        if not q:
            ativo = params.get("ativo", "sim")
            if ativo == "nao":
                qs = qs.filter(ativo=False)
            elif ativo == "todos":
                pass  # sem filtro
            else:
                qs = qs.filter(ativo=True)

        if q:
            qs = qs.filter(
                Q(modelo__icontains=q)
                | Q(placa__icontains=q)
                | Q(tag_contrato__icontains=q)
                | Q(empresa_locadora__nome__icontains=q)
                | Q(contrato_atual__descricao__icontains=q)
            )

        modalidade_id = self.request.GET.get("modalidade")
        if modalidade_id:
            qs = qs.filter(modalidade_id=modalidade_id)

        origem = self.request.GET.get("origem")
        if origem in {"PROPRIO", "ALUGADO"}:
            qs = qs.filter(origem=origem)

        status_id = self.request.GET.get("status")
        if status_id:
            qs = qs.filter(status_id=status_id)

        locadora_id = self.request.GET.get("locadora")
        if locadora_id:
            qs = qs.filter(empresa_locadora_id=locadora_id)

        contrato_id = self.request.GET.get("contrato")
        if contrato_id:
            qs = qs.filter(contrato_atual_id=contrato_id)

        tag_flag = self.request.GET.get("tem_tag")
        if tag_flag == "sim":
            qs = qs.filter(tag_contrato__isnull=False).exclude(tag_contrato__exact="")
        elif tag_flag == "nao":
            qs = qs.filter(Q(tag_contrato__isnull=True) | Q(tag_contrato__exact=""))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["modalidades"] = ModalidadeVeiculo.objects.filter(ativo=True).order_by(
            "nome"
        )
        ctx["statuses"] = StatusVeiculo.objects.filter(ativo=True).order_by("nome")
        ctx["locadoras"] = Fornecedor.objects.filter(ativo=True).order_by("nome")
        ctx["params"] = self.request.GET
        return ctx


class VeiculoCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastro de veículo (com created_by/updated_by + messages), como você faz em Contratos.
    """

    allowed_cargos = []
    view_name = "cadastrar_veiculo"
    no_permission_redirect_url = "lista_veiculos"
    model = Veiculo
    form_class = VeiculoForm
    template_name = "frota/veiculos/cadastrar_veiculo.html"
    success_url = reverse_lazy("frota:lista_veiculos")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        resp = super().form_valid(form)
        messages.success(self.request, "Veículo cadastrado com sucesso!")
        return resp

    def form_invalid(self, form):
        for field, errs in form.errors.items():
            for e in errs:
                if field == "__all__":
                    messages.warning(self.request, e)
                else:
                    messages.warning(self.request, f"{field}: {e}")
        # Renderiza a própria página com erros (sem redirect)
        return self.render_to_response(self.get_context_data(form=form))


class VeiculoUpdateView(AccessRequiredMixin, UpdateView):
    """
    Edição do veículo (updated_by + messages).
    """

    allowed_cargos = []
    view_name = "editar_veiculo"
    no_permission_redirect_url = "frota:lista_veiculos"
    model = Veiculo
    form_class = VeiculoForm
    template_name = "frota/veiculos/editar_veiculo.html"

    def get_queryset(self):
        return Veiculo.objects.filter(ativo=True)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        resp = super().form_valid(form)
        messages.info(self.request, "Veículo atualizado com sucesso!")
        return resp

    def get_success_url(self):
        return reverse_lazy("frota:detalhe_veiculo", kwargs={"pk": self.object.pk})


class VeiculoDetailView(AccessRequiredMixin, DetailView):
    """
    Detalhe com alocação aberta + histórico.
    """

    allowed_cargos = []
    view_name = "detalhe_veiculo"
    model = Veiculo
    template_name = "frota/veiculos/detalhe_veiculo.html"
    context_object_name = "veiculo"

    def get_queryset(self):
        return Veiculo.objects.select_related(
            "modalidade", "empresa_locadora", "status", "contrato_atual"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        v = self.object
        ctx["alocacao_aberta"] = (
            v.alocacoes.filter(ativo=True, data_fim__isnull=True)
            .select_related("contrato", "obra")
            .first()
        )
        ctx["historico"] = (
            v.alocacoes.filter(ativo=True)
            .select_related("contrato", "obra")
            .order_by("-data_inicio", "-id")
        )
        ctx["form_alocar"] = AlocacaoVeiculoForm(initial={"veiculo": v})
        return ctx


class VeiculoDeleteView(AccessRequiredMixin, DeleteView):
    """
    Soft delete (ativo=False) como você usa em outros módulos quando necessário.
    """

    allowed_cargos = []
    view_name = "excluir_veiculo"
    no_permission_redirect_url = "frota:lista_veiculos"
    model = Veiculo
    template_name = "frota/veiculos/confirma_exclusao_veiculo.html"
    success_url = reverse_lazy("frota:lista_veiculos")

    def get_queryset(self):
        return Veiculo.objects.filter(ativo=True)

    def form_valid(self, form):
        obj = self.get_object()
        obj.ativo = False
        obj.updated_by = self.request.user
        obj.save(update_fields=["ativo", "updated_by", "data_alteracao"])
        messages.warning(self.request, "Veículo desativado com sucesso!")
        return redirect(self.get_success_url())


# --- Desativar veículo (soft delete via modal) ---
class VeiculoDesativarView(AccessRequiredMixin, View):
    allowed_cargos = []  # ajuste se quiser restringir
    view_name = "desativar_veiculo"
    no_permission_redirect_url = "frota:lista_veiculos"

    def post(self, request, pk):
        v = get_object_or_404(Veiculo, pk=pk, ativo=True)
        v.ativo = False
        v.updated_by = request.user
        v.save(update_fields=["ativo", "updated_by", "data_alteracao"])
        messages.warning(request, f"Veículo {v.modelo} ({v.placa}) desativado.")
        return redirect("frota:lista_veiculos")


# frota/views/veiculos.py
class VeiculoReativarView(AccessRequiredMixin, View):
    allowed_cargos = []  # ajuste se quiser restringir
    view_name = "reativar_veiculo"
    no_permission_redirect_url = "frota:lista_veiculos"

    def post(self, request, pk):
        v = get_object_or_404(Veiculo, pk=pk, ativo=False)
        v.ativo = True
        v.updated_by = request.user
        v.save(update_fields=["ativo", "updated_by", "data_alteracao"])
        messages.success(request, f"Veículo {v.modelo} ({v.placa}) reativado.")
        return redirect("frota:detalhe_veiculo", pk=v.pk)


# ---------- Ações de Alocação no contexto do Veículo ----------


class VeiculoAlocarView(AccessRequiredMixin, View):
    """
    Cria uma alocação para o veículo.
    Regras:
      - Campos obrigatórios: mostrar erros abaixo dos campos no offcanvas.
      - Se já houver mobilização aberta: bloquear e mostrar TOAST.
      - Se houver conflito de período: bloquear e mostrar TOAST.
      - Permitir troca no mesmo dia (já coberto pelo model.clean()).

    """

    allowed_cargos = []
    view_name = "alocar_veiculo"
    no_permission_redirect_url = "frota:lista_veiculos"

    def post(self, request, pk):
        veiculo = get_object_or_404(Veiculo, pk=pk)
        form = AlocacaoVeiculoForm(request.POST)
        form.instance.veiculo = veiculo

        if form.is_valid():
            aloc = form.save(commit=False)
            aloc.veiculo = veiculo
            aloc.created_by = request.user
            try:
                with transaction.atomic():
                    aloc.full_clean()  # dispara as validações de negócio
                    aloc.save()
            except ValidationError as e:
                # Se for regra de negócio (non-field / __all__), mostrar TOAST e redirecionar
                msg_dict = getattr(e, "message_dict", None)
                non_field = []
                if msg_dict:
                    non_field = msg_dict.get("__all__", [])
                else:
                    # pode ser uma lista simples
                    non_field = [str(e)]

                if non_field:
                    # Mostra todas as mensagens como TOAST
                    for m in non_field:
                        messages.warning(request, m)
                    return redirect("frota:detalhe_veiculo", veiculo.pk)

                # Caso venham erros de campo específicos por algum motivo incomum,
                # propaga para o form e cai para re-renderizar com offcanvas aberto
                if msg_dict:
                    for field, errs in msg_dict.items():
                        for m in errs:
                            form.add_error(field if field != "__all__" else None, m)
                else:
                    form.add_error(None, str(e))
            else:
                # sucesso → volta ao detalhe
                messages.success(request, "Mobilização criada com sucesso!")
                return redirect("frota:detalhe_veiculo", veiculo.pk)

        # FORM INVÁLIDO: reabrir offcanvas e repassar contexto completo
        alocacao_aberta = (
            veiculo.alocacoes.filter(ativo=True, data_fim__isnull=True)
            .select_related("contrato", "obra")
            .first()
        )
        historico = (
            veiculo.alocacoes.filter(ativo=True)
            .select_related("contrato", "obra")
            .order_by("-data_inicio", "-id")
        )

        context = {
            "veiculo": veiculo,
            "form_alocar": form,
            "abrir_offcanvas_alocar": True,  # reabre o offcanvas no template
            "alocacao_aberta": alocacao_aberta,
            "historico": historico,
        }
        return render(request, "frota/veiculos/detalhe_veiculo.html", context)


class VeiculoEncerrarAlocacaoView(AccessRequiredMixin, View):
    """
    Define data_fim da alocação aberta (hoje por padrão).
    """

    allowed_cargos = []
    view_name = "encerrar_alocacao"
    no_permission_redirect_url = "frota:lista_veiculos"

    def post(self, request, pk):
        veiculo = get_object_or_404(Veiculo, pk=pk, ativo=True)
        data_str = request.POST.get("data_fim")
        if data_str:
            try:
                data_fim = datetime.strptime(data_str, "%Y-%m-%d").date()
            except Exception:
                data_fim = timezone.now().date()
        else:
            data_fim = timezone.now().date()

        try:
            with transaction.atomic():
                aloc = (
                    AlocacaoVeiculo.objects.select_for_update()
                    .filter(veiculo=veiculo, ativo=True, data_fim__isnull=True)
                    .first()
                )
                if not aloc:
                    messages.info(
                        request, "Não há mobilização em aberto para este veículo."
                    )
                    return redirect("frota:detalhe_veiculo", pk=veiculo.pk)

                aloc.data_fim = data_fim
                aloc.updated_by = request.user
                aloc.full_clean()
                aloc.save()

                messages.info(request, "Mobilização encerrada!")
        except ValidationError as ve:
            # ✅ mostramos campo e mensagem certinhos (sem dict feio)
            if hasattr(ve, "message_dict"):
                for field, errs in ve.message_dict.items():
                    for e in errs:
                        if field == "__all__":
                            messages.warning(request, e)
                        else:
                            messages.warning(request, f"{field}: {e}")
            else:
                messages.warning(request, str(ve))
        except Exception as e:
            messages.warning(request, f"Erro ao encerrar mobilização: {e}")

        return redirect("frota:detalhe_veiculo", pk=veiculo.pk)
