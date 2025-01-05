from django.urls import path
from . import views
from .views import GerarRelatorioReceitas, GerarRelatorioDespesasFixas, GerarRelatorioDespesasVariaveis

urlpatterns = [
 

    # Receitas
    path('receitas/', views.ReceitaList.as_view(), name='receitas'),
    path('receitas/criar/', views.ReceitaCreate.as_view(), name='receita_criar'),
    path('receitas/<int:pk>/editar/', views.ReceitaUpdate.as_view(), name='receita_editar'),
    path('receitas/<int:pk>/deletar/', views.ReceitaDelete.as_view(), name='receita_deletar'),

    # Despesas Fixas
    path('despesas-fixas/', views.DespesaFixaList.as_view(), name='despesas_fixas'),
    path('despesas-fixas/criar/', views.DespesaFixaCreate.as_view(), name='despesa_fixa_criar'),
    path('despesas-fixas/<int:pk>/editar/', views.DespesaFixaUpdate.as_view(), name='despesa_fixa_editar'),
    path('despesas-fixas/<int:pk>/deletar/', views.DespesaFixaDelete.as_view(), name='despesa_fixa_deletar'),

    # Despesas Variáveis
    path('despesas-variaveis/', views.DespesaVariavelList.as_view(), name='despesas_variaveis'),
    path('despesas-variaveis/criar/', views.DespesaVariavelCreate.as_view(), name='despesa_variavel_criar'),
    path('despesas-variaveis/<int:pk>/editar/', views.DespesaVariavelUpdate.as_view(), name='despesa_variavel_editar'),
    path('despesas-variaveis/<int:pk>/deletar/', views.DespesaVariavelDelete.as_view(), name='despesa_variavel_deletar'),

    # Cartão de Crédito
    path('cartao-credito/', views.CartaoCreditoList.as_view(), name='cartao_credito'),
    path('cartao-credito/criar/', views.CartaoCreditoCreate.as_view(), name='cartao_credito_criar'),
    path('cartao-credito/<int:pk>/editar/', views.CartaoCreditoUpdate.as_view(), name='cartao_credito_editar'),
    path('cartao-credito/<int:pk>/deletar/', views.CartaoCreditoDelete.as_view(), name='cartao_credito_deletar'),

    # Totais
    path('totais/receitas/', views.TotalReceitasList.as_view(), name='total_receitas'),
    path('totais/despesas-fixas/', views.TotalDespesasFixasList.as_view(), name='total_despesas_fixas'),
    path('totais/despesas-variaveis/', views.TotalDespesasVariaveisList.as_view(), name='total_despesas_variaveis'),

    path('home/', views.HomeView.as_view(), name='home-page'),
    path('gerar-relatorio/receitas/', GerarRelatorioReceitas.as_view(), name='gerar_relatorio_receitas'),
    path('gerar-relatorio/despesas_fixas/', GerarRelatorioDespesasFixas.as_view(), name='gerar_relatorio_despesas_fixas'),
    path('gerar-relatorio/despesas_variaveis/', GerarRelatorioDespesasVariaveis.as_view(), name='gerar_relatorio_despesas_variaveis'),
]