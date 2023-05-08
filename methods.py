from statements import statement

class methodDef:
    def __init__(self, inter, name, c, p, top):
        self.interpreter = inter
        #name of the method
        self.m_name = name
        #class that it belongs to
        self.m_class = c
        self.params = p
        self.m_statement = top
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
        return r         