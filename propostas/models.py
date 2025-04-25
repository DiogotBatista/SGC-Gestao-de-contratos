from django.db import models
from contratos.models import Contratante
from django.conf import settings

class PropostaOrcamento(models.Model):
    ETAPAS = [
        ('analise', 'Em Análise'),
        ('negociacao', 'Em Negociação'),
        ('aguardando', 'Aguardando Resposta'),
        ('finalizada', 'Finalizada'),
    ]

    NEGOCIACAO = [
        ('Contrato firmado', 'Orçamento Negociado / Contrato firmado'),
        ("Proposta rejeitada", "Orçamento Não Negociado / Proposta rejeitada"),
        ('Em negociação', "Orçamento aguardando negociação"),
    ]

    titulo = models.CharField(
        max_length=150,
        verbose_name="Título da Proposta",
        help_text='Nome dado à proposta'
    )
    contratante = models.ForeignKey(
        Contratante,
        on_delete=models.PROTECT,
        related_name='propostas',
        verbose_name="Contratante",
        help_text='Nome do contratante'
    )
    local_execucao = models.CharField(
        max_length=255,
        verbose_name="Local de Execução",
        help_text='Local de execução da obra/serviço'
    )
    valor_estimado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor Estimado em Reais (R$)",
        help_text='Valor do orçamento/proposta'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
        help_text='Breve descrição do serviço / obra'
    )
    data_recebimento = models.DateField(
        verbose_name="Data de Recebimento",
        help_text='Data de receb. da solic. de orçamento/proposta'
    )
    etapa_atual = models.CharField(
        max_length=20,
        choices=ETAPAS,
        default='analise',
        verbose_name="Etapa Atual",
        help_text='Etapa da negociação'
    )
    data_envio = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Envio",
        help_text="Data de envio da proposta para o contratante"
    )
    data_resposta = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data da Resposta",
        help_text='Data da resposta do contratante'
    )
    situacao = models.CharField(
        max_length=20,
        choices=NEGOCIACAO,
        default='Em negociação',
        verbose_name="Situação",
        help_text='Situação do orçamento/proposta'
    )
    endereco_servidor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Endereço no Servidor",
        help_text="Informe o link onde a proposta original está armazenada"
    )

    # Automatizados
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    data_alteracao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Alteração"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='propostas_criadas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='propostas_atualizadas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Atualizado por"
    )

    class Meta:
        ordering = ['-data_cadastro']
        verbose_name = "Proposta de Orçamento"
        verbose_name_plural = "Propostas de Orçamento"

    def __str__(self):
        return f"{self.contratante} - {self.local_execucao} - R$ {self.valor_estimado:,.2f}"
