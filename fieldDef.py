from intbase import InterpreterBase, ErrorType


#class for brewin fields within a class
class field:
    def __init__(self, inter, name, val):
        self.interpreter = inter
        self.m_name = name
        self.m_val = val

#class for brewin values, keeps track of type and value
class value:
    def __init__(self, inter, type, value):
        self.interpreter = inter
        self.m_type = type
        self.m_value = value