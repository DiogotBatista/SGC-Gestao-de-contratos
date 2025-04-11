from django.contrib import admin
from .models import AtaReuniao, ItemAta, CategoriaItemAta


@admin.register(CategoriaItemAta)
class CategoriaItemAtaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class ItemAtaInline(admin.TabularInline):
    model = ItemAta
    extra = 0
    fields = ('categoria', 'descricao', 'status', 'created_by', 'data_cadastro', 'ordem')
    readonly_fields = ('created_by', 'data_cadastro')


@admin.register(AtaReuniao)
class AtaReuniaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'contrato', 'autor', 'data_cadastro')
    list_filter = ('contrato', 'autor', 'data')
    search_fields = ('contrato__numero', 'resumo', 'autor__username')
    inlines = [ItemAtaInline]
    readonly_fields = ('created_by', 'updated_by', 'data_cadastro', 'data_alteracao', 'nome')


@admin.register(ItemAta)
class ItemAtaAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'ata', 'status', 'created_by', 'data_cadastro', 'ordem')
    list_filter = ('categoria', 'status')
    search_fields = ('descricao', 'ata__contrato__numero')
    readonly_fields = ('created_by', 'data_cadastro')
