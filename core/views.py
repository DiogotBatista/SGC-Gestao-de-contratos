from contratos.models import Contrato
from django.db.models import Count
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.password_validation import password_validators_help_texts
from django.views.generic import TemplateView
from .mixins import AccessRequiredMixin
from .models import Aviso

class IndexView(AccessRequiredMixin, TemplateView):
    template_name = "index.html"
    allowed_cargos = []
    view_name = 'index'
    no_permission_redirect_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Página Inicial"
        context["avisos"] = Aviso.objects.filter(ativo=True)
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regras_senha'] = password_validators_help_texts()
        return context
