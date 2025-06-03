from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.mixins import AccessRequiredMixin, ContratoAccessMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, TemplateView, UpdateView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from collections import defaultdict
from .models import AtaReuniao, ItemAta, ArquivoAta
from .forms import AtaReuniaoForm, ItemAtaFormSet
from .utils_google_drive import create_folder_for_ata, upload_file_to_drive, delete_file_in_drive, delete_folder_in_drive
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils_ai import gerar_resumo_ata

class MenuAtasView(AccessRequiredMixin, TemplateView):
    template_name = 'reunioes/menu_atas.html'
    allowed_cargos = []
    view_name = 'menu_atas'

@method_decorator(login_required, name='dispatch')
class AtaReuniaoCreateView(AccessRequiredMixin, View):
    allowed_cargos = ['Gestor']
    view_name = 'criar_atas'
    template_name = 'reunioes/cadastrar_ata.html'
    no_permission_redirect_url = 'lista_atas'

    def get(self, request):
        ata_form = AtaReuniaoForm(user=request.user)
        formset = ItemAtaFormSet(prefix='form')
        return render(request, self.template_name, {'form': ata_form, 'formset': formset})

    def post(self, request):
        ata_form = AtaReuniaoForm(request.POST, request.FILES, user=request.user)
        formset = ItemAtaFormSet(request.POST, prefix='form')

        if ata_form.is_valid() and formset.is_valid():
            ata = ata_form.save(commit=False)
            ata.autor = request.user
            ata.created_by = request.user
            ata.updated_by = request.user
            ata.save()

            # Criar pasta no Google Drive para esta ata
            nome_pasta = f"Ata - {ata.contrato.numero} - {ata.data.strftime('%d-%m-%Y')} - ID{ata.pk}"
            pasta_id = create_folder_for_ata(nome_pasta)

            # Upload de arquivos enviados
            arquivos = request.FILES.getlist('arquivos')
            for arquivo in arquivos:
                link_drive, file_id = upload_file_to_drive(arquivo, arquivo.name, pasta_id)
                ArquivoAta.objects.create(
                    ata=ata,
                    nome=arquivo.name,
                    link_arquivo=link_drive,
                    id_arquivo_drive=file_id,
                    id_pasta_drive=pasta_id
                )

            # Salvar os itens da ata
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

            messages.success(request, 'Ata cadastrada com sucesso.')
            return redirect('lista_atas')

        return render(request, self.template_name, {'form': ata_form, 'formset': formset})

class AtaReuniaoUpdateView(AccessRequiredMixin, ContratoAccessMixin, UpdateView):
    model = AtaReuniao
    form_class = AtaReuniaoForm
    template_name = 'reunioes/editar_ata.html'
    allowed_cargos = []
    view_name = 'atualizar_atas'
    no_permission_redirect_url = 'lista_atas'


    def get(self, request, pk):
        ata = get_object_or_404(AtaReuniao, pk=pk)
        form = AtaReuniaoForm(instance=ata, user=request.user)
        formset = ItemAtaFormSet(instance=ata, prefix='form')
        return render(request, self.template_name, {'form': form, 'formset': formset, 'ata': ata})

    def post(self, request, pk):
        ata = get_object_or_404(AtaReuniao, pk=pk)
        form = AtaReuniaoForm(request.POST, request.FILES, instance=ata, user=request.user)
        formset = ItemAtaFormSet(request.POST, instance=ata, prefix='form')

        if form.is_valid() and formset.is_valid():
            ata = form.save(commit=False)
            ata.updated_by = request.user
            ata.save()

            # Upload de novos arquivos (adiciona à pasta existente)
            arquivos = request.FILES.getlist('arquivos')
            pasta_id = ata.arquivos.first().id_pasta_drive if ata.arquivos.exists() else None
            if not pasta_id:
                nome_pasta = f"Ata - {ata.contrato.numero} - {ata.data.strftime('%d-%m-%Y')} - ID{ata.pk}"
                pasta_id = create_folder_for_ata(nome_pasta)

            for arquivo in arquivos:
                link_drive, file_id = upload_file_to_drive(arquivo, arquivo.name, pasta_id)
                ArquivoAta.objects.create(
                    ata=ata,
                    nome=arquivo.name,
                    link_arquivo=link_drive,
                    id_arquivo_drive=file_id,
                    id_pasta_drive=pasta_id
                )

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
            next_url = request.POST.get('next')
            if next_url:
                return redirect(f"{reverse('detalhe_ata', args=[ata.pk])}?next={next_url}")
            return redirect('detalhe_ata', pk=ata.pk)

        return render(request, self.template_name, {'form': form, 'formset': formset, 'ata': ata})

