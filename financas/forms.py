from django import forms
from financas.models import Receita, DespesaFixa, DespesaVariavel, CartaoCredito


class ReceitaModelForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['data', 'descricao', 'valor']
        widgets = {
            'data': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})




class DespesaFixaModelForm(forms.ModelForm):
    class Meta:
        model = DespesaFixa
        fields = ['data', 'descricao', 'valor', 'cartao_credito']
        
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'cartao_credito': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop é redundante agora, mas poderia ser mantido para unificar estilos facilmente
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class DespesaVariavelModelForm(forms.ModelForm):
    class Meta:
        model = DespesaVariavel
        fields = ['data', 'descricao', 'valor', 'cartao_credito']
        
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'cartao_credito': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop é redundante agora, mas poderia ser mantido para unificar estilos facilmente
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CartaoCreditoModelForm(forms.ModelForm):
    class Meta:
        model = CartaoCredito
        fields = ['nome', 'limite']
        
    widgets = {
        'nome': forms.TextInput(attrs={'class': 'form-control'}),  # Campo de texto
        'limite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),  # Campo numérico
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop é redundante agora, mas poderia ser mantido para unificar estilos facilmente
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})