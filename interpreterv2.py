from intbase import InterpreterBase, ErrorType
from bparser import BParser

from classes import classDef
from objects import objDef
from methods import methodDef
from fields import fieldDef
from values import types

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        #begin with empty list of class definitions, methods, and objects
        self.m_classes = []
        self.callstack = []
        #add class types as needed during initialization
        self.types = {'int':types.INT, 'string':types.STRING, 'null':types.NULL, 'bool':types.BOOL}
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
        obj = self.instantiate_object(mainclass)
        mainmethod, mainobj = obj.getMethod('main', {})
        mainobj.run_method(mainmethod, {})

    def instantiate_object(self, classdef):
        f = [d.newfield() for d in classdef.m_fields]
        if classdef.parent:
            # p = classdef.parent.instantiate_object()
            obj = objDef(self, classdef, f, parent=classdef.parent)
        else:
            obj = objDef(self, classdef, f)
            
        return obj
        
    #discover and track all classes
    def trackClasses(self, tokens):
        #top level of parsed program must be class
        definitions = []
        for class_def in tokens:
            if self.classDefined(class_def[1]):
                self.error(ErrorType.TYPE_ERROR, description=f'Duplicate class name {class_def[1]}')

            if isinstance(class_def[2], list):
                c = classDef(self, class_def[1])
                self.m_classes.append(c)
                self.types[class_def[1]] = c
                definitions.append(class_def[2:])
            elif class_def[2] == self.INHERITS_DEF:
                parent = self.findClassDef(class_def[3])
                c = classDef(self, class_def[1], p = parent)
                self.m_classes.append(c)
                self.types[class_def[1]] = c
                definitions.append(class_def[4:])
            else:
                self.error(ErrorType.SYNTAX_ERROR)

        for i in range(len(self.m_classes)):
            self.initializeClass(definitions[i], self.m_classes[i])
            
    def initializeClass(self, mf, a):
        for item in mf:
            match item[0]:
                case 'method':
                    if a.hasMethod(item[2]):
                        self.error(ErrorType.NAME_ERROR, description=f'duplicate method {item[1]}')
                    a.m_methods.append(methodDef(self, item[2], a, item[3], item[4], item[1]))
                case 'field':
                    if a.hasField(item[2]):
                        self.error(ErrorType.NAME_ERROR, description=f'duplicate field {item[2]}')
                    a.m_fields.append(fieldDef(self, item[2], item[1], item[3]))

    def classDefined(self, classname):
        cnames = [c.className for c in self.m_classes]
        return classname in cnames
    
    def findClassDef(self, classname):
        for c in self.m_classes:
            if c.className == classname:
                return c
            
        self.error(ErrorType.TYPE_ERROR, description=f'class {classname} is not defined')
    
    def stackpush(self, frame):
        self.callstack.append(frame)

    def stackpop(self):
        return self.callstack.pop()