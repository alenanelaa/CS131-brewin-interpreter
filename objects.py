from intbase import ErrorType
from classes import classDef
from values import types, value

class objDef:
    def __init__(self, inter, classDef, fields, parent=None, anchor = None):
        self.interpreter, self.m_class, self.m_fields = inter, classDef, fields

        if not anchor:
            self.me = self
        else:
            self.me = anchor

        if parent:
            f = [d.newfield() for d in parent.m_fields]
            self.parent = objDef(self.interpreter, parent, f, parent = parent.parent, anchor = self.me)
        else:
            self.parent = None

    def run_method(self, method, params):
        if self.interpreter.trace:
            p = [str(key) + ':' + str(params[key]) for key in params]
            self.interpreter.output(f'RUN {method.m_name} method: {method.m_statement} with params {p}')

        if method.m_statement[0] == self.interpreter.BEGIN_DEF:
            self.interpreter.stackpush(method.m_statement[1:])
        else:
            self.interpreter.stackpush([method.m_statement])

        stackframe = 1

        while stackframe > 0:
            cur_frame = self.interpreter.stackpop()
            stackframe -= 1

            if not cur_frame:
                break

            s = cur_frame.pop(0)

            self.interpreter.stackpush(cur_frame)
            stackframe += 1

            r = self.__run_statement(s, params, method.default_return, []) #empty list is local variables
        
            if r:
                stackframe -= 1

        if not r:
            return method.default_return
        
        if not method.typematch(method.default_return.type, r.type):
            self.interpreter.error(ErrorType.TYPE_ERROR)
        
        return r
    
    def __run_statement(self, statement, params, rval, localvar):
        a = statement[0]
        match a:
            case self.interpreter.BEGIN_DEF:
                if self.interpreter.trace:
                    self.interpreter.output('ENTER BEGIN BLOCK')

                steps = [line for line in statement[1:]]
                for s in steps:
                    r = self.__run_statement(s, params, rval, localvar)

                    if r: #if statement returns anything besides None, that means it was a return statement
                        return r

            case self.interpreter.CALL_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'CALL {statement[2]} in object {statement[1]} with args {statement[3:]}')

                parameters = self.__evalparams(statement[3:], params, localvar)
                self.__handleCall(statement[1], statement[2], params, parameters, localvar)

            case self.interpreter.IF_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'IF STATEMENT with condition {statement[1]}')
                return self.__handleIf(statement[1:], params, localvar, rval)

            case self.interpreter.INPUT_INT_DEF:
                v = self.__evaluate(statement[1], params, localvar)
                if v.type != types.INT:
                    self.interpreter.output(ErrorType.TYPE_ERROR)
                self.__handleInput(statement[1], types.INT, v, params, localvar)

            case self.interpreter.INPUT_STRING_DEF:
                v = self.__evaluate(statement[1], params, localvar)
                if v.type != types.STRING:
                    self.interpreter.output(ErrorType.TYPE_ERROR)
                self.__handleInput(statement[1], types.STRING, v, params, localvar)

            case self.interpreter.PRINT_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'PRINT expressions {statement[1:]}')
                #list of expression objects to be printed
                exprs = [e for e in statement[1:]]
                self.__handlePrint(exprs, params, localvar)

            case self.interpreter.RETURN_DEF:
                if self.interpreter.trace:
                    self.interpreter.output("RETURN from method called")

                self.interpreter.stackpop()

                if len(statement) == 2:
                    if statement[1] == 'null':
                        if rval.type == types.BOOL or rval.type == types.INT or rval.type == types.STRING or rval.type == types.NOTHING:
                            self.interpreter.error(ErrorType.TYPE_ERROR)
                        else:
                            return value(rval.type, None)
                    return self.__evaluate(statement[1], params, localvar)
                else:
                    return rval

            case self.interpreter.SET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'SET variable {statement[1]} to {statement[2]}')

                self.__handleSet(statement[1], statement[2], params, localvar)

            case self.interpreter.LET_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'LET local variables: {statement[1]}')
                #returns dictionary of local variables in the let statement (with type checking in the function)
                vars = self.__handleLet(statement[1], params, localvar)
                #vlocal stack of let scopes passed from method (method private variable)
                localvar.append(vars) #pushes scope on stack
                steps = [line for line in statement[2:]]
                for s in steps:
                    r = self.__run_statement(s, params, rval, localvar)

                    if r: #if statement returns anything besides None, that means it was a return statement
                        if self.interpreter.trace:
                            self.interpreter.output(f'EXIT LET scope {statement[1]}')
                        break
                #pop the let scope off local variable stack when done
                localvar.pop()
                return r
            case self.interpreter.WHILE_DEF:
                if self.interpreter.trace:
                    self.interpreter.output(f'WHILE LOOP with condition {statement[1]}')
                return self.__handleWhile(statement[1], statement[2], params, localvar, rval)
            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'Invalid statement command "{self.m_statement[0]}" ')
    
    def __evaluate(self, expr, params, localvar):
        binops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=', '&', '|'}
        unops = {'!'}

        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATE expression {expr}')
        #constant or variable
        if isinstance(expr, str):
            r =  self.__getValue(expr, params, localvar)
        elif expr[0] == self.interpreter.CALL_DEF:
            if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_expr[2]} in object {self.m_expr[1]} with args {self.m_expr[3:]}')

            parameters = self.__evalparams(expr[3:], params, localvar)
            r = self.__handleCall(expr[1], expr[2], params, parameters, localvar)
        elif expr[0] == self.interpreter.NEW_DEF:
            cdef = self.interpreter.findClassDef(expr[1])
            obj = self.interpreter.instantiate_object(cdef)
            return value(cdef, obj)
        elif expr[0] in binops:
            a1 = self.__getValue(expr[1], params, localvar)
            a2 = self.__getValue(expr[2], params, localvar)
            r =  self.__binaryExpression(expr[0], a1, a2)
        elif expr[0] in unops:
            arg = self.__getValue(expr[1], params, localvar)
            r =  self.__unaryExpression(expr[0], arg)
        else:
            self.interpreter.error(ErrorType.NAME_ERROR)
        return r

    def __getValue(self, token, params, localvar):
        if isinstance(token, str):
            local = self.searchlocals(token, localvar)
        #edge case for params because they are already mapped to values
        if isinstance(token, value):
            return token
        elif isinstance(token, list):
            val = self.__evaluate(token, params, localvar)
        elif token == 'me':
            val = value(self.m_class, self)
        elif token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
        elif local: #return local variable value if it exists
            return local
        elif token in params: #checks param names first in case there is shadowing of field names
            val = params[token]
        elif self.__isfieldname(token):
            val = self.getField(token).getvalue()
        elif all(c.isdigit() for c in token) or (token[0] == '-' and all(c.isdigit() for c in token[1:])):
            val = value(types.INT, int(token))
        else:
            self.interpreter.error(ErrorType.NAME_ERROR)
        return val

    def __handleCall(self, object, mname, params, parameters, localvar):
        match object:
            case self.interpreter.ME_DEF:
                m, o = self.me.getMethod(mname, parameters)
                p = self.getParams(m.params, parameters)
                r = o.run_method(m,p)
            case self.interpreter.SUPER_DEF:
                if not self.parent:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description = f'invalid call to super object by class {self.m_class.className}')
                m, o = self.parent.getMethod(mname, parameters)
                p = self.getParams(m.params, parameters)
                r = o.run_method(m,p)
            case _:
                val = self.__evaluate(object, params, localvar)
                if not val.m_value:
                    self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                elif not isinstance(val.type, classDef):
                    self.interpreter.error(ErrorType.FAULT_ERROR, description=f'invalid object pointer {object}')
                obj = val.m_value
                m, o = obj.getMethod(mname, parameters)
                p = self.getParams(m.params, parameters)
                r = o.run_method(m,p)
        return r

    def __handleInput(self, var, type, val, params, vlocal):

        fieldnames = [f.m_name for f in self.m_fields]
        
        if any([var in vlocal[i] for i in range(len(vlocal))]):
            for i in range(len(vlocal)-1, -1, -1):
                if var in vlocal[i]:
                    self.setvar(var, vlocal[i], val)
                    break
        elif var in params:
            self.setvar(var, params, val)
        elif var in fieldnames:
            f = self.getField(var)
            val = self.interpreter.get_input()
            if type == types.INT:
                val = int(val)
            f.setvalue(value(type, val))
    
    def __handleIf(self, st, params, vlocal, rval):
        cond = self.__evaluate(st[0], params, vlocal)
        if cond.type != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean if condition')
        if self.interpreter.trace:
            self.interpreter.output(f'condition {st[0]} evaluated to {cond}')
        if cond.m_value:
            return self.__run_statement(st[1], params, rval, vlocal)
        elif len(st[1:]) == 2:
            return self.__run_statement(st[2], params, rval, vlocal)
        
    def __handlePrint(self, s, params, localvar):
        fprint = ''
        for item in s:
            val = self.__evaluate(item, params, localvar)
            fprint = fprint + str(val)
        self.interpreter.output(fprint)
    
    def __handleSet(self, var, value, params, vlocal):
        val = self.__evaluate(value, params, vlocal)
        fieldnames = [f.m_name for f in self.m_fields]

        if any([var in vlocal[i] for i in range(len(vlocal))]):
            if self.interpreter.trace:
                self.interpreter.output(f'setting local variable {var}')
            #set the local variable
            for i in range(len(vlocal)-1, -1, -1):
                if var in vlocal[i]:
                    self.setvar(var, vlocal[i], val)
                    break
        elif var in params:
            self.setvar(var, params, val)
        elif var in fieldnames:
            field = self.getField(var)
            if field.type == val.type:
                field.setvalue(val)
            elif isinstance(field.type, classDef):
                if val.type == types.NULL: #null
                    val.type = field.type
                    field.setvalue(val)
                elif isinstance(val.type, classDef):
                    if self.__typematch(field.type, val.type):
                        field.setvalue(val)
                    else:
                        self.interpreter.error(ErrorType.TYPE_ERROR)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        else:
            self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown variable {var}')

    def __handleLet(self, vars, params, vlocal):
        t = [self.interpreter.types[vars[i][0]] for i in range(len(vars))]
        names = [vars[i][1] for i in range(len(vars))]
        vals = [self.__evaluate(vars[i][2], params, vlocal) for i in range(len(vars))]
        d = {} #empty dict to build local variable scope
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
    
    def __handleWhile(self, condition, st, params, vlocal, rval):

        cond = self.__evaluate(condition, params, vlocal)
        if cond.type != types.BOOL:
            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'Non-boolean while condition')

        while cond.m_value:
            if self.interpreter.trace:
                self.interpreter.output(f'condition {condition} evaluated to {cond}')
            r = self.__run_statement(st, params, rval, vlocal)
            #break out of while loop
            if r:
                return r
            cond = self.__evaluate(condition, params, vlocal)
    
    def __binaryExpression(self, op, arg1, arg2):
        err_msg = f'operator {op} applied to incompatible types'
        match op:
            #arithmetic operators
            case '+':
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.INT, arg1 + arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.STRING, arg1 + arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '-':
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 - arg2)
            case '*':
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 * arg2)
            case '/':
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 // arg2)
            case '%':
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 % arg2)     
            #boolean operators/comparators
            case '<':
                if (arg1.type == types.INT and arg2.type == types.INT) or (arg1.type == types.STRING and arg2.type == types.STRING):
                    return value(types.BOOL, arg1 < arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>':
                if (arg1.type == types.INT and arg2.type == types.INT) or (arg1.type == types.STRING and arg2.type == types.STRING):
                    return value(types.BOOL, arg1 > arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '<=':
                if (arg1.type == types.INT and arg2.type == types.INT) or (arg1.type == types.STRING and arg2.type == types.STRING):
                    return value(types.BOOL, arg1 <= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>=':
                if (arg1.type == types.INT and arg2.type == types.INT) or (arg1.type == types.STRING and arg2.type == types.STRING):
                    return value(types.BOOL, arg1 >= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '==':
                if self.__typematch(arg1.type, arg2.type) or self.__typematch(arg2.type, arg1.type) or (arg1.type == types.NULL or arg2.type == types.NULL):
                    return value(types.BOOL, arg1 == arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '!=':
                if self.__typematch(arg1.type, arg2.type) or (arg1.type == types.NULL or arg2.type == types.NULL):
                    return value(types.BOOL, arg1 != arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '&':
                if arg1.type != types.BOOL or arg2.type != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.BOOL, arg1.m_value and arg2.m_value)
            case '|':
                if arg1.type != types.BOOL or arg2.type != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.BOOL, arg1.m_value or arg2.m_value)
    
    def __unaryExpression(self, op, arg1):
        match op:
            case '!':
                if arg1.type != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.BOOL, not arg1)
    
    def __evalparams(self, p, params, vlocal):
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATING PARAMETERS {p}')
        return [self.__evaluate(x, params, vlocal) for x in p]

    def __isfieldname(self, fieldname):
        fnames = [f.m_name for f in self.m_fields]
        return fieldname in fnames

    def __typematch(self, var, val):
        if var == val:
            return True
        elif isinstance(var, classDef) and isinstance(val, classDef):
            return self.__typematch(var, val.parent) #parents and grandparents
        else:
            return False
    
    def setvar(self, var, dict, value):
        if dict[var].type == value.type:
            dict[var] = value
        elif isinstance(dict[var].type, classDef): 
            if value.type == types.NULL: #null
                value.type = dict[var].type
                dict[var] = value
            elif isinstance(value.type, classDef):
                if self.__typematch(dict[var].type, value.type):
                    dict[var] = value
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            else:
                self.interpreter.error(ErrorType.TYPE_ERROR)
        else:
            self.interpreter.error(ErrorType.TYPE_ERROR)

    def searchlocals(self, token, localvars):

        for i in range(len(localvars)-1, -1, -1):
            if token in localvars[i]:
                return localvars[i][token]

    def __eq__(self, other):
        return self is other
    
    def getParams(self, paramnames, paramvals):
        if self.interpreter.trace:
            self.interpreter.output(f"GETTING PARAMETERS {paramnames}")
        pdict = {paramnames[i][1]:paramvals[i] for i in range(len(paramnames))}
        return pdict
        
    def getMethod(self, mname, params):
        m = self.m_class.findMethodDef(mname, params)
        o = self

        if m == -1:
            if self.parent:
                return self.parent.getMethod(mname, params)
            else:
                self.interpreter.error(ErrorType.NAME_ERROR, description=f'unknown method {mname}')
        else:
            return m, o
    
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f
        self.interpreter.error(ErrorType.NAME_ERROR, description=f'field {fieldname} is not defined')