from  datetime import datetime
from pyexpat.errors import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from django.urls import reverse_lazy
from .models import CartaoCredito, Receita, DespesaFixa, DespesaVariavel, TotalReceitas, TotalDespesasFixas, TotalDespesasVariaveis
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas # type: ignore
from io import BytesIO, StringIO
from django.utils import timezone
from financas.forms import ReceitaModelForm, DespesaFixaModelForm, DespesaVariavelModelForm, CartaoCreditoModelForm



class ReceitaList(ListView):
    model = Receita
    template_name = 'receita_list.html'
    context_object_name = 'receitas'

    def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           # Calcula o total de todas as receitas
           context['total_receitas'] = Receita.objects.aggregate(total=Sum('valor'))['total'] or 0
           return context

class ReceitaCreate(CreateView):
    model = Receita
    form_class  = ReceitaModelForm
    template_name = 'receita_create.html'
    success_url = reverse_lazy('receitas')

class ReceitaUpdate(UpdateView):
    model = Receita
    form_class  = ReceitaModelForm
    template_name = 'receita_update.html'
    success_url = reverse_lazy('receitas')

class ReceitaDelete(DeleteView):
    model = Receita
    template_name = 'receita_delete.html'
    success_url = reverse_lazy('receitas')


# Despesa Fixa
class DespesaFixaList(ListView):
    model = DespesaFixa
    template_name = 'despesa_fixa_list.html'
    context_object_name = 'despesas_fixas'
    paginate_by = 10

    # Filtro dos dados da view
    def get_queryset(self):
        queryset = DespesaFixa.objects.all()  # Exibe todas as despesas fixas

        # Aplica os filtros a partir dos parâmetros GET na URL
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        descricao = self.request.GET.get('descricao')
        status = self.request.GET.get('status')  # Novo filtro de status

        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        if descricao:
            queryset = queryset.filter(descricao__icontains=descricao)

        if status:
            # Filtro por status de pagamento (paga ou não paga)
            if status == 'paga':
                queryset = queryset.filter(paga=True)
            elif status == 'nao_paga':
                queryset = queryset.filter(paga=False)

        return queryset

    # Adiciona o total das despesas não pagas e o total de receitas ao contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status_filtro = self.request.GET.get('status', '')

        # Calcula o total das despesas não pagas
        total_despesas_fixas = self.get_queryset().aggregate(Sum('valor'))['valor__sum'] or 0.0
        if status_filtro == 'paga':
            total_despesas_fixas_pagas = self.get_queryset().filter(paga=True).aggregate(Sum('valor'))['valor__sum'] or 0.0
            context['nome_total'] = 'Total de Despesas Pagas'
            context['total_despesas_fixas'] = total_despesas_fixas_pagas
        elif status_filtro == 'nao_paga':
            total_despesas_fixas_nao_pagas = self.get_queryset().filter(paga=False).aggregate(Sum('valor'))['valor__sum'] or 0.0
            context['nome_total'] = 'Total de Despesas Não Pagas'
            context['total_despesas_fixas'] = total_despesas_fixas_nao_pagas
        else:
            context['nome_total'] = 'Total de Despesas Fixas'
            context['total_despesas_fixas'] = total_despesas_fixas
        

        # Calcula o total das receitas (supondo que exista um modelo Receita com campo 'valor')
        total_receitas = Receita.objects.aggregate(Sum('valor'))['valor__sum'] or 0

        # Adiciona os totais ao contexto
        #context['total_despesas_fixas'] = total_despesas_fixas
        #context['total_despesas_fixas_pagas'] = total_despesas_fixas_pagas
        context['total_receitas'] = total_receitas
        #context['status'] = self.request.GET.get('status', '') 

        return context
    

class DespesaFixaCreate(CreateView):
    model = DespesaFixa
    form_class = DespesaFixaModelForm
    template_name = 'despesa_fixa_create.html'
    success_url = reverse_lazy('despesas_fixas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cartoes_credito'] = CartaoCredito.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associar despesa ao usuário logado
        return super().form_valid(form)

