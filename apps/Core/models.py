from django.db import models
from apps.Loginer.models import User


class Repository(models.Model):
    url=models.CharField(max_length=150)
    name=models.CharField(max_length=70)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="repositories", null=True)

    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"

    def __str__(self):
        return self.name


class Prompt(models.Model):
    prompt=models.TextField()
    files_context=models.JSONField(default=list, null=True)
    answer=models.TextField()
    # repository=models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="questions")
    branch=models.ForeignKey("Branch", on_delete=models.CASCADE, related_name="questions")
    
    class Meta:
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self):
        if len(self.prompt) < 70:
            return self.prompt
        return self.prompt[:70]+"..."


class Branch(models.Model):
    name=models.CharField(max_length=70)
    repository=models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="branches")
    files=models.JSONField(default=list)

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        constraints = [
            models.UniqueConstraint(fields=['name', 'repository'], name='unique_branch_per_repository')
        ]

    def __str__(self):
        return self.name
