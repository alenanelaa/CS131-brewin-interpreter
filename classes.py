from objects import objDef
from intbase import ErrorType

#class for brewin class definitions

class classDef:
    def __init__(self, inter, name):
        self.interpreter = inter
        self.className = name
        #empty list for methods - may change data structure later
        self.m_methods = []
        #empty list for class fields (variables) - may change data structure later
        self.m_fields = []

    #instantiating class object
    def instantiate_object(self):
        obj = objDef(self.interpreter, self, self.m_fields)
        return obj
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f

        self.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')

    def findMethodDef(self, methodname):
        for m in self.m_methods:
            if m.m_name == methodname:
                return m
        
        self.error(ErrorType.NAME_ERROR, description=f'method {methodname} is not defined')