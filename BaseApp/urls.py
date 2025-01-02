from django.contrib import admin
from django.urls import path, include

from apps.Core.views import MainPage
from apps.Repository import urls as repository_urls
from apps.Loginer import urls as login_urls

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path("", include(repository_urls)),
    path("account/", include(login_urls)),
    path("", MainPage.as_view(), name='home'),
]
