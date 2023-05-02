from intbase import InterpreterBase, ErrorType
from bparser import BParser

from classDef import classDef, methodDef, objDef
from fieldDef import field, value

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        #begin with empty list of classes
        self.m_classes = []


    def run(self, program):
        indicator, tokens = BParser.parse(program)

        if not indicator:
            InterpreterBase.output(self, "Parsing Error")
            #FIGURE OUT ANOTHER WAY TO RETURN AN ERROR THIS SEEMS WRONG********
            return SystemError

        self.trackClasses(self, tokens)
        
    #discover and track all classes
    def trackClasses(self, tokens):
        #top level of parsed program must be class
        for class_def in tokens:
            a = classDef(class_def[1])
            #classes have either field or method handlers
            for item in class_def:
                match item[0]:
                    case 'method':
                        a.m_methods.append(methodDef(item[1],class_def[1]))
                        #gets the method to get its parameters and statments
                        m = a.m_methods[-1]
                        m.params = item[2]
                        m.statements = item[3]
                        
                    case 'field': #add feature later
                        a.m_fields.append(field('test', 0))

            self.m_classes.append(a)

    
    #find a specific class definition
    def findClassDef(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return c
        
