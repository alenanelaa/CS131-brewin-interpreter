from intbase import ErrorType
from values import value, types

class expression:
    binops = {'+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!='}
    unops = {'!'}

    def __init__(self, expr, c):
        self.m_expr = expr
        self.m_class = c

    def evaluate(self):
        #constant or field
        if isinstance(self.m_expr, str):
            return self.getValue(self.m_expr)
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

        match self.m_expr[0]:
            #arithmetic operators
            case '+':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.INT, arg1 + arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.STRING, arg1 + arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '-':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 - arg2)
            case '*':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 * arg2)
            case '/':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 // arg2)
            case '%':
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 % arg2)     
            #boolean operators/comparators
            case '<':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 < arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 < arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '>':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 > arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 > arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '<=':
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 <= arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 <= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '>=':
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.BOOL, arg1 >= arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.BOOL, arg1 >= arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '==':
                if arg1.gettype() == types.NULL or arg2.gettype() == types.NULL:
                    return value(types.BOOL, arg1 == arg2)
                elif arg1.gettype() != arg2.gettype():
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                else:
                    return value(types.BOOL, arg1 == arg2)
                return value(types.BOOL, arg1 == arg2)
            case '!=':
                if arg1.gettype() == types.NULL or arg2.gettype() == types.NULL:
                    return value(types.BOOL, arg1 != arg2)
                elif arg1.gettype() != arg2.gettype():
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                else:
                    return value(types.BOOL, arg1 != arg2)
            case _:
                #default case
                self.interpreter.error(ErrorType.SYNTAX_ERROR)

    def getValue(self, token):

        #recursion support
        if isinstance(token, list):
            val = expression(token, self.m_class).evaluate()
        elif token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"' and token[-1] == '"':
            val = value(types.STRING, token.strip('"'))
        elif any(not c.isdigit() for c in token):
            val = self.getField(token).getvalue()
        else:
            val = value(types.INT, int(token))
        return val
    
    def getField(self, fieldname):
        return self.m_class.getField(fieldname)
