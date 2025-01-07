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
from financas.forms import ReceitaModelForm, DespesaFixaModelForm, DespesaVariavelModelForm, CartaoCreditoModelForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required(login_url='login'), name='dispatch')
class ReceitaList(ListView):
    model = Receita
    template_name = 'receita_list.html'
    context_object_name = 'receitas'

    def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           # Calcula o total de todas as receitas
           context['total_receitas'] = Receita.objects.aggregate(total=Sum('valor'))['total'] or 0
           return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class ReceitaCreate(CreateView):
    model = Receita
    form_class  = ReceitaModelForm
    template_name = 'receita_create.html'
    success_url = reverse_lazy('receitas')

@method_decorator(login_required(login_url='login'), name='dispatch')
class ReceitaUpdate(UpdateView):
    model = Receita
    form_class  = ReceitaModelForm
    template_name = 'receita_update.html'
    success_url = reverse_lazy('receitas')

@method_decorator(login_required(login_url='login'), name='dispatch')
class ReceitaDelete(DeleteView):
    model = Receita
    template_name = 'receita_delete.html'
    success_url = reverse_lazy('receitas')


@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaFixaList(ListView):
    model = DespesaFixa
    template_name = 'despesa_fixa_list.html'
    context_object_name = 'despesas_fixas'
    #paginate_by = 10

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
        #context['total_receitas'] = total_receitas
        #context['status'] = self.request.GET.get('status', '') 

        return context
    
@method_decorator(login_required(login_url='login'), name='dispatch')
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
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaFixaUpdate(UpdateView):
    model = DespesaFixa
    form_class = DespesaFixaModelForm
    template_name = 'despesa_fixa_update.html'
    success_url = reverse_lazy('despesas_fixas')

    def form_valid(self, form):
        # Obtém a instância atual do formulário sem salvar ainda
        despesa_fixa = form.save(commit=False)
        
        # Obtém a instância original da despesa fixa
        despesa_original = DespesaFixa.objects.get(pk=self.object.pk)
        
        # Calcula a diferença no valor da despesa
        valor_diferenca = despesa_fixa.valor - despesa_original.valor

        # Se houver diferença no valor e o cartão estiver associado, atualiza o total do cartão
        if valor_diferenca != 0 and despesa_fixa.cartao_credito:
            cartao_credito = despesa_fixa.cartao_credito
            cartao_credito.valor_total += valor_diferenca
            cartao_credito.save()

        # Verifica se o status de pagamento foi alterado
        if despesa_fixa.paga != despesa_original.paga:
            if despesa_fixa.paga:
                # Marcada como paga
                despesa_fixa.marcar_como_pago()
            else:
                # Marcada como não paga
                despesa_fixa.marcar_como_nao_pago()

        # Salva a instância da despesa fixa com as alterações
        despesa_fixa.save()

        # Retorna a resposta padrão para a validação do formulário
        return super().form_valid(form)

@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaFixaDelete(DeleteView):
    model = DespesaFixa
    template_name = 'despesa_fixa_delete.html'
    success_url = reverse_lazy('despesas_fixas')

