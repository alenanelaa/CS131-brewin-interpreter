#class for brewin fields within a class
from intbase import ErrorType
from values import types, value

class field:
    def __init__(self, i, n, t, val):
        self.interpreter, self.m_name, self.m_type = i, n, t

        if val == 'null':
            if t not in self.interpreter.types:
                self.interpreter.error(ErrorType.TYPE_ERROR)
            else:
                self.m_val = value(types.OBJECT, None)
                return
        elif val == 'true' or val == 'false':
            v = value(types.BOOL, (val == 'true'))
        elif val[0] == '"' and val[-1] == '"':
            v = value(types.STRING, val.strip('"'))
        elif all(c.isdigit() for c in val):
            v = value(types.INT, int(val))
        else:
            #invalid value -> may need to change later
            self.interpreter.error(ErrorType.TYPE_ERROR)

        if v.gettype() != self.m_type:
            self.interpreter.error(ErrorType.TYPE_ERROR)
        self.m_val = v

    def getValue(self, token):
        if token == 'null':
            val = value(types.VOID, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
            return val
        else:
            val = value(types.INT, int(token))
        return val

    def __str__(self):
        return str(self.m_val)

    def setname(self, name):
        self.m_name = name

    def setvalue(self, val):
        self.m_val = val

    def getname(self):
        return self.m_name

    def getvalue(self):
        return self.m_val
    
    def gettype(self):
        return self.m_type #should never need to set type after initializing a field
    
# class parameter:
#     def __init__(self, i, type, val):
#         self.interpreter, self.type = i, type
        
#         if val == 'null':
#             if type not in self.interpreter.types:
#                 self.interpreter.error(ErrorType.TYPE_ERROR)
#             else:
#                 self.m_val = value(types.OBJECT, None)
#                 return
#         elif val == 'true' or val == 'false':
#             v = value(types.BOOL, (val == 'true'))
#         elif val[0] == '"' and val[-1] == '"':
#             v = value(types.STRING, val.strip('"'))
#         elif all(c.isdigit() for c in val):
#             v = value(types.INT, int(val))
#         else:
#             #invalid value -> may need to change later
#             self.interpreter.error(ErrorType.TYPE_ERROR)

#         if v.gettype() != self.m_type:
#             self.interpreter.error(ErrorType.TYPE_ERROR)
#         self.m_val = v