class DespesaFixaUpdate(UpdateView):
    model = DespesaFixa
    form_class  = DespesaFixaModelForm
    template_name = 'despesa_fixa_update.html'
    success_url = reverse_lazy('despesas_fixas')

class DespesaFixaDelete(DeleteView):
    model = DespesaFixa
    template_name = 'despesa_fixa_delete.html'
    success_url = reverse_lazy('despesas_fixas')

# Despesa Variável
class DespesaVariavelList(ListView):
    model = DespesaVariavel
    template_name = 'despesa_variavel_list.html'
    context_object_name = 'despesas_variaveis'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcula o total de todas as despesas variáveis
        context['total_despesa_variavel'] = DespesaVariavel.objects.aggregate(total=Sum('valor'))['total'] or 0
        
        return context

class DespesaVariavelCreate(CreateView):
    model = DespesaVariavel
    form_class = DespesaVariavelModelForm
    template_name = 'despesa_variavel_create.html'
    success_url = reverse_lazy('despesas_variaveis')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cartoes_credito'] = CartaoCredito.objects.all()
        return context

    def form_valid(self, form):
        # Assegura que a despesa variável está associada ao usuário atual
        form.instance.user = self.request.user
        return super().form_valid(form)

class DespesaVariavelUpdate(UpdateView):
    model = DespesaVariavel
    form_class = DespesaVariavelModelForm
    template_name = 'despesa_variavel_update.html'
    success_url = reverse_lazy('despesas_variaveis')

class DespesaVariavelDelete(DeleteView):
    model = DespesaVariavel
    template_name = 'despesa_variavel_delete.html'
    success_url = reverse_lazy('despesas_variaveis')


# Cartão de Crédito
class CartaoCreditoList(ListView):
    model = CartaoCredito
    template_name = 'cartao_credito_list.html'
    context_object_name = 'cartoe_credito'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adicionar os totais de gastos no contexto
        cartoes_com_gastos = []
        for cartao in context['cartoe_credito']:
            cartoes_com_gastos.append({
                'cartao': cartao,
                'total_gastos': cartao.total_gastos()  # Chama o método do model
            })

        context['cartoes_com_gastos'] = cartoes_com_gastos
        return context

class CartaoCreditoCreate(CreateView):
    model = CartaoCredito
    form_class  = CartaoCreditoModelForm
    template_name = 'cartao_credito_create.html'
    success_url = reverse_lazy('cartao_credito')

class CartaoCreditoUpdate(UpdateView):
    model = CartaoCredito
    form_class  = CartaoCreditoModelForm
    template_name = 'cartao_credito_update.html'
    success_url = reverse_lazy('cartao_credito')

class CartaoCreditoDelete(DeleteView):
    model = CartaoCredito
    template_name = 'cartao_credito_delete.html'
    success_url = reverse_lazy('cartao_credito')


# Totais
class TotalReceitasList(ListView):
    model = TotalReceitas
    template_name = 'total_receitas_list.html'

class TotalDespesasFixasList(ListView):
    model = TotalDespesasFixas
    template_name = 'total_despesas_fixas_list.html'

class TotalDespesasVariaveisList(ListView):
    model = TotalDespesasVariaveis
    template_name = 'total_despesas_variaveis_list.html'


class GerarRelatorioReceitas(View):
    def get(self, request, *args, **kwargs):
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        # Se as datas de início e fim forem fornecidas, filtra as receitas
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            receitas = Receita.objects.filter(data__range=(data_inicio, data_fim))
        else:
            # Caso contrário, pega todas as receitas
            receitas = Receita.objects.all()

        # Calcula o total das receitas
        total_receitas = receitas.aggregate(total=Sum('valor'))['total'] or 0

        return render(request, 'relatorio_receitas.html', {
            'receitas': receitas,  # Passa a lista de receitas
            'total_receitas': total_receitas,  # Passa o total das receitas
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'imprimir': False  # Para não mostrar o relatório automaticamente
        })

