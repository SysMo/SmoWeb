class CustomException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ArgumentError(CustomException):
    pass

class ArgumentTypeError(CustomException):
    pass
    
class FieldError(CustomException):
    pass
