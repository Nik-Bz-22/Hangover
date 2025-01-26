from django.urls import path

from apps.Repository.views.class_views import CreateRepoView, UserRepositoriesView, RepoDetailView
from apps.Repository.views.api_views import RepoContentAPI, CodeAnalyzeAPI, QuestionDetailAPIView, DeleteQuestionAPIView, UpdateRepositoryContentAPIView

urlpatterns = [
    path("create/", CreateRepoView.as_view(), name="create_repository"),
    path("repos/", UserRepositoriesView.as_view(), name="my_repositories"),
    path("repos/<int:pk>/", RepoDetailView.as_view(), name="repository_detail"),
    path("api/repos/content/<int:pk>/", RepoContentAPI.as_view(), name="api_get_repo_content"),
    path("api/analyze/", CodeAnalyzeAPI.as_view(), name="api_analyze_repo"),
    path("api/question/", QuestionDetailAPIView.as_view(), name="api_get_question"),
    path("api/question/delete/", DeleteQuestionAPIView.as_view(), name="api_delete_question"),
    path("api/branch/update/", UpdateRepositoryContentAPIView.as_view(), name="api_update_branch"),
]
