from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.Loginer.views import LogIn, SignUpView, ChangePasswordView, PasswordChangedView, UpdateUserSettingsView

urlpatterns = [
    path("log-in/", LogIn.as_view(), name="log_in"),
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("logout/", LogoutView.as_view(next_page="home"), name="log_out"),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path("password_change_done/", PasswordChangedView.as_view(), name="password_change_done"),
    path("", UpdateUserSettingsView.as_view(), name="update_user_settings"),

]
