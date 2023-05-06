from intbase import InterpreterBase, ErrorType
from bparser import BParser

from classes import classDef
from methods import methodDef
from fields import field
from values import value, types

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        #begin with empty list of class definitions, methods, and objects
        self.m_classes = []
        self.m_objs = []
        #for debugging
        self.trace = trace_output


    def run(self, program):
        indicator, tokens = BParser.parse(program)

        if not indicator:
            self.output("Parsing Error")
            #FIGURE OUT ANOTHER WAY TO RETURN AN ERROR THIS SEEMS WRONG********
            return SystemError

        self.trackClasses(tokens)
        mainclass = self.findClassDef('main')
        obj = mainclass.instantiate_object()
        self.m_objs.append(obj)
        mainmethod = obj.getMethod('main')
        obj.run_method(mainmethod, {})
        
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
                        a.m_methods.append(methodDef(self, item[1], a, item[2], item[3]))
                        
                    case 'field':
                        a.m_fields.append(field(item[1], self.getValue(item[2])))

    
    #find a specific class definition
    def findClassDef(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return c
            
        self.error(ErrorType.NAME_ERROR, description=f'class {classname} is not defined')

    def getValue(self, token):
        if token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
            return val
        else:
            val = value(types.INT, int(token))
        return val