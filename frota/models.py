from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Upper
from django.utils import timezone

from contratos.models import Contrato, Obra

User = get_user_model()


# ===== Mixins simples seguindo o padrão SGC =====
class AuditMixin(models.Model):
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_criado_por",
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_atualizado_por",
        verbose_name="Atualizado por",
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de cadastro"
    )
    data_alteracao = models.DateTimeField(
        auto_now=True, verbose_name="Data de alteração"
    )

    class Meta:
        abstract = True


# ===== Catálogos  =====
class ModalidadeVeiculo(AuditMixin):
    """
    Ex.: 4x4, Leve, Retro, Pipa, Moto, Caminhão, Vans, etc.
    """

    nome = models.CharField(max_length=60, unique=True, verbose_name="Modalidade")

    class Meta:
        ordering = ["nome"]
        verbose_name = "Modalidade de Veículo"
        verbose_name_plural = "Modalidades de Veículo"

    def __str__(self):
        return self.nome


class StatusVeiculo(AuditMixin):
    """
    Ex.: ATIVO, EM_MANUTENCAO, RESERVA, AGUARDANDO_DOC, INATIVO
    (cadastrável e flexível)
    """

    APARENCIA_CHOICES = (
        ("PRIMARY", "Primary"),
        ("SECONDARY", "Secondary"),
        ("SUCCESS", "Success"),
        ("DANGER", "Danger"),
        ("WARNING", "Warning"),
        ("INFO", "Info"),
        ("LIGHT", "Light"),
        ("DARK", "Dark"),
    )

    nome = models.CharField(max_length=40, unique=True, verbose_name="Status")
    categoria = models.CharField(
        max_length=15,
        choices=APARENCIA_CHOICES,
        verbose_name="Aparencia",
        default="INFO",
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Status de Veículo"
        verbose_name_plural = "Status de Veículo"

    def __str__(self):
        return self.nome


class Fornecedor(AuditMixin):
    """
    Fornecedor/locadora (somente o essencial por enquanto).
    """

    nome = models.CharField(
        max_length=120, unique=True, verbose_name="Nome/Razão social"
    )
    contato = models.CharField(
        max_length=120, blank=True, null=True, verbose_name="Contato"
    )
    telefone = models.CharField(
        max_length=40, blank=True, null=True, verbose_name="Telefone"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return self.nome


# ===== Veículo =====
class Veiculo(AuditMixin):
    ORIGEM_CHOICES = (
        ("PROPRIO", "Próprio"),
        ("ALUGADO", "Alugado"),
    )

    modalidade = models.ForeignKey(
        ModalidadeVeiculo,
        on_delete=models.PROTECT,
        related_name="veiculos",
        verbose_name="Modalidade",
    )
    modelo = models.CharField(max_length=120, verbose_name="Modelo")  # (obrigatório)
    placa = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Placa",
        help_text="Informe sem traço/ponto",
    )  # (obrigatório)
    tag_contrato = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="TAG do Contrato",
        help_text="Deixe em branco se o contrato não utilizar TAG.",
    )
    origem = models.CharField(
        max_length=10, choices=ORIGEM_CHOICES, verbose_name="Origem"
    )
    empresa_locadora = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="veiculos_alugados",
        verbose_name="Empresa locadora",
    )
    # Dados de aquisição/locação (sem valores financeiros neste momento)
    data_aquisicao = models.DateField(
        null=True, blank=True, verbose_name="Data de aquisição"
    )
    data_inicio_locacao = models.DateField(
        null=True, blank=True, verbose_name="Início da locação"
    )

    status = models.ForeignKey(
        StatusVeiculo,
        on_delete=models.PROTECT,
        related_name="veiculos",
        verbose_name="Status",
    )

    contrato_atual = models.ForeignKey(
        Contrato,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="veiculos_atribuidos",
        verbose_name="Contrato atual",
    )

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        ordering = ["modelo", "placa"]
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        indexes = [
            models.Index(fields=["origem"]),
        ]
        constraints = [
            UniqueConstraint(
                Upper("tag_contrato"),
                name="uniq_veiculo_tag_contrato_ci_not_blank",
                condition=Q(tag_contrato__isnull=False) & ~Q(tag_contrato__exact=""),
            )
        ]

    def __str__(self):
        return f"{self.modelo} - {self.placa or 'SEM PLACA'}"

    def clean(self):
        errors = {}

        # Regras de consistência:
        # 1) Origem = ALUGADO -> empresa_locadora obrigatória
        if self.origem == "ALUGADO" and not self.empresa_locadora:
            raise ValidationError(
                {
                    "empresa_locadora": "Obrigatório informar a empresa locadora para veículos alugados."
                }
            )
        # 2) Origem = PROPRIO -> não exigir empresa_locadora
        # 3) Placa normalizada
        if self.placa:
            self.placa = self.placa.replace("-", "").replace(" ", "").upper()

        if self.modelo:
            self.modelo = self.modelo.upper()

        if self.tag_contrato:
            self.tag_contrato = self.tag_contrato.upper()

        if self.tag_contrato:
            existe = (
                Veiculo.objects.filter(tag_contrato__iexact=self.tag_contrato)
                .exclude(pk=self.pk)
                .exists()
            )
            if existe:
                errors["tag_contrato"] = "Esta TAG já está em uso por outro veículo."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.placa:
            self.placa = self.placa.replace("-", "").replace(" ", "").upper()

        if self.modelo:
            self.modelo = self.modelo.upper()

        if self.tag_contrato:
            self.tag_contrato = self.tag_contrato.upper()

        super().save(*args, **kwargs)


