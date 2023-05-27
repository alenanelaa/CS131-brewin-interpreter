from intbase import ErrorType
from values import types

class classDef:
    def __init__(self, inter, name, p = None):
        self.interpreter, self.className, self.parent = inter, name, p
        self.m_methods = []
        self.m_fields = []
    
    def hasField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return True
        return False
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f

        self.interpreter.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')

    def hasMethod(self, methodname):
        for m in self.m_methods:
            if m.m_name == methodname:
                return True
        return False

    def typematch(self, m, p):
        if m == p:
            return True
        elif isinstance(m, classDef) and isinstance(p, classDef):
            #can only pass a child object into a function that expects a parent object
            return self.typematch(m, p.parent) #parents and grandparents
        elif isinstance(m, classDef) and p == types.NULL: #null? but i don't know if this is allowed
            return True
        else:
            return False

    def findMethodDef(self, methodname, params):
        for m in self.m_methods:
            if m.m_name == methodname:
                t1 = [self.interpreter.types[m.params[i][0]] for i in range(len(m.params))] #parameter types
                t2 = [v.type for v in params]

                if len(t1) != len(t2):
                    return -1
                if not all([self.typematch(t1[i], t2[i]) for i in range(len(t1))]):
                    return -1
                
                for i in range(len(t1)):
                    params[i].type = t1[i] #set the types properly
                
                return m
            
        return -1