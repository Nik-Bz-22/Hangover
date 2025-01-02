import asyncio
import httpx
from celery import shared_task
from apps.Core.models import Repository
from apps.Loginer.models import User


def fetch_github_repo_files(repo_url: str, client: httpx.Client):
    response = client.get(repo_url)
    if response.status_code == 200:
        return process_files_async(response.json(), client)
    elif response.status_code == 403:
        raise Exception("Rate limit exceeded. Please try again later.")
    elif response.status_code == 404:
        raise Exception(f"Repository not found at {repo_url}")
    else:
        response.raise_for_status()

def process_files_async(files_data, client: httpx.Client) -> list:
    all_files = []
    for file in files_data:
        if file["type"] == "file":
            all_files.append(file["path"])
        elif file["type"] == "dir":
            sub_dir_files = fetch_github_repo_files(file["url"], client)
            all_files.extend(sub_dir_files)
    return all_files

@shared_task
def fill_repository(repository_id, repo_url):
    owner, repo = repo_url.split('/')[-2:]
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    with httpx.Client() as client:
        all_files = fetch_github_repo_files(github_api_url, client)
    Repository.objects.filter(id=repository_id).update(files=all_files, name=repo)