# ===== Alocação (histórico) =====
class AlocacaoVeiculo(AuditMixin):
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.CASCADE,
        related_name="alocacoes",
        verbose_name="Veículo",
    )
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.PROTECT,
        related_name="alocacoes_veiculos",
        verbose_name="Contrato",
    )
    obra = models.ForeignKey(
        Obra,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alocacoes_veiculos",
        verbose_name="Obra",
    )
    data_inicio = models.DateField(verbose_name="Data de início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de fim")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        ordering = ["-data_inicio", "-id"]
        verbose_name = "Alocação de Veículo"
        verbose_name_plural = "Alocações de Veículos"

    def __str__(self):
        fim = self.data_fim.strftime("%d/%m/%Y") if self.data_fim else "em aberto"
        return f"{self.veiculo} @ {self.contrato} ({self.data_inicio:%d/%m/%Y} → {fim})"

    # ---- Validações de negócio críticas ----

    def clean(self):
        errors = {}

        # --- Campos obrigatórios (evita consultar com None e dá mensagens claras) ---
        if not getattr(self, "veiculo_id", None):
            errors["veiculo"] = "Selecione o veículo."
        if not getattr(self, "contrato_id", None):
            errors["contrato"] = "Selecione o contrato."
        if not self.data_inicio:
            errors["data_inicio"] = "Informe a data de início."

        # Coerência de datas
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            errors["data_fim"] = "A data de fim não pode ser anterior à data de início."

        if self.data_fim and self.data_fim > date.today():
            errors["data_fim"] = "A data de encerramento não pode ser data futura."

        if errors:
            raise ValidationError(errors)

        # --- Máx. 1 mobilização aberta (além desta) ---
        if self.data_fim is None:
            existe_aberta = (
                type(self)
                .objects.filter(
                    ativo=True, veiculo_id=self.veiculo_id, data_fim__isnull=True
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if existe_aberta:
                raise ValidationError(
                    {
                        "__all__": (
                            "Já existe uma mobilização em aberto para este veículo. "
                            "Encerre-a antes de criar outra."
                        )
                    }
                )

        # --- Sobreposição permitindo troca no MESMO dia ---
        novo_inicio = self.data_inicio
        novo_fim = self.data_fim or date(9999, 12, 31)

        qs = (
            type(self)
            .objects.filter(ativo=True, veiculo_id=self.veiculo_id)
            .exclude(pk=self.pk)
        )

        # NÃO conflitam se:
        #   prev_fim <= novo_inicio   OU   novo_fim <= prev_inicio
        nao_conflitam = Q(data_fim__isnull=False, data_fim__lte=novo_inicio) | Q(
            data_inicio__gte=novo_fim
        )
        conflito = qs.exclude(nao_conflitam).exists()
        if conflito:
            raise ValidationError(
                {
                    "__all__": "Período informado conflita com outra mobilização deste veículo."
                }
            )

    @property
    def em_aberto(self):
        return self.data_fim is None
