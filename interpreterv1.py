from intbase import InterpreterBase, ErrorType
from bparser import BParser

class Interpreter(InterpreterBase):
    def __init__(self):
        self.something = 0
        super().__init__()

    def run(self, program):
        print("Not Implemented")