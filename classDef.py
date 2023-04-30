from intbase import InterpreterBase, ErrorType

class classDef:
    def __init__(self, name):
        self.className = name
        #empty list for methods - may change data structure later
        self.m_methods = []
        #empty list for class fields (variables) - may change data structure later
        self.m_fields = []
        #how many instantiated objects in the program
        self.m_objs = 0

    #instantiating class object
    def instantiate_object(self):
        self.m_objs += 1
