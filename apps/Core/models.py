from django.db import models
from apps.Loginer.models import User


class Repository(models.Model):
    url=models.CharField(max_length=150)
    name=models.CharField(max_length=70)
    files=models.JSONField(default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="repositories", null=True)

    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"

    def __str__(self):
        return self.name


class Question(models.Model):
    prompt=models.TextField()
    files_context=models.JSONField(default=list, null=True)
    answer=models.TextField()
    repository=models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="questions")
    asked_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        if len(self.prompt) < 70:
            return self.prompt
        return self.prompt[:70]+"..."
