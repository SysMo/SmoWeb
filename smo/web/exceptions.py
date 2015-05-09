# To be relocated to smo.util

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

class ConvergenceError(CustomException):
	pass

class ConnectionError(Exception):
	def __init__(self, var1, var2, msg):
		self.var1 = var1
		self.var2 = var2
		self.msg = msg

	def __str__(self):
		return "Failed connecting {} and {}:\n {}".format(
				self.var1.qName, self.var2.qName, self.msg) 