class AtaReuniaoListView(AccessRequiredMixin, ListView):
    model = AtaReuniao
    template_name = 'reunioes/lista_atas.html'
    context_object_name = 'atas'
    paginate_by = 10
    ordering = ['-data']
    allowed_cargos = []
    view_name = 'lista_atas'

    def get_queryset(self):
        contratos_permitidos = self.request.user.userprofile.contratos.all()
        queryset = super().get_queryset().select_related('contrato', 'autor').filter(contrato__in=contratos_permitidos)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(contrato__numero__icontains=query) |
                Q(contrato__contratante__nome__icontains=query) |
                Q(resumo__icontains=query)
            )
        return queryset

class AtaReuniaoDetailView(AccessRequiredMixin, ContratoAccessMixin, DetailView):
    model = AtaReuniao
    template_name = 'reunioes/detalhe_ata.html'
    context_object_name = 'ata'
    allowed_cargos = []
    view_name = 'detalhe_atas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.select_related('categoria').all()
        context['arquivos'] = self.object.arquivos.all()
        return context

class AtaReuniaoDeleteView(AccessRequiredMixin, ContratoAccessMixin, DeleteView):
    model = AtaReuniao
    template_name = 'reunioes/excluir_ata.html'
    success_url = reverse_lazy('lista_atas')
    allowed_cargos = []
    view_name = 'deletar_atas'
    no_permission_redirect_url = 'lista_atas'

    def form_valid(self, form):
        ata = self.object
        # Excluir a pasta e arquivos no Drive
        pasta_id = ata.arquivos.first().id_pasta_drive if ata.arquivos.exists() else None
        if pasta_id:
            delete_folder_in_drive(pasta_id)
        messages.success(self.request, 'Ata excluída com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return str(next_url)
        return reverse('lista_atas')


class AtasAgrupadasView(AccessRequiredMixin, View):
    template_name = 'reunioes/atas_agrupadas.html'
    allowed_cargos = []
    view_name = 'atas_agrupadas'

    def get(self, request):
        contratos_permitidos = request.user.userprofile.contratos.all()
        atas = AtaReuniao.objects.select_related('contrato', 'contrato__contratante').prefetch_related('itens').filter(
            contrato__in=contratos_permitidos)

        agrupado = defaultdict(list)
        for ata in atas:
            ata.itens_pendentes = ata.itens.filter(status='pendente').count()
            agrupado[ata.contrato].append(ata)

        atas_grouped = dict(sorted(agrupado.items(), key=lambda c: c[0].numero))

        return render(request, self.template_name, {
            'atas_grouped': atas_grouped
        })

@require_POST
def excluir_arquivo_ata(request, pk):
    arquivo = get_object_or_404(ArquivoAta, pk=pk)
    ata_pk = arquivo.ata.pk
    try:
        delete_file_in_drive(arquivo.id_arquivo_drive)
        arquivo.delete()
        messages.success(request, "Arquivo excluído com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao excluir o arquivo: {e}")
    return HttpResponseRedirect(reverse('detalhe_ata', args=[ata_pk]))

@require_POST
def adicionar_arquivos_ata(request, pk):
    ata = get_object_or_404(AtaReuniao, pk=pk)
    arquivos = request.FILES.getlist('arquivos')

    if not arquivos:
        messages.warning(request, "Nenhum arquivo selecionado.")
        return redirect('detalhe_ata', pk=pk)

    # Usa a pasta existente da ata ou cria uma nova se não existir
    pasta_id = ata.arquivos.first().id_pasta_drive if ata.arquivos.exists() else None
    if not pasta_id:
        nome_pasta = f"Ata - {ata.contrato.numero} - {ata.data.strftime('%d-%m-%Y')} - ID{ata.pk}"
        pasta_id = create_folder_for_ata(nome_pasta)

    for arquivo in arquivos:
        link_drive, file_id = upload_file_to_drive(arquivo, arquivo.name, pasta_id)
        ArquivoAta.objects.create(
            ata=ata,
            nome=arquivo.name,
            link_arquivo=link_drive,
            id_arquivo_drive=file_id,
            id_pasta_drive=pasta_id
        )

    messages.success(request, f"{len(arquivos)} arquivo(s) anexado(s) com sucesso.")
    return redirect('detalhe_ata', pk=pk)

@method_decorator(csrf_exempt, name='dispatch')
class GerarResumoIAView(View):
    def post(self, request, ata_id):
        try:
            resumo = gerar_resumo_ata(ata_id)
            return JsonResponse({"resumo": resumo})
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)

