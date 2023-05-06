from intbase import ErrorType

class objDef:
    def __init__(self, inter, classDef, fields):
        self.interpreter = inter
        self.m_class = classDef
        self.m_fields = fields

    def run_method(self, method, params):
        #DEBUGGING
        if self.interpreter.trace:
            self.interpreter.output(f'RUN {method.m_name} method: {method.m_statement} with params {params}')

        method.execute(self, params)
        
    def getMethod(self, mname):
        return self.m_class.findMethodDef(mname)
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f

        self.interpreter.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')