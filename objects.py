from intbase import ErrorType

class objDef:
    def __init__(self, inter, classtype, methods, fields):
        self.interpreter = inter
        self.m_class = classtype
        self.m_methods = methods
        self.fields = fields

    def run_method(self, methodname):
        a = self.findMethod(methodname)
        a.execute()
        
    def findMethod(self, mname):
        for m in self.m_methods:
            if m.m_name == mname:
                return m
        
        self.interpreter.output(self, f'NAME ERROR: method {mname} not defined')
        self.error(ErrorType.NAME_ERROR)