from django.contrib import admin
from apps.Core.models import Question, Repository
from apps.Loginer.models import User

# Register your models here.

admin.site.register(Question)
admin.site.register(Repository)
admin.site.register(User)