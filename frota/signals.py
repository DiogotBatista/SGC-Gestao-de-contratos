from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AlocacaoVeiculo, Veiculo


def _atualizar_contrato_atual(veiculo: Veiculo):
    """
    Mantém Veiculo.contrato_atual = contrato da alocação em aberto (se houver), senão None.
    """
    aloc_aberta = (
        veiculo.alocacoes.filter(ativo=True, data_fim__isnull=True)
        .order_by("-data_inicio", "-id")
        .first()
    )
    novo_contrato = aloc_aberta.contrato if aloc_aberta else None

    if veiculo.contrato_atual_id != (novo_contrato.id if novo_contrato else None):
        veiculo.contrato_atual = novo_contrato
        veiculo.save(update_fields=["contrato_atual", "data_alteracao"])


@receiver(post_save, sender=AlocacaoVeiculo)
def apos_salvar_alocacao(sender, instance: AlocacaoVeiculo, **kwargs):
    _atualizar_contrato_atual(instance.veiculo)


@receiver(post_delete, sender=AlocacaoVeiculo)
def apos_excluir_alocacao(sender, instance: AlocacaoVeiculo, **kwargs):
    _atualizar_contrato_atual(instance.veiculo)
