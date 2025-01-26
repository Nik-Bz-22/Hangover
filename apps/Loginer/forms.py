from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

user_model = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = user_model
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = user_model
        fields = ['username', "first_name", "last_name"]
