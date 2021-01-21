from app.exceptions.base_exception import BaseException


class InvalidContentType(BaseException):
    status_code = 400
