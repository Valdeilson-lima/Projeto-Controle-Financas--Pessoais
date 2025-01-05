from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Criação do usuário
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            
            # Redireciona para a página inicial (home)
            return redirect('login')  # Certifique-se de que o nome da URL esteja correto
        else:
            return render(request, 'register.html', {'form': form})


        # Se o formulário não for válido, renderiza a tela de cadastro novamente
        return render(request, 'register.html', {'form': form})
class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Obtenção das credenciais e autenticação
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # Redireciona para a página 'home' após login bem-sucedido
                return redirect('home-page')  # Aqui você pode usar a URL de 'home'
            else:
                form.add_error(None, "Credenciais inválidas")
        return render(request, 'login.html', {'form': form})
    

    
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

