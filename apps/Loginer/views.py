from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm
from ..Repository.utils.models_utils import BaseAccountAccess
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
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

class ChangePasswordView(BaseAccountAccess, PasswordChangeView):
    template_name = 'loginer/change_password.html'
    page_title = 'Change Password'


class PasswordChangedView(BaseAccountAccess, PasswordChangeDoneView):
    template_name = 'loginer/password_change_done.html'
    page_title = 'Password Changed'


class UpdateUserSettingsView(BaseAccountAccess, UpdateView):
    model = get_user_model()
    template_name = 'loginer/update_user_settings.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('home')
    page_title = 'Update User Settings'

    def get_object(self, queryset=None):
        return self.request.user
