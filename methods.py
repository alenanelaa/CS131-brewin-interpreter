from intbase import ErrorType
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
        elif r not in self.interpreter.types:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid method return type {r}')
        elif isinstance(self.interpreter.types[r], classDef): #default return null if object not returned in method
            self.default_return = value(self.interpreter.types[r], None)
        else:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid method return type {r}')
        self.localvar = [] #stack of dictionaries for let statements

    def findField(self, fieldname):
        return self.m_class.getField(fieldname)
    
    def typematch(self, default, r):
        if default == r:
            return True
        elif isinstance(default, classDef) and isinstance(r, classDef):
            #can only pass a child object into a function that expects a parent object
            return self.typematch(default, r.parent) #parents and grandparents
        else:
            return False