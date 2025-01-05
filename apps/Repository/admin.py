from django.contrib import admin
from apps.Core.models import Prompt, Repository, Branch
from apps.Loginer.models import User

# Register your models here.

admin.site.register(Prompt)
admin.site.register(Repository)
admin.site.register(User)
admin.site.register(Branch)