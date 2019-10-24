from app.exceptions.base_exception import BaseException

class MissingParam(BaseException):
    status_code = 400
