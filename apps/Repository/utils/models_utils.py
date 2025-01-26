from django.contrib.auth.mixins import LoginRequiredMixin
from apps.Core.models import Branch, Repository
from apps.Core.utils import DataMixin
from django.http import Http404


class BaseAccountAccess(DataMixin, LoginRequiredMixin):
    pass

def get_user_repository_or_404(user, repository_id:int) -> Repository:
    repository = Repository.objects.filter(id=repository_id, user=user).first()
    if not repository:
        raise Http404("You don't have access to this repository.")
    return repository

def get_user_branch_or_404(user, branch_id:int|str, repo_id:int|str=None) -> Branch:
    branch = Branch.objects.filter(id=int(branch_id), repository__user=user).first()
    if not branch:
        raise Http404("You don't have access to this branch.")
    if repo_id:
        if branch.repository.id != int(repo_id):
            raise Http404("You don't have access to this branch.")
    return branch