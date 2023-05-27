from intbase import ErrorType
from values import value, types
from classes import classDef

class expression:
    binops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=', '&', '|'}
    unops = {'!'}

    def __init__(self, inter, expr, o, p, f, l):
        self.interpreter, self.m_expr, self.m_obj, self.m_params, self.m_fields, self.local = inter, expr, o, p, f, l

    def evaluate(self):
        #DEBUGGING
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATE expression {self.m_expr}')

        #constant or variable
        if isinstance(self.m_expr, str):
            r =  self.getValue(self.m_expr)
        elif self.m_expr[0] == self.interpreter.CALL_DEF:
            if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_expr[2]} in object {self.m_expr[1]} with args {self.m_expr[3:]}')
            match self.m_expr[1]:
                case self.interpreter.ME_DEF:
                    self.evalparams()
                    m, o = self.m_obj.me.getMethod(self.m_expr[2], self.m_params)
                    self.getParams(m.params)
                    r = o.run_method(m, self.m_params)
                case self.interpreter.SUPER_DEF:
                        if not self.m_obj.parent:
                            self.interpreter.error(ErrorType.TYPE_ERROR, description=f'invalid call to super object by class {self.m_obj.m_class}')
                        self.evalparams()
                        m, o = self.m_obj.parent.getMethod(self.m_expr[2], self.m_params)
                        self.getParams(m.params)
                        o.run_method(m, self.m_params)
                case _:
                    val = expression(self.interpreter, self.m_expr[1], self.m_obj, self.m_params, self.m_fields, self.local).evaluate()
                    if val.type == types.NULL:
                        self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                    elif not isinstance(val.type, classDef):
                        self.interpreter.error(ErrorType.FAULT_ERROR, description = f'invalid object pointer {self.m_expr[1]}')
                    obj = val.m_value
                    self.evalparams()
                    m, o = obj.getMethod(self.m_expr[2], self.m_params)
                    self.getParams(m.params)
                    r = o.run_method(m, self.m_params)
        elif self.m_expr[0] == self.interpreter.NEW_DEF:
            cdef = self.interpreter.findClassDef(self.m_expr[1])
            obj = self.interpreter.instantiate_object(cdef)
            return value(cdef, obj)
        elif self.m_expr[0] in expression.binops:
            r =  self.binaryExpression()
        elif self.m_expr[0] in expression.unops:
            r =  self.unaryExpression()
        else:
            self.interpreter.error(ErrorType.NAME_ERROR)
        return r

    def unaryExpression(self):
        arg1 = self.getValue(self.m_expr[1])

        match self.m_expr[0]:
            case '!':
                if arg1.type != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.BOOL, not arg1)
            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR)
    
    def binaryExpression(self):
        arg1 = self.getValue(self.m_expr[1])
        arg2 = self.getValue(self.m_expr[2])

        #type checking
        err_msg = f'operator {self.m_expr[0]} applied to incompatible types'

        match self.m_expr[0]:
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
                if self.typematch(arg1.type, arg2.type) or (arg1.type == types.NULL or arg2.type == types.NULL):
                    return value(types.BOOL, arg1 == arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '!=':
                if self.typematch(arg1.type, arg2.type) or (arg1.type == types.NULL or arg2.type == types.NULL):
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
            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'{self.m_expr[0]} is an invalid operator')

    def typematch(self, a1, a2):
        if a1 == a2:
            return True
        elif isinstance(a1, classDef) and isinstance(a2, classDef):
            #if one object is a parent/grandparent/etc of the other
            return self.typematch(a1, a2.parent) or self.typematch(a2, a1.parent)
        else:
            return False

    def getValue(self, token):

        if isinstance(token, str):
            local = self.searchlocals(token, self.local)
        #edge case for params because they are already mapped to values
        if isinstance(token, value):
            return token
        elif isinstance(token, list):
            val = expression(self.interpreter, token, self.m_obj, self.m_params, self.m_fields, self.local).evaluate()
        elif token == 'me':
            val = value(self.m_obj.m_class, self.m_obj)
        elif token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
        elif local: #return local variable value if it exists
            return local
        elif token in self.m_params: #checks param names first in case there is shadowing of field names
            val = self.m_params[token]
        elif self.isfieldname(token):
            val = self.getField(token).getvalue()
        elif all(c.isdigit() for c in token) or (token[0] == '-' and all(c.isdigit() for c in token[1:])):
            val = value(types.INT, int(token))
        else:
            self.interpreter.error(ErrorType.NAME_ERROR)
        return val
    
    def isfieldname(self, fieldname):
        fnames = [f.m_name for f in self.m_fields]
        return fieldname in fnames

    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f
    
    def evalparams(self):
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATING PARAMETERS {self.m_expr[3:]}')

        self.m_params = [expression(self.interpreter, x, self.m_obj, self.m_params, self.m_fields, self.local).evaluate() for x in self.m_expr[3:]]

    def getParams(self, params):
        if self.interpreter.trace:
            self.interpreter.output(f"GETTING PARAMETERS {params}")

        pdict = {params[i][1]:self.m_params[i] for i in range(len(self.m_params))}
        self.m_params = pdict

    def searchlocals(self, token, localvars):

        for i in range(len(localvars)-1, -1, -1):
            if token in localvars[i]:
                return localvars[i][token]