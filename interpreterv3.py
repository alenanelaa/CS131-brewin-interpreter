from intbase import InterpreterBase, ErrorType
from bparser import BParser

from classes import classDef, templateDef
from objects import objDef
from methods import methodDef
from fields import fieldDef
from values import types

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        self.m_templates = {}
        self.callstack = []
        #add class types as needed during initialization
        self.types = {'int':types.INT, 'string':types.STRING, 'null':types.NULL, 'bool':types.BOOL}
        #for debugging
        self.trace = trace_output


    def run(self, program):
        indicator, tokens = BParser.parse(program)

        if not indicator:
            self.error(ErrorType.SYNTAX_ERROR)

        self.trackClasses(tokens)
        mainclass = self.findClassDef('main')
        obj = self.instantiate_object(mainclass)
        mainmethod, mainobj = obj.getMethod('main', {})
        mainobj.run_method(mainmethod, {})

    def instantiate_object(self, classdef):
        f = [d.newfield() for d in classdef.m_fields]
        if classdef.parent:
            obj = objDef(self, classdef, f, parent=classdef.parent)
        else:
            obj = objDef(self, classdef, f)
        return obj
        
    #discover and track all classes
    def trackClasses(self, tokens):
        m_classes = {}
        classdefs = {}
        for class_def in tokens:
            if class_def[0] == self.TEMPLATE_CLASS_DEF:
                if self.templateDefined(class_def[1]):
                    self.error(ErrorType.TYPE_ERROR, description=f'Duplicate template name {class_def[1]}')
                t = templateDef(self, class_def[1], class_def[2], class_def[3:])
                self.m_templates[class_def[1]] = t             
            else:
                if self.classDefined(class_def[1], m_classes):
                    self.error(ErrorType.TYPE_ERROR, description=f'Duplicate class name {class_def[1]}')
                if isinstance(class_def[2], list):
                    c = classDef(self, class_def[1])
                    m_classes[class_def[1]] = c
                    self.types[class_def[1]] = c
                    classdefs[class_def[1]] = class_def[2:]
                elif class_def[2] == self.INHERITS_DEF:
                    parent = self.findClassDef(class_def[3])
                    c = classDef(self, class_def[1], p = parent)
                    m_classes[class_def[1]] = c
                    self.types[class_def[1]] = c
                    classdefs[class_def[1]] = class_def[4:]
                else:
                    self.error(ErrorType.SYNTAX_ERROR)

        for key in m_classes:
            self.initializeClass(classdefs[key], m_classes[key])
            
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
                    if len(item) == 3: #default field value
                        a.m_fields.append(fieldDef(self, item[2], item[1]))
                    else:
                        a.m_fields.append(fieldDef(self, item[2], item[1], item[3]))

    def classDefined(self, classname, classes):
        return classname in classes
    
    def templateDefined(self, tempname):
        return tempname in self.m_templates
    
    def findClassDef(self, classname):
        if classname not in self.types:
            self.error(ErrorType.TYPE_ERROR, description=f'class {classname} is not defined')
        r = self.types[classname]
        if not isinstance(r, classDef):
            self.error(ErrorType.TYPE_ERROR, description=f'invalid class')
        return r
    
    def stackpush(self, frame):
        self.callstack.append(frame)
    def stackpop(self):
        return self.callstack.pop()