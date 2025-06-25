from django.contrib import admin
from .models import ErroSistema

@admin.register(ErroSistema)
class ErroSistemaAdmin(admin.ModelAdmin):
    list_display = ('data', 'view', 'usuario', 'mensagem_curta', 'suporte')
    search_fields = ('view', 'usuario', 'mensagem', 'stack_trace')
    list_filter = ('usuario', 'view', 'data')
    readonly_fields = ('data', 'view', 'usuario', 'mensagem', 'stack_trace')

    def mensagem_curta(self, obj):
        return (obj.mensagem[:60] + '...') if len(obj.mensagem) > 60 else obj.mensagem
    mensagem_curta.short_description = "Mensagem"

    def suporte(self, obj):
        return "🚨"
    suporte.short_description = "!"
