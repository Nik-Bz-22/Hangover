import base64

import httpx


def clear_git_api_response(api_response) -> str:
    file_meta_info = api_response.json()
    encoded_file_content = file_meta_info.get("content")

    try:
        clear_content = base64.b64decode(encoded_file_content).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        print(exc)
        return "File content could not be decoded."
    return clear_content


def get_repo_name_and_owner(url:str):
    return url.split('/')[-2:]

def valid_repo_url(repo_url:str) -> bool:
    if not repo_url:
        return False
    if not repo_url.startswith("https://github.com/"):
        return False
    if len(repo_url.split('/')) != 5:
        return False
    with httpx.Client() as client:
        response = client.get(repo_url)
    if response.status_code == 200:
        return True