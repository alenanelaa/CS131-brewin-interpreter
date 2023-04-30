from intbase import InterpreterBase, ErrorType
from bparser import BParser

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase’s constructor
        #begin with empty list of classes
        self.m_classes = []


    def run(self, program):
        indicator, tokens = BParser.parse(program)

        if not indicator:
            InterpreterBase.output("Parsing Error")
            return SystemError
        
