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
        self.callstack = []
        #add class types as needed during initialization
        self.types = {'int':types.INT, 'string':types.STRING, 'null':types.VOID, 'bool':types.BOOL}
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
        mainmethod = obj.getMethod('main')
        obj.run_method(mainmethod, {}, obj.m_fields)
        
    #discover and track all classes
    def trackClasses(self, tokens):
        #top level of parsed program must be class
        for class_def in tokens:
            if self.classDefined(class_def[1]):
                self.error(ErrorType.TYPE_ERROR, description=f'Duplicate class name {class_def[1]}')
            a = classDef(self, class_def[1])
            self.m_classes.append(a)
            self.types[class_def[1]] = a #add object type (class type) to the map of possible variable types
            #classes have either field or method handlers
            for item in class_def[2:]:
                match item[0]:
                    case 'method':
                        if a.hasMethod(item[2]):
                            self.error(ErrorType.NAME_ERROR, description=f'duplicate method {item[1]}')
                        a.m_methods.append(methodDef(self, item[2], a, item[3], item[4], item[1]))
                        
                    case 'field':
                        if a.hasField(item[2]):
                            self.error(ErrorType.NAME_ERROR, description=f'duplicate field {item[2]}')
                        a.m_fields.append(field(self, item[2], self.types[item[1]], item[3]))

    def classDefined(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return True
        return False
    
    #find a specific class definition
    def findClassDef(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return c
            
        self.error(ErrorType.TYPE_ERROR, description=f'class {classname} is not defined')
    
    def stackpush(self, frame):
        self.callstack.append(frame)

    def stackpop(self):
        return self.callstack.pop()