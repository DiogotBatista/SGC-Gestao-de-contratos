from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.mixins import AccessRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, TemplateView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from collections import defaultdict
from .models import AtaReuniao, ItemAta
from .forms import AtaReuniaoForm, ItemAtaFormSet

class MenuAtasView(AccessRequiredMixin, TemplateView):
    """
    Menu de atas
    """
    template_name = 'reunioes/menu_atas.html'
    allowed_cargos = []
    view_name = 'menu_atas'

@method_decorator(login_required, name='dispatch')
class AtaReuniaoCreateView(AccessRequiredMixin, View):
    """
    Cria Ata de reunião
    """
    allowed_cargos = ['Gestor']
    view_name = 'criar_atas'
    template_name = 'reunioes/cadastrar_ata.html'
    no_permission_redirect_url = 'index'

    def get(self, request):
        ata_form = AtaReuniaoForm()
        formset = ItemAtaFormSet(prefix='form')
        return render(request, self.template_name, {'form': ata_form, 'formset': formset})

    def post(self, request):
        ata_form = AtaReuniaoForm(request.POST)
        formset = ItemAtaFormSet(request.POST, prefix='form')

        if ata_form.is_valid() and formset.is_valid():
            ata = ata_form.save(commit=False)
            ata.autor = request.user
            ata.created_by = request.user
            ata.updated_by = request.user
            ata.save()

            for form_item in formset.forms:
                instance = form_item.instance
                cleaned_data = form_item.cleaned_data

                if cleaned_data.get('DELETE') and instance.pk:
                    instance.delete()
                    continue

                if cleaned_data and not cleaned_data.get('DELETE', False):
                    item = form_item.save(commit=False)
                    item.ata = ata
                    item.ordem = cleaned_data.get('ordem') or 0  # ← pega a ordem do form
                    if not item.pk:
                        item.created_by = request.user
                    item.save()

            messages.success(request, 'Ata cadastrada com sucesso.')
            return redirect('lista_atas')

        return render(request, self.template_name, {'form': ata_form, 'formset': formset})

class AtaReuniaoListView(AccessRequiredMixin, ListView):
    """
    Lista de atas
    """
    model = AtaReuniao
    template_name = 'reunioes/lista_atas.html'
    context_object_name = 'atas'
    paginate_by = 10
    ordering = ['-data']
    allowed_cargos = []
    view_name = 'lista_atas'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('contrato', 'autor')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(contrato__numero__icontains=query) |
                Q(contrato__contratante__nome__icontains=query) |
                Q(resumo__icontains=query)
            )
        return queryset

class AtaReuniaoDetailView(AccessRequiredMixin, DetailView):
    """
    Detalhes da ata
    """
    model = AtaReuniao
    template_name = 'reunioes/detalhe_ata.html'
    context_object_name = 'ata'
    allowed_cargos = []
    view_name = 'detalhe_atas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.select_related('categoria').all()
        return context

class AtaReuniaoUpdateView(AccessRequiredMixin, View):
    """
    Atualização de ata
    """
    allowed_cargos = []
    view_name = 'atualizar_atas'
    template_name = 'reunioes/editar_ata.html'
    no_permission_redirect_url = 'lista_atas'

    def get(self, request, pk):
        ata = get_object_or_404(AtaReuniao, pk=pk)
        form = AtaReuniaoForm(instance=ata)
        formset = ItemAtaFormSet(instance=ata, prefix='form')
        return render(request, self.template_name, {'form': form, 'formset': formset, 'ata': ata})

    def post(self, request, pk):
        ata = get_object_or_404(AtaReuniao, pk=pk)
        form = AtaReuniaoForm(request.POST, instance=ata)
        formset = ItemAtaFormSet(request.POST, instance=ata, prefix='form')

        if form.is_valid() and formset.is_valid():
            ata = form.save(commit=False)
            ata.updated_by = request.user
            ata.save()

            for form_item in formset.forms:
                instance = form_item.instance
                cleaned_data = form_item.cleaned_data

                if cleaned_data.get('DELETE') and instance.pk:
                    instance.delete()
                    continue

                if cleaned_data and not cleaned_data.get('DELETE', False):
                    item = form_item.save(commit=False)
                    item.ata = ata
                    item.ordem = cleaned_data.get('ordem') or 0
                    if not item.pk:
                        item.created_by = request.user
                    item.save()

            messages.success(request, 'Ata atualizada com sucesso.')
            return redirect('detalhe_ata', pk=ata.pk)

        return render(request, self.template_name, {'form': form, 'formset': formset, 'ata': ata})

class AtaReuniaoDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deletar atas
    """
    model = AtaReuniao
    template_name = 'reunioes/excluir_ata.html'
    success_url = reverse_lazy('lista_atas')
    allowed_cargos = []
    view_name = 'deletar_atas'
    no_permission_redirect_url = 'lista_atas'

    def form_valid(self, form):
        messages.success(self.request, 'Ata excluída com sucesso.')
        return super().form_valid(form)

class AtasAgrupadasView(AccessRequiredMixin, View):
    """
    atas agrupadas por contrato
    """
    template_name = 'reunioes/atas_agrupadas.html'
    allowed_cargos = []
    view_name = 'atas_agrupadas'

    def get(self, request):
        atas = AtaReuniao.objects.select_related('contrato', 'contrato__contratante').prefetch_related('itens')

        agrupado = defaultdict(list)
        for ata in atas:
            ata.itens_pendentes = ata.itens.filter(status='pendente').count()
            agrupado[ata.contrato].append(ata)

        # ordena os contratos pelo número
        atas_grouped = dict(sorted(agrupado.items(), key=lambda c: c[0].numero))

        return render(request, self.template_name, {
            'atas_grouped': atas_grouped
        })