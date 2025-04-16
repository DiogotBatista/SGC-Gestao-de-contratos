from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from .models import Tarefa
from .forms import TarefaForm
from core.mixins import AccessRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View


class TarefaBoardView(AccessRequiredMixin, View):
    allowed_cargos = []
    no_permission_redirect_url = 'index'

    def get(self, request):
        tarefas = Tarefa.objects.filter(autor=request.user)
        form = TarefaForm()
        return render(request, 'tarefas/gerenciar_tarefas.html', {'tarefas': tarefas, 'form': form})

@require_http_methods(["POST"])
def criar_tarefa(request):
    form = TarefaForm(request.POST)
    if form.is_valid():
        tarefa = form.save(commit=False)
        tarefa.autor = request.user
        tarefa.save()
        html = render_to_string("tarefas/partials/tarefa_item.html", {'tarefa': tarefa})
        return HttpResponse(html)
    return JsonResponse({'erro': 'Dados inválidos'}, status=400)

@require_http_methods(["POST"])
def alternar_status_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    tarefa.concluida = not tarefa.concluida
    tarefa.save()
    html = render_to_string("tarefas/partials/tarefa_item.html", {'tarefa': tarefa})
    return HttpResponse(html)



@require_http_methods(["POST"])
def excluir_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    tarefa.delete()
    return HttpResponse("")



@require_http_methods(["POST"])
def editar_tarefa(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, autor=request.user)
    form = TarefaForm(request.POST, instance=tarefa)
    if form.is_valid():
        form.save()
        html = render_to_string("tarefas/partials/tarefa_item.html", {'tarefa': tarefa})
        return HttpResponse(html)
    return JsonResponse({'erro': 'Erro ao editar'}, status=400)
