# senhas/views.py
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib import messages

from core.mixins import SuperUserOnlyMixin
from .models import PasswordEntry
from .forms import PasswordEntryForm


class SenhaListView(LoginRequiredMixin, SuperUserOnlyMixin, ListView):
    model = PasswordEntry
    template_name = 'senhas/lista_senhas.html'
    ordering = ['-updated_at']
    paginate_by = 12
    # (lista não precisa de context_object_name='obj')

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get('q') or '').strip()
        if q:
            qs = qs.filter(titulo__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = (self.request.GET.get('q') or '').strip()
        paginator = ctx.get('paginator')
        ctx['total'] = paginator.count if paginator else self.get_queryset().count()
        return ctx


class SenhaCreateView(LoginRequiredMixin, SuperUserOnlyMixin, CreateView):
    model = PasswordEntry
    form_class = PasswordEntryForm
    template_name = 'senhas/cadastrar_senha.html'
    success_url = reverse_lazy('lista_senhas')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        resp = super().form_valid(form)
        messages.success(self.request, "Senha cadastrada com sucesso.")
        return resp

    def form_invalid(self, form):
        messages.error(self.request, "Verifique os campos destacados.")
        return super().form_invalid(form)


class SenhaDetailView(LoginRequiredMixin, SuperUserOnlyMixin, DetailView):
    model = PasswordEntry
    template_name = 'senhas/detalhe_senha.html'
    context_object_name = 'obj'   # 👈 importante


class SenhaUpdateView(LoginRequiredMixin, SuperUserOnlyMixin, UpdateView):
    model = PasswordEntry
    form_class = PasswordEntryForm
    template_name = 'senhas/editar_senha.html'
    context_object_name = 'obj'   # 👈 importante
    # Se quiser voltar para o detalhe após salvar:
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        resp = super().form_valid(form)
        messages.info(self.request, "Senha atualizada com sucesso.")
        return resp

    def get_success_url(self):
        return reverse_lazy('detalhe_senha', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, "Verifique os campos destacados.")
        return super().form_invalid(form)


class SenhaDeleteView(LoginRequiredMixin, SuperUserOnlyMixin, DeleteView):
    model = PasswordEntry
    template_name = 'senhas/confirma_exclusao_senha.html'
    context_object_name = 'obj'   # 👈 se seu template usa {{ obj }}
    success_url = reverse_lazy('lista_senhas')

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.warning(self.request, "Senha excluída com sucesso.")
        return resp


class RevelarSenhaView(LoginRequiredMixin, SuperUserOnlyMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(PasswordEntry, pk=pk)
        return JsonResponse({'senha': obj.get_plain_password()})

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])
