from django.urls import path

from apps.Repository.views import CreateRepositoryView, UserRepositoriesView, RepositoryDetailView, RepoContentAPI, CodeAnalyzeAPI, QuestionDetailAPIView

urlpatterns = [
    path("create/", CreateRepositoryView.as_view(), name="create_repository"),
    path("repos/", UserRepositoriesView.as_view(), name="my_repositories"),
    path("repos/<int:pk>/", RepositoryDetailView.as_view(), name="repository_detail"),
    path("api/repos/content/<int:pk>/", RepoContentAPI.as_view(), name="api_get_repo_content"),
    path("api/analyze/", CodeAnalyzeAPI.as_view(), name="api_analyze_repo"),
    path("api/question/", QuestionDetailAPIView.as_view(), name="api_get_question"),
]
