from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import JsonResponse, Http404
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.contrib import messages

from apps.Repository.utils import BuildFileTreeHTML, clear_git_api_response, get_repo_name_and_owner, FILE_URL, AIFactory, GIT_HEADERS, PRE_PROMPT_TEXT
from apps.Core.models import Repository, Prompt, Branch
from apps.Repository.tasks import fill_repository
from apps.Repository.forms import RepositoryForm
from apps.Core.utils import DataMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import httpx
import json



class CreateRepositoryView(DataMixin, LoginRequiredMixin, FormView):
    template_name = 'analyzer/create_repo_form.html'
    form_class = RepositoryForm
    page_title = 'Create Repository'

    def form_valid(self, form):
        repository = form.save(commit=False)
        repository.user = self.request.user
        repository.save()
        fill_repository.delay(repository.id, form.cleaned_data['url'])
        messages.info(self.request, "Repository adding is in progress.")
        return redirect("home")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid data.")
        return redirect("create_repository")


class UserRepositoriesView(DataMixin, LoginRequiredMixin, ListView):
    model = Repository
    template_name = "analyzer/user_repos_list.html"
    context_object_name = "repositories"
    page_title = "Repositories"

    def get_queryset(self):
        return Repository.objects.filter(user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            repositories_data = [
                {
                    "name": repo.name,
                }
                for repo in context['repositories']
            ]
            return JsonResponse({'repositories': repositories_data})
        return super().render_to_response(context, **response_kwargs)


class RepositoryDetailView(DataMixin, LoginRequiredMixin, DetailView):
    model = Repository
    template_name = "analyzer/repo_detail.html"
    context_object_name = "repository"
    page_title = "WorkSpace"

    def get_object(self, queryset=None):
        repository = super().get_object(queryset)
        if repository.user != self.request.user:
            raise Http404("You don't have access to this repository.")
        return repository

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_branch_name = self.request.GET.get("branch", "main")

        try:
            selected_branch = self.object.branches.get(name=selected_branch_name)
        except Branch.DoesNotExist:
            selected_branch = self.object.branches.first()

        all_branches = self.object.branches.exclude(name=selected_branch_name)

        context['files'] = selected_branch.files

        html_build = BuildFileTreeHTML()
        tree = html_build.build_tree(selected_branch.files, self.object.name)
        context['file_tree'] = tree
        context['all_branches'] = all_branches
        context['selected_branch'] = selected_branch

        questions = Prompt.objects.filter(branch=selected_branch)
        context['questions'] = questions

        return context


class RepoContentAPI(APIView):
    black_list_file_type = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", "mp4", "mp3"]

    def get(self, request, pk):
        repository = Repository.objects.get(id=pk)
        if repository.user != request.user:
            raise Http404("You don't have access to this repository.")

        branch_name = request.GET.get("branch", "main")
        if not branch_name:
            raise Http404("This branch does not exist.")
        branch = repository.branches.get(name=branch_name)


        file_content = {}
        owner, repo = get_repo_name_and_owner(repository.url)
        with httpx.Client() as client:
            for file in branch.files:
                if file.split(".")[-1] in RepoContentAPI.black_list_file_type:
                    file_content[file] = "File not found"
                    continue

                resp = client.get(FILE_URL.format(owner=owner, repo_name=repo, file_path=file, branch=branch_name),
                                  headers=GIT_HEADERS
                                  )

                if resp.status_code == 403:
                    resp = client.get(FILE_URL.format(owner=owner, repo_name=repo, file_path=file, branch=branch_name))


                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    file_content[file] = content
                else:
                    file_content[file] = "File not found"

        return Response(file_content, status=status.HTTP_200_OK)

class CodeAnalyzeAPI(APIView):
    def post(self, request):
        file_paths = request.data.get("selected_files")
        branch_id = request.data.get("branch_id")
        user_question = request.data.get("description")
        current_branch = Branch.objects.get(id=branch_id)
        repository = current_branch.repository

        owner, repo = get_repo_name_and_owner(repository.url)

        prompt = PRE_PROMPT_TEXT + user_question + "\n\n files: "

        prompt_context = {}
        with httpx.Client() as client:
            for file in json.loads(file_paths):
                url = FILE_URL.format(owner=owner, repo_name=repo, file_path=file, branch=current_branch.name)
                resp = client.get(url, headers=GIT_HEADERS)

                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    prompt_context[file] = content

        model = AIFactory.get_ai_instance("gemini")
        answer = model.generate_answer(prompt + json.dumps(prompt_context))

        Prompt.objects.create(
            branch=current_branch,
            prompt=user_question,
            answer=answer,
            files_context=file_paths
        )
        return Response({"summary": answer}, status=status.HTTP_200_OK)


class QuestionDetailAPIView(APIView):
    def get(self, request):
        question_id = request.GET.get("question_id")
        question = Prompt.objects.get(id=question_id)
        files_context = json.loads(question.files_context)
        return Response({"prompt": question.prompt, "answer": question.answer, "files_context": files_context}, status=status.HTTP_200_OK)


class DeleteQuestionAPIView(APIView):
    def delete(self, request):
        question_id = request.GET.get("question_id")
        Prompt.objects.get(id=question_id).delete()
        return Response({"success": True}, status=status.HTTP_200_OK)