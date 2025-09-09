# from django.db import transaction
# from django.utils import timezone
#
# from ..models import AlocacaoVeiculo, Veiculo
#
#
# @transaction.atomic
# def transferir_veiculo(
#     veiculo: Veiculo,
#     contrato_destino,
#     obra_destino=None,
#     data=None,
#     user=None,
#     observacoes=None,
# ):
#     """
#     Fecha a alocação aberta atual (se existir) e cria nova alocação no contrato destino.
#     Operação atômica: ou tudo, ou nada.
#     """
#     data_hoje = data or timezone.now().date()
#
#     # Fecha alocação aberta, se existir
#     aloc_aberta = (
#         AlocacaoVeiculo.objects.select_for_update()
#         .filter(veiculo=veiculo, data_fim__isnull=True, ativo=True)
#         .first()
#     )
#
#     if aloc_aberta:
#         aloc_aberta.data_fim = data_hoje
#         if user:
#             aloc_aberta.updated_by = user
#         aloc_aberta.full_clean()
#         aloc_aberta.save()
#
#     # Cria nova alocação
#     nova = AlocacaoVeiculo(
#         veiculo=veiculo,
#         contrato=contrato_destino,
#         obra=obra_destino,
#         data_inicio=data_hoje,
#         observacoes=observacoes,
#         created_by=user,
#         updated_by=user,
#         ativo=True,
#     )
#     nova.full_clean()
#     nova.save()
#
#     return nova
