from django.contrib import admin

from django.contrib import admin
from .models import (
    CartaoCredito,
    Receita,
    DespesaFixa,
    DespesaVariavel,
    TotalReceitas,
    TotalDespesasFixas,
    TotalDespesasVariaveis
)

class CartaoCreditoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'limite')
    search_fields = ('nome',)
    ordering = ('nome',)

class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor', 'descricao')
    search_fields = ('descricao',)
    ordering = ('-data',)
    list_filter = ('data',)

class DespesaFixaAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor', 'descricao', 'cartao_credito', 'pago_com_cartao')
    search_fields = ('descricao',)
    ordering = ('-data',)
    list_filter = ('data', 'cartao_credito')

class DespesaVariavelAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor', 'descricao', 'cartao_credito', 'pago_com_cartao')
    search_fields = ('descricao',)
    ordering = ('-data',)
    list_filter = ('data', 'cartao_credito')

class TotalReceitasAdmin(admin.ModelAdmin):
    list_display = ('total',)
    ordering = ('-total',)

class TotalDespesasFixasAdmin(admin.ModelAdmin):
    list_display = ('total',)
    ordering = ('-total',)

class TotalDespesasVariaveisAdmin(admin.ModelAdmin):
    list_display = ('total',)
    ordering = ('-total',)

admin.site.register(CartaoCredito, CartaoCreditoAdmin)
admin.site.register(Receita, ReceitaAdmin)
admin.site.register(DespesaFixa, DespesaFixaAdmin)
admin.site.register(DespesaVariavel, DespesaVariavelAdmin)
admin.site.register(TotalReceitas, TotalReceitasAdmin)
admin.site.register(TotalDespesasFixas, TotalDespesasFixasAdmin)
admin.site.register(TotalDespesasVariaveis, TotalDespesasVariaveisAdmin)
