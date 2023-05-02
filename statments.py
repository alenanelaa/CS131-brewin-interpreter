from intbase import InterpreterBase, ErrorType

class statement:
    def __init__(self):
        line = []

    def handlePrint(self, statement):
        InterpreterBase.output(statement)

    