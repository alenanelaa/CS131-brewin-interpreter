from intbase import ErrorType
from statements import statement
from values import value, types
from classes import classDef

class methodDef:
    defaults = {'int':value(types.INT, 0), 'string': value(types.STRING, ''), 'bool':value(types.BOOL, False), 'void':value(types.NOTHING, None)}

    def __init__(self, i, n, c, p, top, r):
        self.interpreter, self.m_name, self.m_class, self.params, self.m_statement = i, n, c, p, top

        paramtypes = [p[index][0] for index in range(len(self.params))]
        paramnames = [p[index][1] for index in range(len(self.params))]
        if len(paramnames) != len(set(paramnames)):
            self.interpreter.error(ErrorType.NAME_ERROR, description='duplicate formal param name')
        if any(param not in self.interpreter.types for param in paramtypes):
            self.interpreter.error(ErrorType.TYPE_ERROR)

        if r in methodDef.defaults:
            self.default_return = methodDef.defaults[r]
        elif isinstance(self.interpreter.types[r], classDef): #default return null if object not returned in method
            self.default_return = value(self.interpreter.types[r], None)
        else:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid method return type {r}')
        self.stackframe = 0
        self.localvar = [] #stack of dictionaries for let statements

    def findField(self, fieldname):
        return self.m_class.getField(fieldname)

    def execute(self, obj, params, fields):

        #push to stack
        if self.m_statement[0] == self.interpreter.BEGIN_DEF:
            self.interpreter.stackpush(self.m_statement[1:])
        else:
            self.interpreter.stackpush([self.m_statement])

        self.stackframe = 1

        while self.stackframe > 0:
            cur_frame = self.interpreter.stackpop()
            self.stackframe -= 1

            if not cur_frame:
                break

            s = cur_frame.pop(0)

            self.interpreter.stackpush(cur_frame)
            self.stackframe += 1
            
            st = statement(self.interpreter, s, obj, params, self.default_return)
            r = st.run_statement(self, fields, self.localvar)

        if not r:
            return self.default_return
        
        if not self.typematch(self.default_return.type, r.type):
            self.interpreter.error(ErrorType.TYPE_ERROR)
        
        return r
    
    def typematch(self, default, r):
        if default == r:
            return True
        elif isinstance(default, classDef) and isinstance(r, classDef):
            #can only pass a child object into a function that expects a parent object
            return self.typematch(default, r.parent) #parents and grandparents
        elif isinstance(default, classDef) and r == types.NULL: #null? but i don't know if this is allowed
            return True
        else:
            return False