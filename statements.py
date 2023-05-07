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

    def run_statement(self, method, fields):
        
        a = self.m_statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output('ENTER BEGIN BLOCK')

                #MAY HAVE TO CHANGE TO ACCOUNT FOR NESTED BEGIN BLOCKS

                steps = [statement(self.interpreter, line, self.m_obj, self.m_params) for line in self.m_statement[1:]]
                for s in steps:
                    r = s.run_statement(method, fields)
                    #if r == something to specify that the statement was a return value, don't run anything else in the begin block

                #MAY HAVE TO CHANGE TO ACCOUNT FOR NESTED BEGIN BLOCKS

            case self.interpreter.CALL_DEF:
                    #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
                match self.m_statement[1]:
                    case self.interpreter.ME_DEF:
                        m = self.m_obj.getMethod(self.m_statement[2])
                        self.getParams(m.params)
                        self.m_obj.run_method(m, self.m_params, fields)
                    case _:
                        pass

            case self.interpreter.IF_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'IF STATEMENT with condition {self.m_statement[1]}')

                self.handleIf(method, fields)

            case self.interpreter.INPUT_INT_DEF:
                self.handleInput(types.INT)

            case self.interpreter.INPUT_STRING_DEF:
                self.handleInput(types.STRING)

            case self.interpreter.PRINT_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'PRINT expressions {self.m_statement[1:]}')

                #list of expression objects to be printed
                exprs = [expression(self.interpreter, e, self.m_obj, self.m_params, fields) for e in self.m_statement[1:]]
                self.handlePrint(exprs)

            case self.interpreter.RETURN_DEF:
                if self.interpreter.trace:
                    self.interpreter.output("RETURN from method called")
                self.interpreter.stackpop()
                method.stackframe -= 1
                if len(self.m_statement) == 2:
                    expr = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields)
                    return expr.evaluate()

            case self.interpreter.SET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'SET variable {self.m_statement[1]} to {self.m_statement[2]}')
                #check if in params first in case of shadowing
                fieldnames = [f.m_name for f in fields]
                if self.m_statement[1] in self.m_params:
                    self.m_params[self.m_statement[1]] = self.m_statement[2]
                elif self.m_statement[1] in fieldnames:
                    for i in range(len(fields)):
                        if fieldnames[i] == fields[i].m_name:
                            field = fields[i]
                            break
                    val = expression(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, fields).evaluate()
                    field.setvalue(val)
                else:
                    self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown variable {self.m_statement[1]}')


            case self.interpreter.WHILE_DEF:
                pass

            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'Invalid statement command "{self.m_statement[0]}" ')

    def handleIf(self, method, fields):
        condition = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields)
        cond = condition.evaluate()

        if cond.gettype() != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean if condition')

        if self.interpreter.trace:
            self.interpreter.output(f'condition evaluated to {cond}')

        if cond.m_value:
            s = statement(self.interpreter, self.m_statement[2], self.m_obj, self.m_params)
            s.run_statement(method, fields)
        #will only run this if condition evaluates to false and there is a statement to run if false
        elif len(self.m_statement[2:]) == 2:
            s = statement(self.interpreter, self.m_statement[3], self.m_obj, self.m_params)
            s.run_statement(method, fields)     

    def getParams(self, params):
        values = [x for x in self.m_statement[3:]]
        if len(values) != len(params):
            self.interpreter.error(ErrorType.TYPE_ERROR, description="Incorrect number of parameters")
        
        self.m_params = {params[i]:values[i] for i in range(len(params))}

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

    
        
    