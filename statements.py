from intbase import ErrorType
from expressions import expression
from values import value, types

class statement:

    def __init__(self, inter, s, o, p, r):
        self.interpreter, self.m_statement, self.m_obj, self.m_params, self.rval = inter, s, o, p, r

    def run_statement(self, method, fields, vlocal):
        
        a = self.m_statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output('ENTER BEGIN BLOCK')

                steps = [statement(self.interpreter, line, self.m_obj, self.m_params, self.rval) for line in self.m_statement[1:]]
                for s in steps:
                    r = s.run_statement(method, fields, vlocal)

                    if r: #if statement returns anything besides None, that means it was a return statement
                        break

            case self.interpreter.CALL_DEF:
                    #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
                match self.m_statement[1]:
                    case self.interpreter.ME_DEF:
                        m = self.m_obj.getMethod(self.m_statement[2])
                        self.getParams(m.params, fields, vlocal)
                        self.m_obj.run_method(m, self.m_params, fields)
                    case _:
                        val = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
                        if val.type == types.VOID: #might have to change to if not val.type (None)
                            self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                        # elif val.m_type != types.OBJECT:
                        #     self.interpreter.error(ErrorType.FAULT_ERROR, description=f'invalid object pointer {self.m_statement[1]}')
                        obj = val.m_value
                        m = obj.getMethod(self.m_statement[2])
                        self.getParams(m.params, fields, vlocal)
                        obj.run_method(m, self.m_params, obj.getfields())

            case self.interpreter.IF_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'IF STATEMENT with condition {self.m_statement[1]}')

                return self.handleIf(method, fields, vlocal)

            case self.interpreter.INPUT_INT_DEF:
                self.handleInput(types.INT)

            case self.interpreter.INPUT_STRING_DEF:
                self.handleInput(types.STRING)

            case self.interpreter.PRINT_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'PRINT expressions {self.m_statement[1:]}')

                #list of expression objects to be printed
                exprs = [expression(self.interpreter, e, self.m_obj, self.m_params, fields, vlocal) for e in self.m_statement[1:]]
                self.handlePrint(exprs)

            case self.interpreter.RETURN_DEF:
                if self.interpreter.trace:
                    self.interpreter.output("RETURN from method called")

                self.interpreter.stackpop()
                method.stackframe -= 1
                if len(self.m_statement) == 2:
                    expr = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal)
                    return expr.evaluate()
                else:
                    return self.rval

            case self.interpreter.SET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'SET variable {self.m_statement[1]} to {self.m_statement[2]}')
                #check if in locals then params then fields for shadowing
                self.handleSet(fields, vlocal)

            case self.interpreter.LET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'LET local variables: {self.m_statement[1]}')

                #returns dictionary of local variables in the let statement (with type checking in the function)
                vars = self.handleLet(self.m_statement[1], fields, vlocal)
                #vlocal stack of let scopes passed from method (method private variable)
                vlocal.append(vars) #pushes scope on stack

                steps = [statement(self.interpreter, line, self.m_obj, self.m_params, self.rval) for line in self.m_statement[2:]]
                for s in steps:
                    r = s.run_statement(method, fields, vlocal)

                    if r: #if statement returns anything besides None, that means it was a return statement
                        break

                #pop the let scope off local variable stack when done
                vlocal.pop()
                

            case self.interpreter.WHILE_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'WHILE LOOP with condition {self.m_statement[1]}')

                return self.handleWhile(method, fields, vlocal)

            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'Invalid statement command "{self.m_statement[0]}" ')

    def handleSet(self, fields, vlocal):

        val = expression(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, fields, vlocal).evaluate()
        fieldnames = [f.m_name for f in fields]

        if any(self.m_statement[1] in vlocal[i] for i in range(len(vlocal))):
            #set the local variable
            for i in range(len(vlocal)-1, -1, -1):
                if self.m_statement[1] in vlocal[i] and vlocal[i][self.m_statement[1]].type == val.type: #reconsider this for inherited types
                    vlocal[i][self.m_statement[1]] = val
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
        elif self.m_statement[1] in self.m_params:
            if self.m_params[self.m_statement[1]].type == val.type:
                self.m_params[self.m_statement[1]] = val
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        elif self.m_statement[1] in fieldnames:
            for i in range(len(fields)):
                if fieldnames[i] == fields[i].m_name:
                    field = fields[i]
                    break
            if field.type == val.type:
                field.setvalue(val)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        else:
            self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown variable {self.m_statement[1]}')

    def handleWhile(self, method, fields, vlocal):
        cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
        if cond.type != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean while condition')

        while cond.m_value:
            if self.interpreter.trace:
                self.interpreter.output(f'condition {self.m_statement[1]} evaluated to {cond}')

            s = statement(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, self.rval)
            r = s.run_statement(method, fields, vlocal)
            
            #break out of while loop
            if r:
                return r

            cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
    
    def handleIf(self, method, fields, vlocal):
        cond = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()

        if cond.type != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean if condition')

        if self.interpreter.trace:
            self.interpreter.output(f'condition {self.m_statement[1]} evaluated to {cond}')

        if cond.m_value:
            s = statement(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, self.rval)
            return s.run_statement(method, fields, vlocal)
        #will only run this if condition evaluates to false and there is a statement to run if false
        elif len(self.m_statement[2:]) == 2:
            s = statement(self.interpreter, self.m_statement[3], self.m_obj, self.m_params, self.rval)
            return s.run_statement(method, fields, vlocal)     

    def handleLet(self, vars, fields, vlocal):
        types = [self.interpreter.types[vars[i][0]] for i in range(len(vars))]
        names = [vars[i][1] for i in range(len(vars))]
        vals = [expression(self.interpreter, vars[i][2], self.m_obj, self.m_params, fields, vlocal).evaluate() for i in range(len(vars))]

        for i in range(len(vars)):
            if types[i] != vals[i].type:
                self.interpreter.error(ErrorType.TYPE_ERROR, description=f"invalid type/type mismatch with local variable {names[i]}")

        if self.interpreter.trace:
            self.interpreter.output(f'local variable scope with vars: {[names[i] +":"+ str(vals[i]) for i in range(len(vars))]}')

        return {names[i]:vals[i] for i in range(len(vars))}

    def getParams(self, params, fields, vlocal):
        if self.interpreter.trace:
            self.interpreter.output(f"GETTING PARAMETERS {params}")
          
        values = [expression(self.interpreter, x, self.m_obj, self.m_params, fields, vlocal).evaluate() for x in self.m_statement[3:]]
        if len(values) != len(params):
            self.interpreter.error(ErrorType.TYPE_ERROR, description="Incorrect number of parameters")

        pdict = {}

        for i in range(len(params)):
            if self.interpreter.types[params[i][0]] != values[i].type:
                self.interpreter.error(ErrorType.TYPE_ERROR)
            pdict[params[i][1]] = values[i]       
        
        self.m_params = pdict

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