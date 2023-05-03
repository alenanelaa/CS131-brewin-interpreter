from intbase import InterpreterBase, ErrorType
from bparser import BParser

from classes import classDef
from methods import methodDef
from fields import field

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        #begin with empty list of class definitions
        self.m_classes = []


    def run(self, program):
        indicator, tokens = BParser.parse(program)

        if not indicator:
            self.output("Parsing Error")
            #FIGURE OUT ANOTHER WAY TO RETURN AN ERROR THIS SEEMS WRONG********
            return SystemError

        self.trackClasses(tokens)
        mainclass = self.findClassDef('main')
        obj = mainclass.instantiate_object()
        obj.run_method('main')
        
    #discover and track all classes
    def trackClasses(self, tokens):
        #top level of parsed program must be class
        for class_def in tokens:
            a = classDef(self, class_def[1])
            self.m_classes.append(a)
            #classes have either field or method handlers
            for item in class_def[2:]:
                match item[0]:
                    case 'method':
                        a.m_methods.append(methodDef(self, item[1],class_def[1]))
                        #gets the method to get its parameters and statments
                        m = a.m_methods[-1]
                        m.setParams(item[2])
                        m.setStatements(item[3])
                        
                    case 'field': #add feature later
                        a.m_fields.append(field(self, 'test', 0))

    
    #find a specific class definition
    def findClassDef(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return c
            
        self.output(f'NAME ERROR: class {classname} not defined')
        self.error(ErrorType.NAME_ERROR)
        
