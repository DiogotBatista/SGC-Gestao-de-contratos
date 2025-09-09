import pandas as pd
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.timezone import localtime
from django.views.decorators.http import require_GET

from ..models import AlocacaoVeiculo, Veiculo
from .veiculos import VeiculoListView


def _token_ok(request):
    # Ajuste a origem desse token conforme seu padrão (env/settings).
    expected = getattr(settings, "EXPORT_BI_TOKEN", None)
    received = request.GET.get("token")
    return expected and received and expected == received


@require_GET
def exportar_bi_veiculos(request):
    if not _token_ok(request):
        return HttpResponseForbidden("Token inválido")

    qs = Veiculo.objects.select_related(
        "modalidade", "empresa_locadora", "status", "contrato_atual"
    ).filter(ativo=True)

    data = []
    for v in qs:
        data.append(
            {
                "id": v.id,
                "modalidade": v.modalidade.nome if v.modalidade else None,
                "modelo": v.modelo,
                "placa": v.placa,
                "tag_contrato": v.tag_contrato,
                "origem": v.get_origem_display(),
                "empresa_locadora": (
                    v.empresa_locadora.nome if v.empresa_locadora else None
                ),
                "status": v.status.nome if v.status else None,
                "contrato_atual_id": v.contrato_atual_id,
                "contrato_atual": getattr(v.contrato_atual, "descricao", None),
                "data_cadastro": v.data_cadastro.isoformat(),
                "data_alteracao": v.data_alteracao.isoformat(),
            }
        )
    return JsonResponse(data, safe=False)


@require_GET
def exportar_bi_alocacoes(request):
    if not _token_ok(request):
        return HttpResponseForbidden("Token inválido")

    qs = (
        AlocacaoVeiculo.objects.select_related("veiculo", "contrato", "obra")
        .filter(ativo=True)
        .order_by("-data_inicio", "-id")
    )

    data = []
    for a in qs:
        data.append(
            {
                "id": a.id,
                "veiculo_id": a.veiculo_id,
                "veiculo_modelo": a.veiculo.modelo,
                "veiculo_placa": a.veiculo.placa,
                "contrato_id": a.contrato_id,
                "contrato": a.contrato.descricao if a.contrato else None,
                "obra_id": a.obra_id,
                "obra": a.obra.descricao if a.obra else None,
                "data_inicio": a.data_inicio.isoformat(),
                "data_fim": a.data_fim.isoformat() if a.data_fim else None,
                "observacoes": a.observacoes,
                "em_aberto": a.data_fim is None,
                "data_cadastro": a.data_cadastro.isoformat(),
                "data_alteracao": a.data_alteracao.isoformat(),
            }
        )
    return JsonResponse(data, safe=False)


def exportar_excel_veiculos(request):
    # Reaproveita a lógica de filtros da listagem
    view = VeiculoListView()
    view.request = request
    qs = view.get_queryset()

    data = []
    for v in qs:
        data.append(
            {
                "Modelo": v.modelo,
                "Placa": v.placa,
                "TAG": v.tag_contrato or "—",
                "Modalidade": v.modalidade.nome if v.modalidade else "—",
                "Origem": v.get_origem_display(),
                "Status": v.status.nome if v.status else "—",
                "Locadora": v.empresa_locadora.nome if v.empresa_locadora else "—",
                "Contrato Atual": (
                    v.contrato_atual.numero if v.contrato_atual else "Sem alocação"
                ),
                "Ativo": "Sim" if v.ativo else "Não",
            }
        )

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="veiculos.xlsx"'

    # aqui tenta usar openpyxl, se não tiver cai no xlsxwriter
    try:
        import openpyxl  # noqa

        engine = "openpyxl"
    except ImportError:
        engine = "xlsxwriter"

    df.to_excel(response, index=False, engine=engine)
    return response
