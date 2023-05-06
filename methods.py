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

    def findField(self, fieldname):
        return self.m_class.getField(fieldname)

    #execute top level statement
    def execute(self, obj, params):
        s = statement(self.interpreter, self.m_statement, obj, params)
        s.run_statement()