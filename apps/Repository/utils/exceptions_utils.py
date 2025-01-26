import httpx
from django.db import DatabaseError
from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    status_code = 500
    default_detail = "An unexpected error occurred."

def handle_exceptions(func) -> callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError:
            raise CustomAPIException("Database error occurred.")
        except httpx.HTTPError:
            raise CustomAPIException("External API call failed.")
        except Exception as e:
            raise CustomAPIException(str(e))
    return wrapper