from abc import ABC, abstractmethod

from BaseApp.settings import GITHUB_TOKEN, GEMINI_MODEL, GEMINI_API_KEY
import google.generativeai as genai
import base64

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

FILE_URL = "https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}?ref={branch}"
GIT_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
PRE_PROMPT_TEXT = """
            Руководство к формату ответа:
            Свой ответ подай в виде сплошного текста без пропусков строк. Если нужно будет написать фрагмент кода, то просто начни его писать с новой строки.


        """




class AI(ABC):
    @abstractmethod
    def generate_answer(self, prompt) -> str:
        pass

class Gemini(AI):
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=GEMINI_MODEL)

    def generate_answer(self, prompt:str) -> str:
        response = self.model.generate_content(prompt)
        return response.parts.pop(0).text


class AIFactory:
    @staticmethod
    def get_ai_instance(ai_type) -> AI|None:
        if ai_type == "gemini":
            return Gemini()
        else:
            return None

