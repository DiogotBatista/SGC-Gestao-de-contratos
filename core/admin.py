from django.contrib import admin
from .models import UserProfile, Cargo, ViewDisponivel, PermissaoDeAcessoPorCargo

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cargo', 'empresa']
    list_filter = ['cargo', 'empresa']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(ViewDisponivel)
class ViewDisponivelAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(PermissaoDeAcessoPorCargo)
class PermissaoDeAcessoPorCargoAdmin(admin.ModelAdmin):
    list_display = ['cargo']
    filter_horizontal = ['views']
    search_fields = ['cargo__nome']
