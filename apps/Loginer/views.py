from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from ..Core.utils import DataMixin


class SignUpView(DataMixin, CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'loginer/signup.html'
    page_title = 'Sign Up'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        return redirect('home')


class LogIn(DataMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'loginer/login.html'
    page_title = 'Login'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            return redirect('home')
        messages.success(self.request, 'Login successful!')
        return super().form_valid(form)
