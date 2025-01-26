from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.Repository.tasks import fill_branch
from apps.Core.models import Prompt

import httpx
import json

from apps.Repository.utils.ai_utils import AIFactory
from apps.Repository.utils.exceptions_utils import handle_exceptions
from apps.Repository.utils.git_utils import get_repo_name_and_owner, clear_git_api_response
from apps.Repository.utils.models_utils import get_user_repository_or_404, get_user_branch_or_404
from apps.Repository.utils.utils import Constants


class RepoContentAPI(APIView):
    @staticmethod
    @handle_exceptions
    def get(request, pk):
        repository = get_user_repository_or_404(request.user, pk)

        branch_id = request.GET.get("branch", "main")
        branch = get_user_branch_or_404(request.user, branch_id, repository.id)

        file_content = {}
        owner, repo = get_repo_name_and_owner(repository.url)

        with httpx.Client() as client:
            for file in branch.files:

                if file.split(".")[-1] in Constants.BLACKLISTED_FILE_TYPES.value:
                    file_content[file] = Constants.FILE_NOT_FOUND_MESSAGE.value
                    continue
                git_api_url = Constants.FILE_URL.value.format(owner=owner, repo_name=repo, file_path=file, branch=branch.name)
                resp = client.get(git_api_url, headers=Constants.GIT_HEADERS.value)

                if resp.status_code == 403:
                    resp = client.get(git_api_url)

                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    file_content[file] = content
                else:
                    file_content[file] = Constants.FILE_NOT_FOUND_MESSAGE.value

        return Response(file_content, status=status.HTTP_200_OK)

class CodeAnalyzeAPI(APIView):

    @staticmethod
    @handle_exceptions
    def post(request):
        file_paths = request.data.get("selected_files")
        user_question = request.data.get("description")
        branch_id = request.data.get("branch_id")
        current_branch = get_user_branch_or_404(request.user, branch_id)
        repository = current_branch.repository

        owner, repo = get_repo_name_and_owner(repository.url)

        prompt = Constants.PRE_PROMPT_TEXT.value + user_question + "\n\n files: "

        prompt_context = {}
        with httpx.Client() as client:
            for file in json.loads(file_paths):
                url = Constants.FILE_URL.value.format(owner=owner, repo_name=repo, file_path=file, branch=current_branch.name)
                resp = client.get(url, headers=Constants.GIT_HEADERS.value)

                if resp.status_code == 200:
                    content = clear_git_api_response(resp)
                    prompt_context[file] = content

        model = AIFactory.get_ai_instance("gemini")
        answer = model.generate_answer(prompt + json.dumps(prompt_context))

        Prompt.objects.create(branch=current_branch, prompt=user_question, answer=answer, files_context=file_paths)
        return Response({"summary": answer}, status=status.HTTP_200_OK)


class QuestionDetailAPIView(APIView):
    @staticmethod
    @handle_exceptions
    def get(request):
        question_id = request.GET.get("question_id")
        question = Prompt.objects.get(id=question_id)
        files_context = json.loads(question.files_context)
        return Response({"prompt": question.prompt, "answer": question.answer, "files_context": files_context}, status=status.HTTP_200_OK)


class DeleteQuestionAPIView(APIView):
    @staticmethod
    @handle_exceptions
    def delete(request):
        question_id = request.GET.get("question_id")
        Prompt.objects.get(id=question_id).delete()
        return Response({"success": True}, status=status.HTTP_200_OK)

class UpdateRepositoryContentAPIView(APIView):
    @staticmethod
    @handle_exceptions
    def put(request):
        repository_id = request.data.get("repository_id")
        selected_branch_id = request.data.get("selectedBranchID")
        # repository = get_user_repository_or_404(request.user, repository_id)
        branch = get_user_branch_or_404(request.user, selected_branch_id, repository_id)
        fill_branch.delay(branch.id)
        return Response({"success": True}, status=status.HTTP_201_CREATED)