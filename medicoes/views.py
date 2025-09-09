# medicoes/views.py
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import AccessRequiredMixin, ContratoAccessMixin

from .forms import MedicaoForm
# from teste_openrouter import response
from .models import Medicao


class MedicaoListView(AccessRequiredMixin, ListView):
    model = Medicao
    template_name = "medicoes/lista_medicoes.html"
    context_object_name = "medicoes"
    ordering = ["-data_inicio"]
    allowed_cargos = []
    view_name = "lista_medicoes"
    paginate_by = 20

    def get_queryset(self):
        contratos_permitidos = self.request.user.userprofile.contratos.all()
        queryset = super().get_queryset().filter(contrato__in=contratos_permitidos)
        contrato = self.request.GET.get("contrato")
        situacao = self.request.GET.get("situacao")
        periodo = self.request.GET.get("periodo")

        if contrato:
            queryset = queryset.filter(contrato__numero__icontains=contrato)
        if situacao:
            queryset = queryset.filter(situacao=situacao)
        if periodo:
            queryset = queryset.filter(periodo__icontains=periodo)

        return queryset


class MedicaoCreateView(AccessRequiredMixin, CreateView):
    model = Medicao
    form_class = MedicaoForm
    template_name = "medicoes/cadastrar_medicao.html"
    success_url = reverse_lazy("lista_medicoes")
    allowed_cargos = []
    view_name = "criar_medicao"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Medição do período {self.object.periodo_formatado} cadastrada com sucesso no contrato {self.object.contrato}.",
        )
        return response


class MedicaoUpdateView(AccessRequiredMixin, ContratoAccessMixin, UpdateView):
    model = Medicao
    form_class = MedicaoForm
    template_name = "medicoes/editar_medicao.html"
    success_url = reverse_lazy("lista_medicoes")
    allowed_cargos = []
    view_name = "atualizar_medicao"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.info(
            self.request, f"Medição {self.object.identificador} atualizada com sucesso!"
        )
        return response


class MedicaoDeleteView(AccessRequiredMixin, ContratoAccessMixin, DeleteView):
    model = Medicao
    template_name = "medicoes/excluir_medicao.html"
    success_url = reverse_lazy("lista_medicoes")
    allowed_cargos = []
    view_name = "deletar_medicao"

    def form_valid(self, form):
        identificador = self.object.identificador
        response = super().form_valid(form)
        messages.warning(self.request, f"Medição {identificador} excluída com sucesso!")
        return response


@csrf_exempt
def api_powerbi_medicoes(request):
    TOKEN_ESPERADO = "8d6e6258-142c-4118-b8a7-03567b7363b3"

    token = request.GET.get("token")
    if token != TOKEN_ESPERADO:
        return HttpResponseForbidden("Acesso negado")

    medicoes = Medicao.objects.select_related("contrato").all()
    dados = [
        {
            "contrato": m.contrato.numero,
            "identificador": m.identificador,
            "data_inicio": m.data_inicio.strftime("%Y-%m-%d"),
            "data_fim": m.data_fim.strftime("%Y-%m-%d"),
            "periodo_formatado": m.periodo_formatado,  # "20/03/25 a 21/04/25"
            "valor": float(m.valor),
            "situacao": m.get_situacao_display(),
            "criado_em": m.criado_em.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for m in medicoes
    ]

    return JsonResponse(dados, safe=False)
