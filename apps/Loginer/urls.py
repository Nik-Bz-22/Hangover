from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.Loginer.views import LogIn, SignUpView
#  register_view,
urlpatterns = [
    path("log-in/", LogIn.as_view(), name="log_in"),
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("logout/", LogoutView.as_view(next_page="home"), name="log_out"),
]
