from intbase import InterpreterBase, ErrorType
from fieldDef import value, types

class statement:
    def __init__(self, inter, s):
        self.m_statement = s
        self.interpreter = inter

    #may be better to do with if statements (to catch all the arithmetic operators versus method calls)
    def run_statement(self):
        match self.m_statement[0]:
            case 'begin':
                for s in self.m_statement[1:]:
                    step = statement(self.interpreter,s)
                    step.run_statement()
            case 'print':
                self.handlePrint(self.m_statement[1:])
            
            case '+':
                self.handleExpression()
            case '-':
                self.handleExpression()
            case '*':
                self.handleExpression()

    #all tokens passed in as strings
    #if there are quotation marks -> indicates string ('"4"' would be the string 4) 
    def getValue(self, token):
        if token == 'null':
            val = value(types.NULL, None)
        elif token == 'true' or token == 'false':
            val = value(types.BOOL, (token == 'true'))
        elif token[0] == '"':
            val = value(types.STRING, token.strip('"'))
            return val
        else:
            val = value(types.INT, int(token))
        return val
        

    #ADD TYPE CHECKING
    def handleExpression(self):
        match self.m_statement[0]:
            #arithmetic operators
            case '+':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                #type checking
                if isinstance(arg1.m_value, int) and isinstance(arg2.m_value, int):
                    return value(types.INT, arg1 + arg2)
                elif isinstance(arg1.m_value, str) and isinstance(arg2.m_value, str):
                    return value(types.STRING, arg1 + arg2)
                else:
                    self.interpreter.error(ErrorType.TYPE_ERROR)
            case '-':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 - arg2)
            case '*':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 * arg2)
            case '/':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 // arg2)
            case '%':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2]) 
                #type checking
                if not isinstance(arg1.m_value, int) or not isinstance(arg2.m_value, int):
                    self.interpreter.error(ErrorType.TYPE_ERROR)
                return value(types.INT, arg1 % arg2)     
            #boolean operators/comparators 
            case '!':
                arg = self.getValue(self.m_statement[1])
                #type checking
                return value(types.BOOL, not arg)
            case '<':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 < arg2)
            case '>':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 > arg2)
            case '<=':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 <= arg2)
            case '>=':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 >= arg2)
            case '==':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 == arg2)
            case '!=':
                arg1 = self.getValue(self.m_statement[1])
                arg2 = self.getValue(self.m_statement[2])
                return value(types.BOOL, arg1 != arg2)
            case _:
                #default case
                self.interpreter.error(ErrorType.SYNTAX_ERROR)


    def handlePrint(self, s):
        fprint = ''

        for item in s:
            if isinstance(item, list):
                val = statement(self.interpreter, item).handleExpression()
                fprint = fprint + str(val)
            else:
                fprint = fprint + str(item).strip('"')

        self.interpreter.output(fprint)
    