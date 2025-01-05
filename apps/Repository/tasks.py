import asyncio

import celery.result
import httpx
from celery import shared_task

from BaseApp.settings import GITHUB_TOKEN
from apps.Core.models import Repository, Branch
from apps.Loginer.models import User


def fetch_github_repo_files(repo_url: str, client: httpx.Client):

    response = client.get(repo_url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                             "Accept": "application/vnd.github+json",
                             "X-GitHub-Api-Version": "2022-11-28"})
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
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}"
    github_content_api_url = f"{github_api_url}/contents"
    github_branches_api_url = f"{github_api_url}/branches"

    repository = Repository.objects.get(id=repository_id)
    print(f"Filling repository {repository.name}...")


    with httpx.Client() as client:

        all_branches = client.get(github_branches_api_url)
        if all_branches.status_code != 200:
            return False

        for branch in all_branches.json():
            github_api_url = f"{github_content_api_url}?ref={branch['name']}"

            all_files = fetch_github_repo_files(github_api_url, client)
            print(f"Found {len(all_files)} files in branch {branch['name']}.")

            branch, _ = Branch.objects.get_or_create(name=branch["name"], repository=repository)
            branch.files = all_files
            branch.save()
            print(f"Branch {branch.name} saved.")

    Repository.objects.filter(id=repository_id).update(name=repo)


