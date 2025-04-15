from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import NotaPessoal

class SuperUserOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class NotaPessoalListView(LoginRequiredMixin, SuperUserOnlyMixin, ListView):
    model = NotaPessoal
    template_name = 'notaspessoais/lista_notaspessoais.html'
    context_object_name = 'notas'
    ordering = ['-criada_em']

class NotaPessoalCreateView(LoginRequiredMixin, SuperUserOnlyMixin, CreateView):
    model = NotaPessoal
    fields = ['titulo', 'texto']
    template_name = 'notaspessoais/cadastrar_notaspessoais.html'
    success_url = reverse_lazy('lista_notas')

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)

class NotaPessoalUpdateView(LoginRequiredMixin, SuperUserOnlyMixin, UpdateView):
    model = NotaPessoal
    fields = ['titulo', 'texto']
    template_name = 'notaspessoais/cadastrar_notaspessoais.html'
    success_url = reverse_lazy('lista_notas')

class NotaPessoalDeleteView(LoginRequiredMixin, SuperUserOnlyMixin, DeleteView):
    model = NotaPessoal
    template_name = 'notaspessoais/confirma_exclusao_notaspessoais.html'
    success_url = reverse_lazy('lista_notas')

class NotaPessoalDetailView(LoginRequiredMixin, SuperUserOnlyMixin, DetailView):
    model = NotaPessoal
    template_name = 'notaspessoais/detalhe_notaspessoais.html'

