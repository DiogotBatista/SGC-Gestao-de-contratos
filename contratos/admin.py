from django.contrib import admin
from .models import Empresa, Contratante, Contrato, Obra

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj']
    search_fields = ['nome', 'cnpj']

@admin.register(Contratante)
class ContratanteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'ativo', 'data_cadastro']
    list_filter = ['ativo']
    search_fields = ['nome', 'cnpj']

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'contratante', 'preposto', 'valor_total', 'ativo', 'data_inicio', 'data_fim']
    list_filter = ['ativo', 'contratante']
    search_fields = ['numero', 'contratante__nome', 'preposto']
    ordering = ['numero']

@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'contrato', 'local', 'ativo', 'porcentagem_execucao']
    list_filter = ['ativo', 'contrato']
    search_fields = ['codigo', 'local', 'contrato__numero']
    ordering = ['codigo']
