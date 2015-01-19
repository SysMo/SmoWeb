class ArgumentTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class FieldError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
