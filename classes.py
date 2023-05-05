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
        #how many instantiated objects in the program
        self.m_objs = 0 #prob don't need this lmfao

    #instantiating class object
    def instantiate_object(self):
        obj = objDef(self.className, self.interpreter, self.m_methods, self.m_fields)
        return obj
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f
            
        self.interpreter.output(f'NAME ERROR: field {fieldname} is not defined')
        self.error(ErrorType.NAME_ERROR)