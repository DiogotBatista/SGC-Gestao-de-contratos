from django.contrib import admin
from .models import Empresa, Contratante, Contrato, Obra, AndamentoContrato

admin.site.register(Empresa)
admin.site.register(Contratante)
admin.site.register(Contrato)
admin.site.register(Obra)
admin.site.register(AndamentoContrato)
