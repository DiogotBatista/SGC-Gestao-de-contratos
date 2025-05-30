from django.contrib import admin
from .models import AtaReuniao, ItemAta, CategoriaItemAta, ArquivoAta


@admin.register(CategoriaItemAta)
class CategoriaItemAtaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class ItemAtaInline(admin.TabularInline):
    model = ItemAta
    extra = 0
    fields = ('categoria', 'descricao', 'responsavel', 'solicitante', 'status', 'created_by', 'data_cadastro', 'ordem')
    readonly_fields = ('created_by', 'data_cadastro')

class ArquivoAtaInline(admin.TabularInline):
    model = ArquivoAta
    extra = 0
    fields = ('nome', 'link_arquivo', 'id_arquivo_drive', 'data_upload')
    readonly_fields = ('nome', 'link_arquivo', 'id_arquivo_drive', 'data_upload')

@admin.register(AtaReuniao)
class AtaReuniaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'contrato', 'autor', 'data_cadastro')
    list_filter = ('contrato', 'autor', 'data')
    search_fields = ('contrato__numero', 'resumo', 'autor__username')
    inlines = [ItemAtaInline, ArquivoAtaInline]
    readonly_fields = ('created_by', 'updated_by', 'data_cadastro', 'data_alteracao', 'nome')

@admin.register(ItemAta)
class ItemAtaAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'ata', 'responsavel', 'solicitante', 'status', 'created_by', 'data_cadastro', 'ordem')
    list_filter = ('categoria', 'status')
    search_fields = ('descricao', 'responsavel', 'solicitante', 'ata__contrato__numero')
    readonly_fields = ('created_by', 'data_cadastro')

@admin.register(ArquivoAta)
class ArquivoAtaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ata', 'link_arquivo', 'data_upload')
    search_fields = ('nome', 'ata__nome')
    readonly_fields = ('nome', 'link_arquivo', 'id_arquivo_drive', 'id_pasta_drive', 'data_upload')