@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaVariavelList(ListView):
    model = DespesaVariavel
    template_name = 'despesa_variavel_list.html'
    context_object_name = 'despesas_variaveis'
    #paginate_by = 10

    # Filtro dos dados da view
    def get_queryset(self):
        queryset = DespesaVariavel.objects.all()  # Exibe todas as despesas fixas

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
            if status == 'pago':
                queryset = queryset.filter(paga=True)
            elif status == 'nao_pago':
                queryset = queryset.filter(paga=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status_filtro = self.request.GET.get('status', '')

        # Calcula o total das despesas não pagas
        total_despesas_variaveis = self.get_queryset().aggregate(Sum('valor'))['valor__sum'] or 0.0
        if status_filtro == 'pago':
            total_despesas_variaveis_pagas = self.get_queryset().filter(paga=True).aggregate(Sum('valor'))['valor__sum'] or 0.0
            context['nome_total'] = 'Total de Despesas Pagas'
            context['total_despesas_variaveis'] = total_despesas_variaveis_pagas
        elif status_filtro == 'nao_pago':
            total_despesas_variaveis_nao_pagas = self.get_queryset().filter(paga=False).aggregate(Sum('valor'))['valor__sum'] or 0.0
            context['nome_total'] = 'Total de Despesas Não Pagas'
            context['total_despesas_variaveis'] = total_despesas_variaveis_nao_pagas
        else:
            context['nome_total'] = 'Total de Despesas Variaveis'
            context['total_despesas_variaveis'] = total_despesas_variaveis
        

        # Calcula o total das receitas (supondo que exista um modelo Receita com campo 'valor')
        total_receitas = Receita.objects.aggregate(Sum('valor'))['valor__sum'] or 0

        # Adiciona os totais ao contexto
        context['total_despesas_variaveis'] = total_despesas_variaveis
        context['total_despesas_variaveis_pagas'] = total_despesas_variaveis 
        context['total_receitas'] = total_receitas
        context['status'] = self.request.GET.get('status', '') 

        return context

@method_decorator(login_required(login_url='login'), name='dispatch')
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

@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaVariavelUpdate(UpdateView):
    model = DespesaVariavel
    form_class = DespesaVariavelModelForm
    template_name = 'despesa_variavel_update.html'
    success_url = reverse_lazy('despesas_variaveis')

@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaVariavelUpdate(UpdateView):
        model = DespesaVariavel
        form_class = DespesaVariavelModelForm
        template_name = 'despesa_variavel_update.html'
        success_url = reverse_lazy('despesas_variaveis')

        def form_valid(self, form):
            despesa_variavel = form.save(commit=False)  # Não salva automaticamente
            despesa_original = DespesaVariavel.objects.get(pk=self.object.pk)

        # Calcula a diferença no valor
            valor_diferenca = despesa_variavel.valor - despesa_original.valor

        # Ajusta o total do cartão apenas se houver diferença de valor
            if valor_diferenca != 0 and despesa_variavel.cartao_credito:
                cartao_credito = despesa_variavel.cartao_credito
                cartao_credito.valor_total += valor_diferenca
                cartao_credito.save()

        # Ajusta o status de pagamento, se alterado
            if despesa_variavel.paga != despesa_original.paga:
                if despesa_variavel.paga:  # Marcada como paga
                    despesa_variavel.marcar_como_pago()
                else:  # Marcada como não paga
                    despesa_variavel.marcar_como_nao_pago()

        # Salva a instância após as alterações
            despesa_variavel.save()

            return super().form_valid(form)

@method_decorator(login_required(login_url='login'), name='dispatch')
class DespesaVariavelDelete(DeleteView):
    model = DespesaVariavel
    template_name = 'despesa_variavel_delete.html'
    success_url = reverse_lazy('despesas_variaveis')


@method_decorator(login_required(login_url='login'), name='dispatch')
class CartaoCreditoList(ListView):
    model = CartaoCredito
    template_name = 'cartao_credito_list.html'
    context_object_name = 'cartao_credito'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcula o total de todos os cartões
        total_cartoes = CartaoCredito.objects.aggregate(total=Sum('valor_total'))['total'] or 0
        context['total_cartoes'] = total_cartoes
        return context
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class CartaoCreditoCreate(CreateView):
    model = CartaoCredito
    form_class  = CartaoCreditoModelForm
    template_name = 'cartao_credito_create.html'
    success_url = reverse_lazy('cartao_credito')

@method_decorator(login_required(login_url='login'), name='dispatch')
class CartaoCreditoUpdate(UpdateView):
    model = CartaoCredito
    form_class  = CartaoCreditoModelForm
    template_name = 'cartao_credito_update.html'
    success_url = reverse_lazy('cartao_credito')

@method_decorator(login_required(login_url='login'), name='dispatch')
class CartaoCreditoDelete(DeleteView):
    model = CartaoCredito
    template_name = 'cartao_credito_delete.html'
    success_url = reverse_lazy('cartao_credito')


@method_decorator(login_required(login_url='login'), name='dispatch')
class TotalReceitasList(ListView):
    model = TotalReceitas
    template_name = 'total_receitas_list.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class TotalDespesasFixasList(ListView):
    model = TotalDespesasFixas
    template_name = 'total_despesas_fixas_list.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class TotalDespesasVariaveisList(ListView):
    model = TotalDespesasVariaveis
    template_name = 'total_despesas_variaveis_list.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
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

@method_decorator(login_required(login_url='login'), name='dispatch')
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
        total_despesas_fixas = despesas.aggregate(total=Sum('valor'))['total'] or 0

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

@method_decorator(login_required(login_url='login'), name='dispatch')
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

        total_despesas_variaveis = despesas.aggregate(total=Sum('valor'))['total'] or 0

        total_despesas_variaveis= despesas.filter(paga=False).aggregate(total=Sum('valor'))['total'] or 0

        total_despesas_pagas = despesas.filter(paga=True).aggregate(total=Sum('valor'))['total'] or 0

        total_receitas = Receita.objects.aggregate(total=Sum('valor'))['total'] or 0



        return render(request, 'relatorio_despesas_variavel.html', {
            'despesas': despesas,
            #'total_despesas': total_despesas,
            'total_despesas_variaveis': total_despesas_variaveis,
            'total_despesas_pagas': total_despesas_pagas,
            'total_receitas': total_receitas,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'imprimir': False  # Para não mostrar o relatório automaticamente
        })


@method_decorator(login_required(login_url='login'), name='dispatch')
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
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class MarcarComoDespesaFixaPagoView(RedirectView):
    url = reverse_lazy('despesas_fixas')  # Redireciona para a lista de despesas

    def get(self, request, pk):
        despesa_fixa = get_object_or_404(DespesaFixa, pk=pk)
        
        # Verifica se a despesa está marcada como paga ou não paga
        if not despesa_fixa.paga:
            # Se a despesa não estiver paga, marca como paga e retira o valor do cartão
            despesa_fixa.marcar_como_pago()
        else:
            # Se a despesa já estiver paga, desmarca como paga e adiciona o valor de volta ao cartão
            despesa_fixa.marcar_como_nao_pago()

        # Redireciona de volta para a lista de despesas fixa
        return redirect('despesas_fixas')

    def get_redirect_url(self, *args, **kwargs):
        # Obtém a despesa com o ID fornecido na URL
        despesa_fixa = DespesaFixa.objects.get(pk=kwargs['pk'])
        
        # Se a despesa estiver marcada como paga, salva o valor no cartão, senão adiciona ao cartão
        if despesa_fixa.paga:
            # Marca a despesa como paga e retira o valor do cartão
            despesa_fixa.cartao_credito.valor_total -= despesa_fixa.valor
        else:
            # Marca a despesa como não paga e adiciona o valor de volta ao cartão
            despesa_fixa.cartao_credito.valor_total += despesa_fixa.valor
        
        despesa_fixa.cartao_credito.save()  # Salva a atualização no limite do cartão
        despesa_fixa.save()  # Salva a atualização da despesa

        # Redireciona para a lista de despesas fixas
        return super().get_redirect_url(*args, **kwargs)

        # Redireciona de volta para a lista de despesas com o total atualizado
        #return super().get_redirect_url(*args, **kwargs)
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class MarcarComoDespesaVariavelPagoView(RedirectView):
    url = reverse_lazy('despesas_variaveis')  # Redireciona para a lista de despesas variáveis

    def get(self, request, pk):
        despesa_variavel = get_object_or_404(DespesaVariavel, pk=pk)
        
        # Verifica se a despesa está marcada como paga ou não paga
        if not despesa_variavel.paga:
            # Se a despesa não estiver paga, marca como paga e retira o valor do cartão
            despesa_variavel.marcar_como_pago()
        else:
            # Se a despesa já estiver paga, desmarca como paga e adiciona o valor de volta ao cartão
            despesa_variavel.marcar_como_nao_pago()

        # Redireciona de volta para a lista de despesas variáveis
        return redirect('despesas_variaveis')

    def get_redirect_url(self, *args, **kwargs):
        # Obtém a despesa com o ID fornecido na URL
        despesa_variavel = DespesaVariavel.objects.get(pk=kwargs['pk'])
        
        # Se a despesa estiver marcada como paga, salva o valor no cartão, senão adiciona ao cartão
        if despesa_variavel.paga:
            # Marca a despesa como paga e retira o valor do cartão
            despesa_variavel.cartao_credito.valor_total -= despesa_variavel.valor
        else:
            # Marca a despesa como não paga e adiciona o valor de volta ao cartão
            despesa_variavel.cartao.limite += despesa_variavel.valor
        
        despesa_variavel.cartao.save()  # Salva a atualização no limite do cartão
        despesa_variavel.save()  # Salva a atualização da despesa

        # Redireciona para a lista de despesas variáveis
        return super().get_redirect_url(*args, **kwargs)

        # Redireciona de volta para a lista de despesas com o total atualizado
        return super().get_redirect_url(*args, **kwargs)