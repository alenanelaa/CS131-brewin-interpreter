from intbase import ErrorType
from values import value, types

class expression:
    binops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=', '&', '|'}
    unops = {'!'}

    def __init__(self, inter, expr, o, p, f):
        self.interpreter = inter
        self.m_expr = expr
        self.m_obj = o
        self.m_params = p
        self.m_fields = f

    def evaluate(self):
        #DEBUGGING
        if self.interpreter.trace:
            self.interpreter.output(f'EVALUATE expression {self.m_expr}')

        #constant or field
        if isinstance(self.m_expr, str):
            return self.getValue(self.m_expr)
        elif self.m_expr[0] == self.interpreter.CALL_DEF:
            if self.interpreter.trace:
                    self.interpreter.output(f'CALL {self.m_statement[2]} in object {self.m_statement[1]} with args {self.m_statement[3:]}')
            match self.m_expr[1]:
                case self.interpreter.ME_DEF:
                    m = self.m_obj.getMethod(self.m_expr[2])
                    self.getParams(m.params)
                    return self.m_obj.run_method(m, self.m_params, self.m_fields)
                case _:
                    pass
        elif self.m_expr[0] in expression.binops:
            return self.binaryExpression()
        elif self.m_expr[0] in expression.unops:
            return self.unaryExpression()
        else:
            pass

    def unaryExpression(self):
        arg1 = self.getValue(self.m_expr[1])
        match self.m_expr[0]:
            case '!':
                if not isinstance(arg1.m_value, bool):
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
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.INT, arg1 + arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.STRING, arg1 + arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '-':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 - arg2)
            case '*':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 * arg2)
            case '/':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 // arg2)
            case '%':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.INT, arg1 % arg2)     
            #boolean operators/comparators
            case '<':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 < arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 < arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 > arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 > arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '<=':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 <= arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 <= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '>=':
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 >= arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 >= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
            case '==':
                if arg1.gettype() == types.NULL or arg2.gettype() == types.NULL:
                    return value(types.BOOL, arg1 == arg2)
                elif arg1.gettype() != arg2.gettype():
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                else:
                    return value(types.BOOL, arg1 == arg2)
            case '!=':
                if arg1.gettype() == types.NULL or arg2.gettype() == types.NULL:
                    return value(types.BOOL, arg1 != arg2)
                elif arg1.gettype() != arg2.gettype():
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                else:
                    return value(types.BOOL, arg1 != arg2)
            case '&':
                if arg1.gettype() != types.BOOL or arg2.gettype() != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.BOOL, arg1.m_value and arg2.m_value)
            case '|':
                if arg1.gettype() != types.BOOL or arg2.gettype() != types.BOOL:
                    self.interpreter.error(ErrorType.TYPE_ERROR, description=err_msg)
                return value(types.BOOL, arg1.m_value or arg2.m_value)
            case _:
                self.interpreter.error(ErrorType.SYNTAX_ERROR, description=f'{self.m_expr[0]} is an invalid operator')

    def getValue(self, token):

        #recursion support
        if isinstance(token, list):
            val = expression(self.interpreter, token, self.m_obj, self.m_params, self.m_fields).evaluate()
        elif token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
        elif token in self.m_params: #checks param names first in case there is shadowing of field names
            val = self.getValue(self.m_params[token])
        elif self.isfieldname(token):
            val = self.getField(token).getvalue()
        elif all(c.isdigit() for c in token):
            val = value(types.INT, int(token))
        else:
            self.interpreter.error(ErrorType.SYNTAX_ERROR)
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
        values = [x for x in self.m_expr[3:]]
        if len(values) != len(params):
            self.interpreter.error(ErrorType.SYNTAX_ERROR, description="Incorrect number of parameters")
        
        self.m_params = {params[i]:values[i] for i in range(len(params))}
