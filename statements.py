from intbase import ErrorType
from expressions import expression
from values import value, types
from classes import classDef

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
                        return r

            case self.interpreter.CALL_DEF:
                    #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
                match self.m_statement[1]:
                    case self.interpreter.ME_DEF:
                        self.evalparams(fields, vlocal)
                        m, o = self.m_obj.me.getMethod(self.m_statement[2], self.m_params)
                        self.getParams(m.params)
                        o.run_method(m, self.m_params)
                    case self.interpreter.SUPER_DEF:
                        if not self.m_obj.parent:
                            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid call to super object by class {self.m_obj.m_class}')
                        self.evalparams(fields, vlocal)
                        m, o = self.m_obj.parent.getMethod(self.m_statement[2], self.m_params)
                        self.getParams(m.params)
                        o.run_method(m, self.m_params)
                    case _:
                        val = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
                        if not val.m_value:
                            self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                        elif not isinstance(val.type, classDef):
                             self.interpreter.error(ErrorType.FAULT_ERROR, description=f'invalid object pointer {self.m_statement[1]}')
                        obj = val.m_value
                        self.evalparams(fields, vlocal)
                        m, o = obj.getMethod(self.m_statement[2], self.m_params)
                        self.getParams(m.params)
                        o.run_method(m, self.m_params)

            case self.interpreter.IF_DEF:
                #DEBUGGING
                if self.interpreter.trace:
                    self.interpreter.output(f'IF STATEMENT with condition {self.m_statement[1]}')

                return self.handleIf(method, fields, vlocal)

            case self.interpreter.INPUT_INT_DEF:
                v = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
                if v.type != types.INT:
                    self.interpreter.output(ErrorType.TYPE_ERROR)
                self.handleInput(types.INT, v, vlocal)

            case self.interpreter.INPUT_STRING_DEF:
                v = expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
                if v.type != types.STRING:
                    self.interpreter.output(ErrorType.TYPE_ERROR)
                self.handleInput(types.STRING, v, vlocal)

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

                if len(self.m_statement) == 2:
                    if self.m_statement[1] == 'null':
                        if self.rval.type == types.BOOL or self.rval.type == types.INT or self.rval.type == types.STRING or self.rval.type == types.NOTHING:
                            self.interpreter.error(ErrorType.TYPE_ERROR)
                        else:
                            return value(self.rval.type, None)

                    return expression(self.interpreter, self.m_statement[1], self.m_obj, self.m_params, fields, vlocal).evaluate()
                else:
                    return self.rval

            case self.interpreter.SET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'SET variable {self.m_statement[1]} to {self.m_statement[2]}')

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
                        if self.interpreter.trace:
                            self.interpreter.output(f'EXIT LET scope {self.m_statement[1]}')
                        break

                #pop the let scope off local variable stack when done
                vlocal.pop()
                return r
                
            case self.interpreter.WHILE_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'WHILE LOOP with condition {self.m_statement[1]}')

                return self.handleWhile(method, fields, vlocal)

            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'Invalid statement command "{self.m_statement[0]}" ')

    def handleSet(self, fields, vlocal):

        val = expression(self.interpreter, self.m_statement[2], self.m_obj, self.m_params, fields, vlocal).evaluate()
        fieldnames = [f.m_name for f in fields]

        if any([self.m_statement[1] in vlocal[i] for i in range(len(vlocal))]):
            if self.interpreter.trace:
                self.interpreter.output(f'setting local variable {self.m_statement[1]}')
            #set the local variable
            for i in range(len(vlocal)-1, -1, -1):
                if self.m_statement[1] in vlocal[i]:
                    self.setvar(self.m_statement[1], vlocal[i], val)
                    break
        elif self.m_statement[1] in self.m_params:
            self.setvar(self.m_statement[1], self.m_params, val)
        elif self.m_statement[1] in fieldnames:
            for i in range(len(fields)):
                if self.m_statement[1] == fieldnames[i]:
                    field = fields[i]
                    break
            if field.type == val.type:
                field.setvalue(val)
            elif isinstance(field.type, classDef):
                if val.type == types.NULL: #null
                    val.type = field.type
                    field.setvalue(val)
                elif isinstance(val.type, classDef):
                    if self.typematch(field.type, val.type):
                        field.setvalue(val)
                    else:
                        self.interpreter.error(ErrorType.TYPE_ERROR)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        else:
            self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown variable {self.m_statement[1]}')
        
    def setvar(self, var, dict, value):
        if dict[var].type == value.type:
            dict[var] = value
        elif isinstance(dict[var].type, classDef): 
            if value.type == types.NULL: #null
                value.type = dict[var].type
                dict[var] = value
            elif isinstance(value.type, classDef):
                if self.typematch(dict[var].type, value.type):
                    dict[var] = value
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        else:
            self.interpreter.error(ErrorType.TYPE_ERROR)

    def typematch(self, var, val):

        if var == val:
            return True
        elif isinstance(var, classDef) and isinstance(val, classDef):
            #can only pass a child object into a function that expects a parent object
            return self.typematch(var, val.parent) #parents and grandparents
        else:
            return False

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
        t = [self.interpreter.types[vars[i][0]] for i in range(len(vars))]
        names = [vars[i][1] for i in range(len(vars))]
        vals = [expression(self.interpreter, vars[i][2], self.m_obj, self.m_params, fields, vlocal).evaluate() for i in range(len(vars))]

        d = {}

        for i in range(len(vars)):
            if names[i] in d:
                self.interpreter.error(ErrorType.NAME_ERROR) #duplicate let variables
            elif t[i] == vals[i].type:
                d[names[i]] = vals[i]
            elif isinstance(t[i], classDef) and vals[i].type == types.NULL: #null
                vals[i].type = t[i]
                d[names[i]] = vals[i]
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR, description=f"invalid type/type mismatch with local variable {names[i]}")

        if self.interpreter.trace:
            self.interpreter.output(f'local variable scope with vars: {[names[i] +":"+ str(vals[i]) for i in range(len(vars))]}')

        return d

    def evalparams(self, fields, vlocal):
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATING PARAMETERS {self.m_statement[3:]}')

        self.m_params = [expression(self.interpreter, x, self.m_obj, self.m_params, fields, vlocal).evaluate() for x in self.m_statement[3:]]

    def getParams(self, params):
        if self.interpreter.trace:
            self.interpreter.output(f"GETTING PARAMETERS {params}")

        #at this point parameter type and number checking has already happened

        pdict = {params[i][1]:self.m_params[i] for i in range(len(self.m_params))}
        self.m_params = pdict

    def handleInput(self, type, val, vlocal):

        fieldnames = [f.m_name for f in self.m_obj.getfields()]
        
        if any([self.m_statement[1] in vlocal[i] for i in range(len(vlocal))]):
            for i in range(len(vlocal)-1, -1, -1):
                if self.m_statement[1] in vlocal[i]:
                    self.setvar(self.m_statement[1], vlocal[i], val)
                    break
        elif self.m_statement[1] in self.m_params:
            self.setvar(self.m_statement[1], self.m_params, val)
        elif self.m_statement[1] in fieldnames:
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