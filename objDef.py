from intbase import InterpreterBase, ErrorType

class objDef:
    def __init__(self, classtype):
        self.m_class = classtype

    def run_method(self, methodname):
        raise NotImplementedError
