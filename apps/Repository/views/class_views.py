from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework.reverse import reverse_lazy

from apps.Repository.utils.git_utils import valid_repo_url
from apps.Repository.utils.models_utils import get_user_branch_or_404, BaseAccountAccess, get_user_repository_or_404
from apps.Repository.utils.exceptions_utils import handle_exceptions
from apps.Repository.utils.utils import BuildFileTreeHTML
from apps.Core.models import Repository, Prompt
from apps.Repository.tasks import fill_repository
from apps.Repository.forms import RepositoryForm



class CreateRepoView(BaseAccountAccess, FormView):
    template_name = 'analyzer/create_repo_form.html'
    form_class = RepositoryForm
    page_title = 'Create Repository'
    success_url = reverse_lazy('home')

    @handle_exceptions
    def form_valid(self, form):
        repo_url = form.cleaned_data['url']
        if Repository.objects.filter(user=self.request.user, url=repo_url).exists():
            return self.form_invalid(form, custom_error_message="Repository already exists.")
        repository = form.save(commit=False)
        repository.user = self.request.user
        repository.save()
        # check uniq repo for this user

        fill_repository.delay(repository.id, repo_url)
        messages.info(self.request, "Repository adding is in progress.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, custom_error_message=None):
        if custom_error_message:
            print(custom_error_message)
            form.add_error("url", custom_error_message)
        return self.render_to_response(self.get_context_data(form=form))


class UserRepositoriesView(BaseAccountAccess, ListView):
    model = Repository
    template_name = "analyzer/user_repos_list.html"
    context_object_name = "repositories"
    page_title = "Repositories"

    @handle_exceptions
    def get_queryset(self):
        return Repository.objects.filter(user=self.request.user)

    @handle_exceptions
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            repositories_data = [{"name": repo.name,} for repo in context['repositories']]
            return JsonResponse({'repositories': repositories_data})
        return super().render_to_response(context, **response_kwargs)


class RepoDetailView(BaseAccountAccess, DetailView):
    model = Repository
    template_name = "analyzer/repo_detail.html"
    context_object_name = "repository"
    page_title = "WorkSpace"

    @handle_exceptions
    def get_object(self, queryset=None):
        repository = super().get_object(queryset)
        if repository.user != self.request.user:
            raise Http404("You don't have access to this repository.")
        return repository

    @handle_exceptions
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_branch_id = self.request.GET.get("branch")
        repo_id = self.kwargs.get("pk")

        if not selected_branch_id:
            repo = get_user_repository_or_404(self.request.user, repo_id)
            selected_branch = repo.branches.first()
        else:
            selected_branch = get_user_branch_or_404(self.request.user, selected_branch_id, repo_id=repo_id)
            repo = selected_branch.repository

        selected_branch_id = selected_branch.id
        all_branches = repo.branches.exclude(id=selected_branch_id)
        context['files'] = selected_branch.files

        tree = BuildFileTreeHTML().build_tree(selected_branch.files, self.object.name)
        context['file_tree'] = tree
        context['all_branches'] = all_branches
        context['selected_branch'] = selected_branch

        prompt = Prompt.objects.filter(branch=selected_branch)
        context['questions'] = prompt

        return context
