import google.generativeai as genai
from abc import ABC, abstractmethod

from BaseApp.settings import GEMINI_MODEL, GEMINI_API_KEY


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