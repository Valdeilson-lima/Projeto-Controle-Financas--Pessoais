from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import  post_save, post_delete
from .models import Receita, DespesaFixa, DespesaVariavel, TotalReceitas, TotalDespesasFixas, TotalDespesasVariaveis
from django.utils import timezone

def atualizar_total_receitas(sender, instance, **kwargs):
    total = Receita.objects.aggregate(total=Sum('valor'))['total']
    TotalReceitas.objects.update_or_create(
        pk=1,
        defaults={'total': total, 'data_criação': timezone.now()}
    )

def atualizar_total_despesas_fixas(sender, instance, **kwargs):
    total = DespesaFixa.objects.aggregate(total=Sum('valor'))['total']
    TotalDespesasFixas.objects.update_or_create(
        pk=1,
        defaults={'total': total, 'data_criação': timezone.now()}
    )


def atualizar_total_despesas_variaveis(sender, instance, **kwargs):
    total = DespesaVariavel.objects.aggregate(total=Sum('valor'))['total']
    TotalDespesasVariaveis.objects.update_or_create(
        pk=1,
        defaults={'total': total, 'data_criação': timezone.now()}
    )


@receiver(post_save, sender=Receita)
@receiver(post_delete, sender=Receita)
def atualizar_total_receitas_signal(sender, instance, **kwargs):
    atualizar_total_receitas(sender, instance, **kwargs)

@receiver(post_save, sender=DespesaFixa)
@receiver(post_delete, sender=DespesaFixa)
def atualizar_total_despesas_fixas_signal(sender, instance, **kwargs):
    atualizar_total_despesas_fixas(sender, instance, **kwargs)

@receiver(post_save, sender=DespesaVariavel)
@receiver(post_delete, sender=DespesaVariavel)
def atualizar_total_despesas_variaveis_signal(sender, instance, **kwargs):
    atualizar_total_despesas_variaveis(sender, instance, **kwargs)