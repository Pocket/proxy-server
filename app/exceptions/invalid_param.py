from app.exceptions.base_exception import BaseException

class InvalidParam(BaseException):
    status_code = 400
