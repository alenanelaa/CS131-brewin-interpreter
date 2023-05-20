from intbase import ErrorType
from values import value, types
from classes import classDef

class expression:
    binops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=', '&', '|'}
    unops = {'!'}

    def __init__(self, inter, expr, o, p, f, l): #UPDATE ALL CREATIONS OF EXPRESSION OBJECT TO INCLUDE LOCAL VARS
        self.interpreter, self.m_expr, self.m_obj, self.m_params, self.m_fields, self.local = inter, expr, o, p, f, l

    def evaluate(self):
        #DEBUGGING
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATE expression {self.m_expr}')

        #constant or field
        if isinstance(self.m_expr, str):
            r =  self.getValue(self.m_expr)
        elif self.m_expr[0] == self.interpreter.CALL_DEF:
            if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_expr[2]} in object {self.m_expr[1]} with args {self.m_expr[3:]}')
            match self.m_expr[1]:
                case self.interpreter.ME_DEF:
                    m = self.m_obj.getMethod(self.m_expr[2])
                    self.getParams(m.params)
                    r = self.m_obj.run_method(m, self.m_params, self.m_fields)
                case _:
                    val = expression(self.interpreter, self.m_expr[1], self.m_obj, self.m_params, self.m_fields, self.local).evaluate()
                    if val.type == types.VOID:
                        self.interpreter.error(ErrorType.FAULT_ERROR, description='null dereference')
                    elif not isinstance(val.type, classDef):
                        self.interpreter.error(ErrorType.FAULT_ERROR, description = f'invalid object pointer {self.m_expr[1]}')
                    obj = val.m_value
                    m = obj.getMethod(self.m_expr[2])
                    self.getParams(m.params)
                    r = obj.run_method(m, self.m_params, obj.getfields())
        elif self.m_expr[0] == self.interpreter.NEW_DEF:
            cdef = self.interpreter.findClassDef(self.m_expr[1])
            obj = cdef.instantiate_object()
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
                #type checking
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.INT, arg1 + arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.STRING, arg1 + arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '-':
                #type checking
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 - arg2)
            case '*':
                #type checking
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 * arg2)
            case '/':
                #type checking
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 // arg2)
            case '%':
                #type checking
                if arg1.type != types.INT or arg2.type != types.INT:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 % arg2)     
            #boolean operators/comparators
            case '<':
                #type checking
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.BOOL, arg1 < arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.BOOL, arg1 < arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>':
                #type checking
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.BOOL, arg1 > arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.BOOL, arg1 > arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '<=':
                #type checking
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.BOOL, arg1 <= arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.BOOL, arg1 <= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>=':
                if arg1.type == types.INT and arg2.type == types.INT:
                    return value(types.BOOL, arg1 >= arg2)
                elif arg1.type == types.STRING and arg2.type == types.STRING:
                    return value(types.BOOL, arg1 >= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '==':
                if arg1.type == types.VOID or arg2.type == types.VOID:
                    return value(types.BOOL, arg1 == arg2)
                elif arg1.type != arg2.type:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                else:
                    return value(types.BOOL, arg1 == arg2)
            case '!=':
                if arg1.type == types.VOID or arg2.type == types.VOID:
                    return value(types.BOOL, arg1 != arg2)
                elif arg1.type != arg2.type:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                else:
                    return value(types.BOOL, arg1 != arg2)
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

    def getValue(self, token):

        local = self.searchlocals(token, self.local)
        #edge case for params because they are already mapped to values
        if isinstance(token, value):
            return token

        #recursion support
        elif isinstance(token, list):
            val = expression(self.interpreter, token, self.m_obj, self.m_params, self.m_fields, self.local).evaluate()
        elif token == 'null':
            val = value(types.VOID, None)
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
        elif all(c.isdigit() for c in token):
            val = value(types.INT, int(token))
        else:
            self.interpreter.error(ErrorType.NAME_ERROR)
        return val
    
    def isfieldname(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return True
        return False

    #only gets called if fieldname is a valid, defined field
    def getField(self, fieldname):
        for f in self.m_fields:
            if f.m_name == fieldname:
                return f
    
    def getParams(self, params):
        if self.interpreter.trace:
            self.interpreter.output(f"GETTING PARAMETERS {params}")

        values = [expression(self.interpreter, x, self.m_obj, self.m_params, self.m_fields, self.local).evaluate() for x in self.m_expr[3:]]
        if len(values) != len(params):
            self.interpreter.error(ErrorType.TYPE_ERROR, description="Incorrect number of parameters")

        pdict = {}

        for i in range(len(params)):
            if self.interpreter.types[params[i][0]] != values[i].type:
                self.interpreter.error(ErrorType.TYPE_ERROR)
            pdict[params[i][1]] = values[i]       
        
        self.m_params = pdict

    def searchlocals(self, token, localvars):
        for i in range(len(localvars)-1, -1, -1):
            if token in localvars[i]:
                return localvars[i][token]
        
        return