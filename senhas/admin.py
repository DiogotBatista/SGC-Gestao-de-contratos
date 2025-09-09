from django.contrib import admin

from .models import PasswordEntry


@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "url", "ativo", "updated_at")
    search_fields = ("titulo", "usuario", "url", "observacoes")
    list_filter = ("ativo", "updated_at")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "senha_encriptada",
    )
