import re
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_cnpj(value):
    # Remove qualquer caractere não numérico
    cnpj = re.sub(r'\D', '', value)
    if len(cnpj) != 14:
        raise ValidationError('CNPJ deve ter 14 dígitos.')
    # Verifica se todos os dígitos são iguais (ex: 11111111111111 é inválido)
    if cnpj == cnpj[0] * 14:
        raise ValidationError('CNPJ inválido.')

    def calculate_digit(cnpj, digit):
        if digit == 1:
            weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            numbers = cnpj[:12]
        else:
            weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            numbers = cnpj[:13]
        total = sum(int(n) * w for n, w in zip(numbers, weights))
        remainder = total % 11
        return '0' if remainder < 2 else str(11 - remainder)

    digit1 = calculate_digit(cnpj, 1)
    digit2 = calculate_digit(cnpj, 2)

    if cnpj[-2:] != digit1 + digit2:
        raise ValidationError('CNPJ inválido.')

class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome


class Contratante(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Empresa' ,help_text="Nome do contratante, ex: Empresa X")
    cnpj = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="CNPJ do contratante",
        validators=[validate_cnpj]
    )
    ativo = models.BooleanField(default=True, help_text="Indica que o contratante será tratado como ativo. Ao invés de exclui-lo, desmarque isso.")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contratante_criados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contratante_atualizados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['nome']
        verbose_name = 'Contratante'
        verbose_name_plural = 'Contratantes'

    def __str__(self):
        return self.nome


class Contrato(models.Model):
    numero = models.CharField(max_length=50, unique=True, verbose_name='Contrato', help_text="Número do contrato")
    contratante = models.ForeignKey(Contratante, on_delete=models.RESTRICT, related_name='contratos')
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Valor total do contrato incluídos os TAC's")
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True, help_text="Descrição ou observações sobre o contrato")
    ativo = models.BooleanField(default=True, help_text="Indica que o contrato será tratado como ativo. Ao invés de exclui-lo, desmarque isso.")
    preposto = models.CharField(max_length=150)
    url_dashboard = models.URLField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contrato_criado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contrato_atualizados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    @property
    def media_execucao_obras(self):
        obras = self.obras.all()
        valores = [obra.porcentagem_execucao for obra in obras if obra.porcentagem_execucao is not None]
        if not valores:
            return 0
        return sum(valores) / len(valores)

    def __str__(self):
        return f"{self.numero} - {self.contratante}"


class Obra(models.Model):
    codigo = models.CharField(max_length=50, unique=True,verbose_name='Cod/Nome Obra', help_text="Código da obra/serviço")
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, related_name='obras')
    local = models.CharField(max_length=100, help_text="Local de execução da obra")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição ou observações sobre a obra")
    ativo = models.BooleanField(default=True, help_text="Indica que a obra será tratada como ativa. Ao invés de exclui-la, desmarque isso.")
    porcentagem_execucao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Execução (%)',
        help_text='Percentual de execução da obra'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='obras_criadas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='obras_atualizadas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Obra'
        verbose_name_plural = 'Obras'

    def __str__(self):
        return self.codigo

class NotaContrato(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='notas')
    texto = models.TextField(verbose_name='Anotação')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Nota do Contrato'
        verbose_name_plural = 'Notas do Contrato'

    def __str__(self):
        return f"Nota - {self.contrato.numero} ({self.criado_em.strftime('%d/%m/%Y')})"

class NotaObra(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='notas')
    texto = models.TextField(verbose_name='Anotação')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Nota da Obra"
        verbose_name_plural = "Notas das Obras"

    def __str__(self):
        return f"Nota - {self.obra.codigo} por {self.criado_por}"