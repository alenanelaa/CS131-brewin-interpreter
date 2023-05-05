from intbase import ErrorType
from expressions import expression

class statement:
    bops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!='}
    uops = {'!'}

    def __init__(self, inter, c, m, s):
        self.interpreter = inter
        self.m_class = c
        self.m_method = m
        self.m_statement = s

    def run_statement(self):
        a = self.m_statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                    steps = [statement(self.interpreter, self.m_class, self.m_method, line) for line in self.m_statement[1:]]
                    for s in steps:
                        s.run_statement()
            case self.interpreter.CALL_DEF:
                pass
            case self.interpreter.IF_DEF:
                pass
            case self.interpreter.INPUT_INT_DEF:
                pass
            case self.interpreter.INPUT_STRING_DEF:
                pass
            case self.interpreter.PRINT_DEF:
                #list of expression objects to be printed
                exprs = [expression(e, self.m_class) for e in self.m_statement[1:]]
                self.handlePrint(exprs)
            case self.interpreter.RETURN_DEF:
                pass
            case self.interpreter.SET_DEF:
                pass
            case self.interpreter.WHILE_DEF:
                pass
            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR)

    def handleInput(self, type):
        #instantiate input of the method
        pass

    def handlePrint(self, s):
        fprint = ''

        for item in s:
            val = item.evaluate()
            fprint = fprint + str(val)

        self.interpreter.output(fprint)
    