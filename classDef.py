from intbase import InterpreterBase, ErrorType


#class for brewin class definitions

class classDef:
    def __init__(self, name):
        self.className = name
        #empty list for methods - may change data structure later
        self.m_methods = []
        #empty list for class fields (variables) - may change data structure later
        self.m_fields = []
        #how many instantiated objects in the program
        self.m_objs = 0 #prob don't need this lmfao

    #instantiating class object
    def instantiate_object(self):
        self.m_objs += 1

#class for brewin class methods

class methodDef:
    def __init__(self, name, c):
        #name of the method
        self.m_name = name
        #class that it belongs to
        self.m_class = c
        self.params = []
        self.m_statements = []

class objDef:
    def __init__(self, classtype):
        self.m_class = classtype

    def run_method(self, methodname):
        raise NotImplementedError