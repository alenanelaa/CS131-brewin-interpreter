from intbase import ErrorType

class objDef:
    def __init__(self, inter, classDef, fields):
        self.interpreter = inter
        self.m_class = classDef
        self.m_fields = fields

    def run_method(self, method, params, fields):
        #DEBUGGING
        if self.interpreter.trace:
            p = [str(key) + ' : ' + str(params[key]) for key in params]
            self.interpreter.output(f'RUN {method.m_name} method: {method.m_statement} with params {p}')

        r = method.execute(self, params, fields)
        # if self.interpreter.trace:
        #     self.interpreter.output(f'method returned {r}')
        return r
        
    def getMethod(self, mname):
        return self.m_class.findMethodDef(mname)
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f

        self.interpreter.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')

    def getfields(self):
        return self.m_fields