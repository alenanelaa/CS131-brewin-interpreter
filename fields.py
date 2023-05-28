#class for brewin fields within a class
from intbase import ErrorType
from values import types, value
from classes import classDef

class fieldDef:
    def __init__(self, i , n, t, val):
        self.interpreter, self.m_name = i, n

        if t not in self.interpreter.types:
            self.interpreter.error(ErrorType.TYPE_ERROR)

        self.m_type = self.interpreter.types[t]

        if val == 'null':
            if isinstance(self.interpreter.types[t], classDef): #only object variables can be null (no primitives)
                self.m_val = value(self.m_type, None)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
            return
        elif val == 'true' or val == 'false':
            v = value(types.BOOL, (val == 'true'))
        elif val[0] == '"' and val[-1] == '"':
            v = value(types.STRING, val.strip('"'))
        elif all(c.isdigit() for c in val):
            v = value(types.INT, int(val))
        else:
            self.interpreter.error(ErrorType.TYPE_ERROR)

        if v.type != self.m_type:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid type/type mismatch with field {self.m_name}')
        self.m_val = v

    def newfield(self):
        return field(self.interpreter, self.m_name, self.m_type, self.m_val)

class field:
    def __init__(self, i, n, t, val):
        self.interpreter, self.m_name, self.m_type, self.m_val = i, n, t, val

    def setvalue(self, val):
        self.m_val = val

    def getvalue(self):
        return self.m_val

    @property 
    def type(self):
        return self.m_type #should never need to set type after initializing a field