from django.core.exceptions import ValidationError

from apps.Core.models import Repository
from django import forms

from apps.Repository.utils.git_utils import valid_repo_url


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['url']
        widgets = {
            'url': forms.TextInput(attrs={
                'placeholder': 'Enter repository URL',
                'class': 'repo-form',
            }),
        }
        labels = {
            'url': 'Repository URL:',
        }

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not valid_repo_url(url):
            raise ValidationError("Invalid repository URL. Please provide a correct URL.")
        return url
