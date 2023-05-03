from intbase import InterpreterBase, ErrorType
from statements import statement


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

class objDef:
    def __init__(self, inter, classtype, methods, fields):
        self.interpreter = inter
        self.m_class = classtype
        self.m_methods = methods
        self.fields = fields

    def run_method(self, methodname):
        a = self.findMethod(methodname)
        a.execute()
        
    def findMethod(self, mname):
        for m in self.m_methods:
            if m.m_name == mname:
                return m
        
        self.interpreter.output(self, f'NAME ERROR: method {mname} not defined')
        return ErrorType.NAME_ERROR

#class for brewin class methods

class methodDef:
    def __init__(self, inter, name, c):
        self.interpreter = inter
        #name of the method
        self.m_name = name
        #class that it belongs to
        self.m_class = c
        self.params = []
        self.m_statements = []

    def execute(self):
        for s in self.m_statements:
            s.run_statement()
        #this probably has to be more complex to handle control flows