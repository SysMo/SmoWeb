class CodeBlock(object):
    """ A block of code included in the template """
    def __init__(self, srcType = None, src = None):
        if (srcType == None):
            self.srcType = 'string'
            if (src == None):
                self.src = ''
            else:
                self.src = src
        elif (srcType == 'file'):
            self.srcType = srcType
            if (src == None):
                raise ValueError('File path missing as second argument.')
            else:
                self.src = src
        elif (srcType == 'string'):
            self.srcType = srcType
            if (src == None):
                self.src = ''
            else:
                self.src = src
        else:
            raise ValueError("Valid source types are 'string' and 'file'.")
            
class HtmlBlock(CodeBlock):
    """ A block of HTML code """
    pass

class JsBlock(CodeBlock):
    """ A block of JavaScript code """
    pass