from django.contrib import admin
from .models import Empresa, Contratante, Contrato, Obra

admin.site.register(Empresa)
admin.site.register(Contratante)
admin.site.register(Contrato)
admin.site.register(Obra)

