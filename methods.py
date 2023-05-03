from statements import statement

class methodDef:
    def __init__(self, inter, name, c):
        self.interpreter = inter
        #name of the method
        self.m_name = name
        #class that it belongs to
        self.m_class = c
        self.params = []
        self.m_statements = []

    #list of parameters passed in
    def setParams(self, p):
        self.params.extend(p)

    #list representing statement(s) passed in
    def setStatements(self, st):
        self.m_statements.append(statement(self.interpreter, st))

    def execute(self):
        for s in self.m_statements:
            s.run_statement()
        #this probably has to be more complex to handle control flows