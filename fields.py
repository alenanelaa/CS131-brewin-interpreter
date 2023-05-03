from intbase import InterpreterBase, ErrorType
from enum import Enum

class types(Enum):
    NULL = 0
    BOOL = 1
    INT = 2
    STRING = 3
    #FLOAT = 4
    #DOUBLE = 5

#class for brewin fields within a class
class field:
    def __init__(self, inter, name, val):
        self.interpreter = inter
        self.m_name = name
        self.m_val = val