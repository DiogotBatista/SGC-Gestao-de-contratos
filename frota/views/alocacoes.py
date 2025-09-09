from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.generic import ListView

from core.mixins import AccessRequiredMixin

from ..models import AlocacaoVeiculo, Veiculo


class AlocacaoListView(AccessRequiredMixin, ListView):
    """
    Lista de alocações com busca, filtros e paginação.
    """

    allowed_cargos = []
    view_name = "lista_alocacoes"
    model = AlocacaoVeiculo
    template_name = "frota/alocacoes/lista_alocacoes.html"
    context_object_name = "alocacoes"
    paginate_by = 20
    ordering = ["-data_inicio", "-id"]

    def get_queryset(self):
        params = self.request.GET.copy()
        q = (params.get("q") or "").strip()
        aberto = params.get(
            "aberto", "1"
        )  # 1 = abertas (padrão), 0 = fechadas, 'todos' = todas
        di = parse_date(params.get("data_inicio") or "")
        df = parse_date(params.get("data_fim") or "")

        qs = AlocacaoVeiculo.objects.select_related("veiculo", "contrato", "obra")

        # Ativo/Inativo: só filtre quando NÃO houver busca textual (mesma lógica que aplicamos nas outras listas)
        if not q:
            ativo = params.get("ativo", "sim")
            if ativo == "nao":
                qs = qs.filter(ativo=False)
            elif ativo == "todos":
                pass
            else:
                qs = qs.filter(ativo=True)

        # Filtro Aberta/Fechada/Todas
        if aberto == "1":  # abertas
            qs = qs.filter(data_fim__isnull=True)
        elif aberto == "0":  # fechadas
            qs = qs.filter(data_fim__isnull=False)
        # 'todos' -> sem filtro por data_fim

        # Busca textual
        if q:
            qs = qs.filter(
                Q(veiculo__modelo__icontains=q)
                | Q(veiculo__placa__icontains=q)
                | Q(contrato__numero__icontains=q)
                | Q(obra__descricao__icontains=q)
                | Q(veiculo__modalidade__nome__icontains=q)
            )

        # Filtros por chaves diretas
        if vid := params.get("veiculo"):
            qs = qs.filter(veiculo_id=vid)
        if cid := params.get("contrato"):
            qs = qs.filter(contrato_id=cid)

        # Filtros por data (comportamento claro p/ abertas x fechadas)
        di = parse_date(params.get("data_inicio") or "")
        df = parse_date(params.get("data_fim") or "")

        #  Filtro de datas, simples e independente
        if di:
            qs = qs.filter(data_inicio__gte=di)

        if df:
            qs = qs.filter(
                data_fim__lte=df
            )  # abertas (data_fim IS NULL) ficam naturalmente de fora

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["veiculos"] = Veiculo.objects.filter(ativo=True).order_by("modelo", "placa")
        ctx["params"] = self.request.GET
        return ctx
