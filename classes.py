from objects import objDef
from intbase import ErrorType

#class for brewin class definitions

class classDef:
    def __init__(self, inter, name):
        self.interpreter, self.className = inter, name
        self.m_methods = []
        self.m_fields = []

    #instantiating class object
    def instantiate_object(self):
        obj = objDef(self.interpreter, self, self.m_fields)
        return obj
    
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

    def findMethodDef(self, methodname):
        for m in self.m_methods:
            if m.m_name == methodname:
                return m
        
        self.interpreter.error(ErrorType.NAME_ERROR, description=f'method {methodname} is not defined')