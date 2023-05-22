from intbase import ErrorType

class objDef:
    def __init__(self, inter, classDef, fields, parent=None):
        self.interpreter, self.m_class, self.m_fields, self.parent = inter, classDef, fields, parent

    def run_method(self, method, params):
        #method passed in as string name
        if self.interpreter.trace:
            p = [str(key) + ':' + str(params[key]) for key in params]
            self.interpreter.output(f'RUN {method.m_name} method: {method.m_statement} with params {p}')

        return method.execute(self, params, self.m_fields)
        
    def getMethod(self, mname, params):
        m = self.m_class.findMethodDef(mname, params)
        o = self

        if m == -1:
            if self.parent:
                return self.parent.getMethod(mname, params)
            else:
                self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown method {mname}')
        else:
            return m, o
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f

        self.interpreter.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')

    def getfields(self):
        return self.m_fields
    
    def __eq__(self, other):
        return self is other