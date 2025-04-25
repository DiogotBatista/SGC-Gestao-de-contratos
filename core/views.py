from django.views.generic import TemplateView
from contratos.models import Contrato
from django.db.models import Count
from .mixins import AccessRequiredMixin  # ajuste o path se estiver em outro app
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.password_validation import password_validators_help_texts

class DashboardView(AccessRequiredMixin, TemplateView):
    template_name = "index.html"
    allowed_cargos = []  # ou outros cargos permitidos
    view_name = 'index'
    no_permission_redirect_url = 'login'  # ou outra página apropriada

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contratos_ativos = Contrato.objects.filter(ativo=True).prefetch_related("obras", "contratante")

        cards_contratos = []
        for contrato in contratos_ativos:
            obras = contrato.obras.all()
            execucoes = [obra.porcentagem_execucao for obra in obras if obra.porcentagem_execucao is not None]
            media_execucao = round(sum(execucoes) / len(execucoes), 2) if execucoes else 0

            cards_contratos.append({
                "id": contrato.id,
                "numero": contrato.numero,
                "contratante": contrato.contratante.nome,
                "preposto": contrato.preposto,
                "valor": contrato.valor_total or 0,
                "quantidade_obras": obras.count(),
                "media_execucao": media_execucao,
            })

        context["cards_contratos"] = cards_contratos
        return context



class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regras_senha'] = password_validators_help_texts()
        return context
