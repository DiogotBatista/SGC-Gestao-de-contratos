# app: reunioes/models.py

from django.db import models
from django.conf import settings
from contratos.models import Contrato
from django.utils import timezone

class AtaReuniao(models.Model):
    nome = models.CharField(max_length=255, editable=False, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='atas')
    data = models.DateField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    resumo = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atas_criadas'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atas_atualizadas'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Ata de Reunião'
        verbose_name_plural = 'Atas de Reunião'

    def save(self, *args, **kwargs):
        if self.contrato and self.data:
            self.nome = f"{self.contrato.numero} - {self.data.strftime('%d/%m/%Y')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ata {self.data} - {self.contrato}"

class CategoriaItemAta(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Categoria de Item"
        verbose_name_plural = "Categorias de Itens"

    def __str__(self):
        return self.nome

from django.utils import timezone

class ItemAta(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('nao_aplicavel', 'Não Aplicável'),
    ]

    ata = models.ForeignKey(AtaReuniao, on_delete=models.CASCADE, related_name='itens')
    categoria = models.ForeignKey(CategoriaItemAta, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    responsavel = models.CharField(max_length=100, null=True, blank=True,
                                   help_text="Responsável pela ação")
    solicitante = models.CharField(max_length=100, null=True, blank=True, help_text="Quem solicitou essa ação")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    data_prazo = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_ata_criados'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.categoria} - {self.ata.data}"

    def prazo_status(self):
        if self.data_prazo and self.status == 'pendente':
            return "atrasado" if self.data_prazo < timezone.now().date() else "em_dia"
        return None

class ArquivoAta(models.Model):
    ata = models.ForeignKey(AtaReuniao, on_delete=models.CASCADE, related_name='arquivos')
    nome = models.CharField(max_length=255, help_text="Nome original do arquivo")
    link_arquivo = models.URLField("Link no Drive")
    id_arquivo_drive = models.CharField("ID do Arquivo no Drive", max_length=100)
    id_pasta_drive = models.CharField("ID da Pasta no Drive", max_length=100, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome




