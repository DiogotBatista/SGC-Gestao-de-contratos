#medicoes/models.py

from django.db import models
from contratos.models import Contrato
from django.conf import settings

class Medicao(models.Model):
    contrato = models.ForeignKey('contratos.Contrato', on_delete=models.CASCADE, related_name='medicoes')
    identificador = models.CharField(max_length=100)
    data_inicio = models.DateField(verbose_name="Inicio do período")
    data_fim = models.DateField(verbose_name="Fim do Período")
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    situacao = models.CharField(max_length=20, verbose_name="Situação", choices=[("pendente", "Pendente"), ("fechada", "Fechada")], default="pendente")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='medicoes_criadas', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='medicoes_atualizadas', on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def periodo_formatado(self):
        return f"{self.data_inicio.strftime('%d/%m/%y')} a {self.data_fim.strftime('%d/%m/%y')}"

    class Meta:
        ordering = ['-data_inicio']


