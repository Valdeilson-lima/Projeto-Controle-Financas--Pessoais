
from django.utils import timezone
from django.db import models

class CartaoCredito(models.Model):
    nome = models.CharField('Nome', max_length=50)  # Corrigido max_digits
    limite = models.DecimalField('Limite', max_digits=10, decimal_places=2)
    data_vencimento = models.DateField('Data')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Aqui é onde o valor total é armazenado

       

    def __str__(self):
        return self.nome
        """
    def total_gastos(self):
        """
        #Calcula o total de despesas (fixas e variáveis) associadas a este cartão.
        """
        despesas_fixas = self.despesafixa_set.aggregate(total=models.Sum('valor'))['total'] or 0
        despesas_variaveis = self.despesavariavel_set.aggregate(total=models.Sum('valor'))['total'] or 0
        return despesas_fixas + despesas_variaveis
        """

class Receita(models.Model):
    data = models.DateField('Data')
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=255)

    def __str__(self):
        return self.descricao

class DespesaFixa(models.Model):
    data = models.DateField('Data')
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=255)
    cartao_credito = models.ForeignKey(CartaoCredito, on_delete=models.CASCADE, null=True, blank=True)
    pago_com_cartao = models.BooleanField('Pago com cartão?', default=False)
    paga = models.BooleanField(default=False)

    def __str__(self):
        return self.descricao
    
    def save(self, *args, **kwargs):
        # Antes de salvar a despesa, ajusta o total de gastos do cartão
        if self.cartao_credito:
            if not self.pk:  # Se for uma nova despesa
                self.cartao_credito.valor_total += self.valor
                self.cartao_credito.save()

        
        super().save(*args, **kwargs)

    def marcar_como_pago(self):
        """Marca a despesa como paga e subtrai o valor do total de gastos do cartão"""
        self.paga = True
        self.save()  # Salva a despesa como paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total -= self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão

    def marcar_como_nao_pago(self):
        """Marca a despesa como não paga e adiciona o valor de volta ao total de gastos do cartão"""
        self.paga = False
        self.save()  # Salva a despesa como não paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total += self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão


class DespesaVariavel(models.Model):
    
    data = models.DateField('Data',)
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=255)
    cartao_credito = models.ForeignKey(CartaoCredito, on_delete=models.CASCADE, null=True, blank=True)
    pago_com_cartao = models.BooleanField('Pago com cartão?', default=False)
    paga = models.BooleanField(default=False)


    def __str__(self):
        return self.descricao
    

    def save(self, *args, **kwargs):
        # Antes de salvar a despesa, ajusta o total de gastos do cartão
        if self.cartao_credito:
            if not self.pk:  # Se for uma nova despesa
                self.cartao_credito.valor_total += self.valor
                self.cartao_credito.save()
        
        super().save(*args, **kwargs)

    def marcar_como_pago(self):
        """Marca a despesa como paga e subtrai o valor do total de gastos do cartão"""
        self.paga = True
        self.save()  # Salva a despesa como paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total -= self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão

    def marcar_como_nao_pago(self):
        """Marca a despesa como não paga e adiciona o valor de volta ao total de gastos do cartão"""
        self.paga = False
        self.save()  # Salva a despesa como não paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total += self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão


    def save(self, *args, **kwargs):
        # Antes de salvar a despesa, ajusta o total de gastos do cartão
        if self.cartao_credito:
            if not self.pk:  # Se for uma nova despesa
                self.cartao_credito.valor_total += self.valor
                self.cartao_credito.save()
        
        super().save(*args, **kwargs)

    def marcar_como_pago(self):
        """Marca a despesa como paga e subtrai o valor do total de gastos do cartão"""
        self.paga = True
        self.save()  # Salva a despesa como paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total -= self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão

    def marcar_como_nao_pago(self):
        """Marca a despesa como não paga e adiciona o valor de volta ao total de gastos do cartão"""
        self.paga = False
        self.save()  # Salva a despesa como não paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total += self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão


    def save(self, *args, **kwargs):
        # Antes de salvar a despesa, ajusta o total de gastos do cartão
        if self.cartao_credito:
            if not self.pk:  # Se for uma nova despesa
                self.cartao_credito.valor_total += self.valor
                self.cartao_credito.save()
        
        super().save(*args, **kwargs)

    def marcar_como_pago(self):
        """Marca a despesa como paga e subtrai o valor do total de gastos do cartão"""
        self.paga = True
        self.save()  # Salva a despesa como paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total -= self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão

    def marcar_como_nao_pago(self):
        """Marca a despesa como não paga e adiciona o valor de volta ao total de gastos do cartão"""
        self.paga = False
        self.save()  # Salva a despesa como não paga

        if self.cartao_credito:  # Verifica se há um cartão associado
            self.cartao_credito.valor_total += self.valor
            self.cartao_credito.save()  # Salva a atualização do total de gastos do cartão


class TotalReceitas(models.Model):
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    data_criação = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data_criação']


    def __str__(self):
        return f'Total: {self.total}'

class TotalDespesasFixas(models.Model):
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    data_criação = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-data_criação']


    def __str__(self):
        return f'Total: {self.total}'

class TotalDespesasVariaveis(models.Model):
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    data_criação = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data_criação']


    def __str__(self):
        return f'Total: {self.total}'
