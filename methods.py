from intbase import ErrorType
from statements import statement
from values import value, types

class methodDef:
    def __init__(self, i, n, c, p, top, r):
        self.interpreter, self.m_name, self.m_class, self.params, self.m_statement = i, n, c, p, top

        dict = {'int':value(types.INT, 0), 'bool':value(types.BOOL, False), 'void':value(types.VOID, None)}
        self.default_return = dict[r]
        self.stackframe = 0

    def findField(self, fieldname):
        return self.m_class.getField(fieldname)

    #execute top level statement
    def execute(self, obj, params, fields):
        #push to stack
        if self.m_statement[0] == self.interpreter.BEGIN_DEF:
            self.interpreter.stackpush(self.m_statement[1:])
        else:
            self.interpreter.stackpush([self.m_statement])

        self.stackframe = 1

        while self.stackframe > 0:
            cur_frame = self.interpreter.stackpop()
            self.stackframe -= 1

            # if self.interpreter.trace:
            #     self.interpreter.output(f'current_frame: {cur_frame}')

            if not cur_frame:
                return

            s = cur_frame.pop(0)

            self.interpreter.stackpush(cur_frame)
            self.stackframe += 1
            
            st = statement(self.interpreter, s, obj, params)
            r = st.run_statement(self, fields)

        if self.interpreter.trace:
            self.interpreter.output(f'method returned {r}')

        if not r:
            return self.default_return
        
        if r.gettype() != self.default_return.gettype():
            self.interpreter.error(ErrorType.TYPE_ERROR)
        
        return r         