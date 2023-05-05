from statements import statement

class methodDef:
    def __init__(self, inter, name, c, top):
        self.interpreter = inter
        #name of the method
        self.m_name = name
        #class that it belongs to
        self.m_class = c
        self.params = [] #need to keep track of the name -> consider creating param class
        self.m_statement = statement(self.interpreter, c, self, top)

    #list of parameters passed in
    def setParams(self, p):
        self.params.extend(p)

    def findField(self, fieldname):
        return self.m_class.getField(fieldname)

    #execute top level statement
    def execute(self):
        self.m_statement.run_statement()