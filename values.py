from enum import Enum

class types(Enum):
    NULL = 0
    BOOL = 1
    INT = 2
    STRING = 3
    NOTHING = 4
    EXCEPTION = 5

class environment:
    def __init__(self, p):
        self.params = p
        self.locals = []
        self.exception = None
    def addlocal(self, scope):
        self.locals.append(scope)
    def addexception(self, ex):
        self.exception = ex
    def clearexception(self):
        self.exception = None

#class for brewin values, keeps track of type and value
class value:
    defaults = {(types.INT): 0, (types.STRING): "", (types.BOOL): False}
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
    def __not__(self):
        return not self.m_value