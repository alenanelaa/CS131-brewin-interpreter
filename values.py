from enum import Enum

class types(Enum):
    VOID = 0
    BOOL = 1
    INT = 2
    STRING = 3
    # OBJECT = 4

#class for brewin values, keeps track of type and value
class value:
    def __init__(self, type, value):
        self.m_type, self.m_value = type, value

    @property
    def type(self):
        return self.m_type

    @type.setter
    def type(self, t):
        self.m_type = t
    #for outputting correctly
    def __str__(self):
        if self.m_type == types.BOOL:
            if self.m_value:
                return 'true'
            else:
                return 'false'

        return str(self.m_value)

    #operation wrappers for brewin values

    def __add__(self, other):
        return self.m_value + other.m_value
    
    def __sub__(self, other):
        return self.m_value - other.m_value
    
    def __mul__(self, other):
        return self.m_value * other.m_value
    
    def __truediv__(self, other):
        return self.m_value/other.m_value
    
    def __floordiv__(self, other):
        return self.m_value//other.m_value
    
    def __mod__(self, other):
        return self.m_value % other.m_value
    
    #comparison operators

    def __lt__(self, other):
        return self.m_value < other.m_value
    
    def __gt__(self, other):
        return self.m_value > other.m_value

    def __eq__(self, other):
        return self.m_value == other.m_value

    def __le__(self, other):
        return self.m_value <= other.m_value

    def __ge__(self, other):
        return self.m_value >= other.m_value

    def __ne__(self, other):
        return self.m_value != other.m_value

    #unary not operator
    def __not__(self):
        return not self.m_value