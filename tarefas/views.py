from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from core.mixins import AccessRequiredMixin

from .forms import TarefaForm
from .models import Tarefa


class TarefaBoardView(AccessRequiredMixin, ListView):
    model = Tarefa
    template_name = "tarefas/gerenciar_tarefas.html"
    context_object_name = "tarefas"

    def get_queryset(self):
        return Tarefa.objects.filter(autor=self.request.user).order_by("criada_em")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TarefaForm()
        return context


@require_http_methods(["POST"])
def criar_tarefa(request):
    form = TarefaForm(request.POST)
    if form.is_valid():
        tarefa = form.save(commit=False)
        tarefa.autor = request.user
        tarefa.save()
        html = render_to_string("tarefas/partials/tarefa_item.html", {"tarefa": tarefa})
        return HttpResponse(html)
    return JsonResponse({"erro": "Dados inválidos"}, status=400)


@require_http_methods(["POST"])
def alternar_status_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    tarefa.concluida = not tarefa.concluida
    tarefa.save()
    html = render_to_string("tarefas/partials/tarefa_item.html", {"tarefa": tarefa})
    return HttpResponse(html)


@require_http_methods(["POST"])
def excluir_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    tarefa.delete()
    return HttpResponse(status=204)


@require_http_methods(["POST"])
def editar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    form = TarefaForm(request.POST, instance=tarefa)
    if form.is_valid():
        form.save()
        html = render_to_string("tarefas/partials/tarefa_item.html", {"tarefa": tarefa})
        return HttpResponse(html)
    return JsonResponse({"erro": "Erro ao editar"}, status=400)
