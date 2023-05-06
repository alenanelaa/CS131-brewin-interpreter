from intbase import ErrorType
from expressions import expression
from values import value, types

class statement:
    bops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!='}
    uops = {'!'}

    def __init__(self, inter, s, o, p):
        self.interpreter = inter
        self.m_statement = s
        self.m_obj = o
        self.m_params = p

    def run_statement(self):
        a = self.m_statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                    #DEBUGGING
                    if self.interpreter.trace:
                        self.interpreter.output('Entering begin block')

                    steps = [statement(self.interpreter, line, self.m_obj, self.m_params) for line in self.m_statement[1:]]
                    for s in steps:
                        s.run_statement()
            case self.interpreter.CALL_DEF:
                    #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
                match self.m_statement[1]:
                    case self.interpreter.ME_DEF:
                        m = self.m_obj.getMethod(self.m_statement[2])
                        self.getParams(m.params)
                        self.m_obj.run_method(m, self.m_params)
                    case _:
                        pass
            case self.interpreter.IF_DEF:
                pass
            case self.interpreter.INPUT_INT_DEF:
                self.handleInput(types.INT)
            case self.interpreter.INPUT_STRING_DEF:
                self.handleInput(types.STRING)
            case self.interpreter.PRINT_DEF:
                #list of expression objects to be printed
                exprs = [expression(self.interpreter, e, self.m_obj, self.m_params) for e in self.m_statement[1:]]
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
        f = self.m_obj.getField(self.m_statement[1])
        val = self.interpreter.get_input()
        if type == types.INT:
            val = int(val)

        f.setvalue(value(type, val))

    def handlePrint(self, s):
        fprint = ''

        for item in s:
            val = item.evaluate()
            fprint = fprint + str(val)

        self.interpreter.output(fprint)

    def getParams(self, params):
        values = [x for x in self.m_statement[3:]]
        if len(values) != len(params):
            self.interpreter.error(ErrorType.SYNTAX_ERROR, description="Incorrect number of parameters")
        
        self.m_params = {params[i]:values[i] for i in range(len(params))}
        
    