class GerarRelatorioDespesasFixas(View):
    def get(self, request, *args, **kwargs):
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            despesas = DespesaFixa.objects.filter(data__range=(data_inicio, data_fim))
        else:
            despesas = DespesaFixa.objects.all()

        # Calcular o total das despesas
        #total_despesas = despesas.aggregate(total=Sum('valor'))['total'] or 0

        # Calcular o total das despesas não pagas
        total_despesas_fixas= despesas.filter(paga=False).aggregate(total=Sum('valor'))['total'] or 0

        # Calcular o total das despesas pagas
        total_despesas_pagas = despesas.filter(paga=True).aggregate(total=Sum('valor'))['total'] or 0

        # Calcular o total de receitas
        total_receitas = Receita.objects.aggregate(total=Sum('valor'))['total'] or 0

        return render(request, 'relatorio_despesas_fixas.html', {
            'despesas': despesas,
            #'total_despesas': total_despesas,
            'total_despesas_fixas': total_despesas_fixas,
            'total_despesas_pagas': total_despesas_pagas,
            'total_receitas': total_receitas,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'imprimir': False  # Para não mostrar o relatório automaticamente
        })

class GerarRelatorioDespesasVariaveis(View):
    def get(self, request, *args, **kwargs):
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            despesas = DespesaVariavel.objects.filter(data__range=(data_inicio, data_fim))
        else:
            despesas = DespesaVariavel.objects.all()

        total_despesas = despesas.aggregate(total=Sum('valor'))['total'] or 0

        return render(request, 'relatorio_despesas_variavel.html', {
            'despesas': despesas,
            'total_despesas': total_despesas,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'imprimir': False  # Para não mostrar o relatório automaticamente
        })


class HomeView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        # Calculando o total de receitas
        total_receitas = Receita.objects.aggregate(total=Sum('valor'))['total'] or 0
        
        # Calculando os totais de despesas fixas e variáveis
        total_despesas_fixas = DespesaFixa.objects.aggregate(total=Sum('valor'))['total'] or 0
        total_despesas_variaveis = DespesaVariavel.objects.aggregate(total=Sum('valor'))['total'] or 0
        
        # Calculando o total de despesas gerais (soma de fixas e variáveis)
        total_despesas_gerais = total_despesas_fixas + total_despesas_variaveis
        
        # Calculando a diferença entre receitas e despesas
        total_despesas = total_despesas_gerais  # Agora usamos o total de despesas gerais
        diferenca = total_receitas - total_despesas
        diferenca_abs = abs(diferenca)  # Calculando o valor absoluto da diferença

        # Criando o contexto para passar para o template
        context = {
            'total_receitas': total_receitas,
            'total_despesas_fixas': total_despesas_fixas,
            'total_despesas_variaveis': total_despesas_variaveis,
            'total_despesas_gerais': total_despesas_gerais,  # Passando o total de despesas gerais
            'diferenca': diferenca,
            'diferenca_abs': diferenca_abs,  # Passando o valor absoluto para o template
        }

        return render(request, self.template_name, context)
    
class MarcarComoPagoView(RedirectView):
    url = reverse_lazy('despesas_fixas')  # Redireciona para a lista de despesas

    def get_redirect_url(self, *args, **kwargs):
        # Obtém a despesa com o ID fornecido na URL
        despesa_fixa = DespesaFixa.objects.get(pk=kwargs['pk'])
        
        # Marca a despesa como paga
        despesa_fixa.paga = True
        despesa_fixa.save()

        # Atualiza o total das despesas não pagas
        total_despesas_fixas = DespesaFixa.objects.filter(paga=False).aggregate(Sum('valor'))['valor__sum'] or 0
        
        

        # Redireciona de volta para a lista de despesas com o total atualizado
        return super().get_redirect_url(*args, **kwargs)