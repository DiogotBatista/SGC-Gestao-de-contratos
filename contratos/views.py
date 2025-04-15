from .models import Contrato, Obra, Contratante, NotaContrato, NotaObra
from .forms import ContratoForm, ContratanteForm, ObraForm, NotaContratoForm, NotaObraForm
from django.db.models import Q, Count, Max
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView, View
from core.mixins import AccessRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from reunioes.models import AtaReuniao, ItemAta
from django.shortcuts import  get_object_or_404, redirect

# MENU
class MenuView(AccessRequiredMixin, TemplateView):
    """
    Pagina principal de contratos
    """
    allowed_cargos = []
    template_name = 'contratos/menu_contratos.html'

# VIEWS DOS CONTRATOS
class ContratoListView(AccessRequiredMixin, ListView):
    """
    Lista de contratos
    """
    allowed_cargos = []
    model = Contrato
    template_name = 'contratos/contratos/lista_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 20
    ordering = ['-data_cadastro']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        ativo = self.request.GET.get('ativo')

        if query:
            queryset = queryset.filter(
                Q(numero__icontains=query) |
                Q(contratante__nome__icontains=query)
            )

        if ativo == 'ativos':
            queryset = queryset.filter(ativo=True)
        elif ativo == 'inativos':
            queryset = queryset.filter(ativo=False)

        return queryset

class ContratoCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastrar novo contrato
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_contratos'
    model = Contrato
    form_class = ContratoForm
    template_name = 'contratos/contratos/cadastrar_contrato.html'
    success_url = reverse_lazy('lista_contratos')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Contrato cadastrado com sucesso!")
        return super().form_valid(form)

class ContratoDetailView(AccessRequiredMixin, DetailView):
    """
    Detalhes de um contrato específico
    """
    model = Contrato
    template_name = 'contratos/contratos/detalhes_contrato.html'
    context_object_name = 'contrato'
    allowed_cargos = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato = self.object

        atas = AtaReuniao.objects.filter(contrato=contrato).prefetch_related('itens')
        total_atas = atas.count()
        total_itens = ItemAta.objects.filter(ata__contrato=contrato).count()
        pendentes = ItemAta.objects.filter(ata__contrato=contrato, status='pendente').count()
        concluidos = ItemAta.objects.filter(ata__contrato=contrato, status='concluido').count()
        ultima_ata = atas.order_by('-data').first()

        context.update({
            'total_atas': total_atas,
            'total_itens': total_itens,
            'pendentes': pendentes,
            'concluidos': concluidos,
            'ultima_ata': ultima_ata,
        })
        context['nota_form'] = NotaContratoForm()
        return context

class ContratoUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualizar contrato
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_contratos'
    model = Contrato
    form_class = ContratoForm
    template_name = 'contratos/contratos/editar_contratos.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Contrato atualizado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detalhes_contrato', kwargs={'pk': self.object.pk})

class ContratoDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deletar contrato
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_contratos'
    model = Contrato
    template_name = 'contratos/contratos/excluir_contratos.html'
    success_url = reverse_lazy('lista_contratos')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Contrato excluído com sucesso!")
        return response

class AtasPorContratoView(AccessRequiredMixin, ListView):
    """
    Lista de atas do contrato
    """
    model = AtaReuniao
    template_name = 'contratos/contratos/atas_por_contrato.html'
    context_object_name = 'atas'
    allowed_cargos = []
    paginate_by = 20

    def get_queryset(self):
        return AtaReuniao.objects.filter(contrato_id=self.kwargs['pk']).select_related('contrato')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contrato'] = get_object_or_404(Contrato, pk=self.kwargs['pk'])
        return context

class ObrasPorContratoView(AccessRequiredMixin, ListView):
    """
    Lista de obras do contrato
    """
    model = Obra
    template_name = 'contratos/contratos/obras_por_contrato.html'
    context_object_name = 'obras'
    allowed_cargos = []
    paginate_by = 20

    def get_queryset(self):
        return Obra.objects.filter(contrato_id=self.kwargs['pk']).select_related('contrato')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contrato'] = get_object_or_404(Contrato, pk=self.kwargs['pk'])
        return context

#Notas nos contatos
class NotaContratoCreateView(AccessRequiredMixin, View):
    """
    Notas por contrato
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'index'

    def post(self, request, contrato_id):
        contrato = get_object_or_404(Contrato, pk=contrato_id)
        form = NotaContratoForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.contrato = contrato
            nota.criado_por = request.user
            nota.save()
            messages.success(request, 'Anotação adicionada com sucesso.')
        else:
            messages.warning(request, 'Erro ao adicionar anotação.')
        return redirect('detalhes_contrato', pk=contrato.pk)

class NotaContratoUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza a nota do contrato
    """
    allowed_cargos = ['Gestor']
    model = NotaContrato
    form_class = NotaContratoForm
    template_name = 'contratos/contratos/editar_nota.html'

    def form_valid(self, form):
        nota = form.save(commit=False)
        nota.updated_by = self.request.user
        nota.save()
        messages.success(self.request, 'Anotação atualizada com sucesso.')
        return redirect('detalhes_contrato', pk=nota.contrato.pk)

class NotaContratoDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta a nota do contrato
    """
    allowed_cargos = ['Gestor']
    model = NotaContrato
    template_name = 'contratos/contratos/excluir_nota.html'

    def get_success_url(self):
        messages.success(self.request, 'Anotação excluída com sucesso.')
        return reverse_lazy('detalhes_contrato', kwargs={'pk': self.object.contrato.pk})

# VIEWS DOS CONTRATANTES
class ContratanteListView(AccessRequiredMixin, ListView):
    """
    Lista das empresas contratantes
    """
    allowed_cargos = [] # Informar os cargos que terão acesso à esse template
    model = Contratante
    template_name = 'contratos/contratantes/lista_contratantes.html'
    context_object_name = 'contratantes'
    paginate_by = 20
    ordering = ['nome']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) |
                Q(cnpj__icontains=query)
            )
        return queryset

class ContratanteCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastro das empresas contratantes
    """
    allowed_cargos = ['Gestor'] # Informar os cargos que terão acesso à esse template
    no_permission_redirect_url = 'lista_contratantes'
    model = Contratante
    form_class = ContratanteForm
    template_name = 'contratos/contratantes/cadastrar_contratante.html'
    success_url = reverse_lazy('lista_contratantes')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Empresa cadastrada com sucesso!")
        return super().form_valid(form)

class ContratanteUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualização da empresa contratante
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_contratantes'
    model = Contratante
    form_class = ContratanteForm
    template_name = 'contratos/contratantes/editar_contratante.html'
    success_url = reverse_lazy('lista_contratantes')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Empresa atualizada com sucesso!")
        return super().form_valid(form)

class ContratanteDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta uma empresa contratante
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_contratantes'
    model = Contratante
    template_name = 'contratos/contratantes/excluir_contratante.html'
    success_url = reverse_lazy('lista_contratantes')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Empresa excluída com sucesso!")
        return response

# VIEWS DAS OBRAS
class ObraListView(AccessRequiredMixin, ListView):
    """
    Lista de obras
    """
    allowed_cargos = []
    model = Obra
    template_name = 'contratos/obras/lista_obras.html'
    context_object_name = 'obras'
    paginate_by = 20
    ordering = ['codigo']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        ativo = self.request.GET.get('ativo')
        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query) |
                Q(contrato__numero__icontains=query)|
                Q(local__icontains=query)
            )
        if ativo == 'ativas':
            queryset = queryset.filter(ativo=True)
        elif ativo == 'inativas':
            queryset = queryset.filter(ativo=False)

        return queryset

class ObraDetailView(AccessRequiredMixin, DetailView):
    """
    Detalher da obra
    """
    allowed_cargos = []
    model = Obra
    template_name = 'contratos/obras/detalhes_obra.html'
    context_object_name = 'obra'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notas'] = self.object.notas.all()
        context['form_nota'] = NotaObraForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = NotaObraForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.obra = self.object
            nota.autor = request.user
            nota.save()
        return redirect('detalhe_obra', pk=self.object.pk)

class ObraCreateView(AccessRequiredMixin, CreateView):
    """
    Cadastrar nova obra
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_obras'
    model = Obra
    form_class = ObraForm
    template_name = 'contratos/obras/cadastrar_obra.html'
    success_url = reverse_lazy('lista_obras')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Obra cadastrada com sucesso!")
        return super().form_valid(form)

class ObraUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualizar obra
    """
    allowed_cargos = ['Gestor']
    model = Obra
    form_class = ObraForm
    template_name = 'contratos/obras/editar_obra.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Obra atualizada com sucesso!")
        return response

    def get_success_url(self):
        return reverse_lazy('detalhes_obra', kwargs={'pk': self.object.pk})


class ObraDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deletar obra
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'lista_obras'
    model = Obra
    template_name = 'contratos/obras/excluir_obra.html'
    success_url = reverse_lazy('lista_obras')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Obra excluída com sucesso!")
        return response

#Notas na obras
class NotaObraCreateView(AccessRequiredMixin, View):
    """
    Adiciona anotação à obra
    """
    allowed_cargos = ['Gestor']
    no_permission_redirect_url = 'index'

    def post(self, request, obra_id):
        obra = get_object_or_404(Obra, pk=obra_id)
        form = NotaObraForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.obra = obra
            nota.criado_por = request.user
            nota.save()
            messages.success(request, 'Anotação adicionada com sucesso.')
        else:
            messages.warning(request, 'Erro ao adicionar anotação.')
        return redirect('detalhes_obra', pk=obra.pk)

class NotaObraUpdateView(AccessRequiredMixin, UpdateView):
    """
    Atualiza anotação da obra
    """
    allowed_cargos = ['Gestor']
    model = NotaObra
    form_class = NotaObraForm
    template_name = 'contratos/obras/editar_nota_obra.html'

    def form_valid(self, form):
        nota = form.save(commit=False)
        nota.save()
        messages.success(self.request, 'Anotação atualizada com sucesso.')
        return redirect('detalhes_obra', pk=nota.obra.pk)

class NotaObraDeleteView(AccessRequiredMixin, DeleteView):
    """
    Deleta anotação da obra
    """
    allowed_cargos = ['Gestor']
    model = NotaObra
    template_name = 'contratos/obras/excluir_nota_obra.html'

    def get_success_url(self):
        messages.success(self.request, 'Anotação excluída com sucesso.')
        return reverse_lazy('detalhes_obra', kwargs={'pk': self.object.obra.pk})