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

        # if self.interpreter.trace:
        #     self.interpreter.output(f'RUNNING STATEMENT {self.m_statement}')
        
        a = self.m_statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output('ENTER BEGIN BLOCK')

                steps = [statement(self.interpreter, line, self.m_obj, self.m_params) for line in self.m_statement[1:]]
                for s in steps:
                    r = s.run_statement(method, fields)

                    if r: #if statement returns anything besides None, that means it was a return statement
                        break

            case self.interpreter.CALL_DEF:
                    #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
                match self.m_statement[1]:
                    case self.interpreter.ME_DEF:
                        m = self.m_obj.getMethod(self.m_statement[2])
                        self.getParams(m.params, fields)
                        self.m_obj.run_method(m, self.m_params, fields)
                    case _:
                        val = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields).evaluate()
                        if val.gettype() == types.NULL:
                            self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                        elif val.gettype() != types.OBJECT:
                            self.interpreter.error(ErrorType.FAULT_ERROR, description=f'invalid object pointer {self.m_statement[1]}')
                        obj = val.m_value
                        m = obj.getMethod(self.m_statement[2])
                        self.getParams(m.params, fields)
                        obj.run_method(m, self.m_params, obj.getfields())

            case self.interpreter.IF_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'IF STATEMENT with condition {self.m_statement[1]}')

                return self.handleIf(method, fields)

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
                else:
                    return types.RETURN
                
                # if self.interpreter.trace:
                #     self.interpreter.output(f'expression evaluation returned {r}')
                # return r

            case self.interpreter.SET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'SET variable {self.m_statement[1]} to {self.m_statement[2]}')
                #check if in params first in case of shadowing
                fieldnames = [f.m_name for f in fields]
                if self.m_statement[1] in self.m_params:
                    self.m_params[self.m_statement[1]] = expression(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, fields).evaluate()
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
                if self.interpreter.trace:
                    self.interpreter.output(f'WHILE LOOP with condition {self.m_statement[1]}')

                return self.handleWhile(method, fields)

            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'Invalid statement command "{self.m_statement[0]}" ')

    def handleWhile(self, method, fields):
        cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields).evaluate()
        if cond.gettype() != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean while condition')

        while cond.m_value:
            if self.interpreter.trace:
                self.interpreter.output(f'condition {self.m_statement[1]} evaluated to {cond}')

            s = statement(self.interpreter, self.m_statement[2], self.m_obj, self.m_params)
            r = s.run_statement(method, fields)
            
            #break out of while loop
            if r:
                return r

            cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields).evaluate()
    
    def handleIf(self, method, fields):
        cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields).evaluate()

        if cond.gettype() != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean if condition')

        if self.interpreter.trace:
            self.interpreter.output(f'condition {self.m_statement[1]} evaluated to {cond}')

        if cond.m_value:
            s = statement(self.interpreter, self.m_statement[2], self.m_obj, self.m_params)
            return s.run_statement(method, fields)
        #will only run this if condition evaluates to false and there is a statement to run if false
        elif len(self.m_statement[2:]) == 2:
            s = statement(self.interpreter, self.m_statement[3], self.m_obj, self.m_params)
            return s.run_statement(method, fields)     

    def getParams(self, params, fields):
        values = [expression(self.interpreter, x, self.m_obj, self.m_params, fields).evaluate() for x in self.m_statement[3:]]
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