from values import types
from intbase import ErrorType
from copy import deepcopy

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

    def hasMethod(self, methodname):
        for m in self.m_methods:
            if m.m_name == methodname:
                return True
        return False

    def typematch(self, m, p):
        if m == p:
            return True
        elif isinstance(m, classDef) and isinstance(p, classDef):
            return self.typematch(m, p.parent) #parents and grandparents
        elif isinstance(m, classDef) and p == types.NULL:
            return True
        else:
            return False

    def findMethodDef(self, methodname, params):
        if self.interpreter.trace:
            self.interpreter.output(f'methods in class {self.className}:')
            for m in self.m_methods:
                self.interpreter.output(f'name: {m.m_name}; params: {m.params}; code: {m.m_statement}')

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
    
class templateDef:
    def __init__(self, inter, name, tnames, mf):
        self.interpreter, self.temp_name, self.param_names, self.code = inter, name, tnames, mf

    def returnClassDef(self, instname):
        if self.interpreter.trace:
            self.interpreter.output(f'TEMPLATE instantiation {instname}')

        pnames = instname.split('@')[1:]
        if len(self.param_names) != len(pnames) or any([pnames[i] not in self.interpreter.types for i in range(len(pnames))]):
            self.interpreter.error(ErrorType.TYPE_ERROR)

        c = classDef(self.interpreter, instname)
        self.interpreter.types[instname] = c
        map_types = {self.param_names[i]:pnames[i] for i in range(len(self.param_names))}
        mf = self.replaceStrings(deepcopy(self.code), map_types)

        self.interpreter.initializeClass(mf, c)

        return c

    #the following function was written with assistance from chatGPT
    def replaceStrings(self, code, replace): #replace is a dictionary of what needs to be replaced
        if isinstance(code, list):
            return [self.replaceStrings(token, replace) for token in code]
        elif isinstance(code, str):
            for key, val in replace.items():
                code = code.replace(key, val)
            return code
        else:
            return code
    #end of chatGPT code
