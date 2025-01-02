from django.views.generic import TemplateView
from apps.Core.utils import DataMixin

class MainPage(DataMixin, TemplateView):
    template_name = "main/main_page.html"
    page_title = "Hangover"