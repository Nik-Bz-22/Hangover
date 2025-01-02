from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.http import JsonResponse, Http404
from django.views.generic import DetailView

from BaseApp.settings import GITHUB_TOKEN, GEMINI_MODEL, GEMINI_API_KEY
from apps.Core.models import Repository, Question
from apps.Repository.tasks import fill_repository
from apps.Repository.forms import RepositoryForm
from apps.Core.utils import DataMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import google.generativeai as genai
import base64
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
        return JsonResponse({'status': 'success'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


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


class BuildFileTreeHTML:
    @staticmethod
    def build_tree(file_list, repo_name):
        tree = {}
        for file_path in file_list:
            parts = file_path.split('/')
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        main_tree = {repo_name: tree}
        return main_tree


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
        context['files'] = self.object.files
        html_build = BuildFileTreeHTML()
        tree = html_build.build_tree(self.object.files, self.object.name)
        context['file_tree'] = tree
        questions = Question.objects.filter(repository=self.object)
        context['questions'] = questions
        return context



def clear_git_api_response(api_response) -> str:
    file_meta_info = api_response.json()
    encoded_file_content = file_meta_info.get("content")

    try:
        clear_content = base64.b64decode(encoded_file_content).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        print(exc)
        return "File content could not be decoded."
    return clear_content


class RepoContentAPI(APIView):
    black_list_file_type = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", "mp4", "mp3"]

    def get(self, request, pk):
        repository = Repository.objects.get(id=pk)
        if repository.user != request.user:
            raise Http404("You don't have access to this repository.")

        file_content = {}
        FILE_URL = "https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
        owner, repo = repository.url.split('/')[-2:]
        with httpx.Client() as client:
            for file in repository.files:
                if file.split(".")[-1] in RepoContentAPI.black_list_file_type:
                    file_content[file] = "File not found"
                    continue

                resp = client.get(FILE_URL.format(owner=owner, repo_name=repo, file_path=file),
                                  headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                                           "Accept": "application/vnd.github+json",
                                           "X-GitHub-Api-Version": "2022-11-28"}
                                  )

                if resp.status_code == 403:
                    resp = client.get(FILE_URL.format(owner=owner, repo_name=repo, file_path=file))


                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    file_content[file] = content
                else:
                    file_content[file] = "File not found"

        return Response(file_content, status=status.HTTP_200_OK)

class CodeAnalyzeAPI(APIView):
    def post(self, request):
        file_paths = request.data.get("selected_files")
        repo_id = request.data.get("repo_id")
        user_question = request.data.get("description")
        repository = Repository.objects.get(id=repo_id)

        FILE_URL = "https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
        owner, repo = repository.url.split('/')[-2:]

        prompt_context = {}

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)

        pre_prompt_text = """
            Руководство к формату ответа:
            Свой ответ подай в виде сплошного текста без пропусков строк. Если нужно будет написать фрагмент кода, то просто начни его писать с новой строки.
            
            
        """

        prompt = pre_prompt_text + user_question + "\n\n files: "

        with httpx.Client() as client:
            for file in json.loads(file_paths):
                url = FILE_URL.format(owner=owner, repo_name=repo, file_path=file)
                print(f"{url=}")
                resp = client.get(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                                           "Accept": "application/vnd.github+json",
                                           "X-GitHub-Api-Version": "2022-11-28"})

                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    prompt_context[file] = content

        response = model.generate_content(prompt + json.dumps(prompt_context))
        answer = response.parts.pop(0).text

        Question.objects.create(
            repository=repository,
            prompt=user_question,
            answer=answer,
            files_context=file_paths
        )
        return Response({"summary": answer}, status=status.HTTP_200_OK)


class QuestionDetailAPIView(APIView):
    def get(self, request):
        question_id = request.GET.get("question_id")
        question = Question.objects.get(id=question_id)
        files_context = json.loads(question.files_context)
        return Response({"prompt": question.prompt, "answer": question.answer, "files_context": files_context}, status=status.HTTP_200_OK)
