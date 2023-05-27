from intbase import ErrorType
from statements import statement

class objDef:
    def __init__(self, inter, classDef, fields, parent=None, anchor = None):
        self.interpreter, self.m_class, self.m_fields = inter, classDef, fields

        if not anchor:
            self.me = self
        else:
            self.me = anchor

        if parent:
            f = [d.newfield() for d in parent.m_fields]
            self.parent = objDef(self.interpreter, parent, f, parent = parent.parent, anchor = self.me)
        else:
            self.parent = None

    def run_method(self, method, params):
        if self.interpreter.trace:
            p = [str(key) + ':' + str(params[key]) for key in params]
            self.interpreter.output(f'RUN {method.m_name} method: {method.m_statement} with params {p}')

        if method.m_statement[0] == self.interpreter.BEGIN_DEF:
            self.interpreter.stackpush(method.m_statement[1:])
        else:
            self.interpreter.stackpush([method.m_statement])

        stackframe = 1

        while stackframe > 0:
            cur_frame = self.interpreter.stackpop()
            stackframe -= 1

            if not cur_frame:
                break

            s = cur_frame.pop(0)

            self.interpreter.stackpush(cur_frame)
            stackframe += 1
            
            st = statement(self.interpreter, s, self, params, method.default_return)
            r = st.run_statement(method, self.m_fields, [])
        
            if r:
                stackframe -= 1

        if not r:
            return method.default_return
        
        if not method.typematch(method.default_return.type, r.type):
            self.interpreter.error(ErrorType.TYPE_ERROR)
        
        return r
        
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
    
