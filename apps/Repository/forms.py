from apps.Core.models import Repository
from django import forms


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
        if not url.startswith('http'):
            raise forms.ValidationError("URL must start with 'http' or 'https'")
        return url