from BaseApp.settings import GITHUB_TOKEN
from enum import Enum


class Constants(Enum):
    BLACKLISTED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", "mp4", "mp3"]
    FILE_NOT_FOUND_MESSAGE = "File not found"
    PRE_PROMPT_TEXT = """
                

            """
    FILE_URL = "https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}?ref={branch}"
    GIT_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


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









