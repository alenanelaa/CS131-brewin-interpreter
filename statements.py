from intbase import InterpreterBase, ErrorType

class statement:
    def __init__(self, inter, s):
        self.m_statement = s
        self.interpreter = inter

    def run_statement(self):
        match self.m_statement[0]:
            case 'begin':
                for s in self.m_statement[1:]:
                    step = statement(self.interpreter,s)
                    step.run_statement()
            case 'print':
                self.handlePrint(self.m_statement[1:])
            #add many more cases for different statement types

    def handlePrint(self, s):
        fprint = ''

        for item in s:
            if isinstance(item, list):
                raise NotImplementedError
            else:
                fprint = fprint + str(item).strip('"')

        self.interpreter.output(fprint)
    