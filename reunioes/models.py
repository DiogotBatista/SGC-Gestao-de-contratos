from django.db import models
from django.conf import settings
from contratos.models import Contrato


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

class ItemAta(models.Model):
    ata = models.ForeignKey(AtaReuniao, on_delete=models.CASCADE, related_name='itens')
    categoria = models.ForeignKey(CategoriaItemAta, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('pendente', 'Pendente'), ('concluido', 'Concluído')],
        default='pendente'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_ata_criados'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ordem = models.PositiveIntegerField(default=0)  # <- novo campo

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.categoria} - {self.ata.data}"

