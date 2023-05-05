from values import value


#inputs have a name and an associated value
class inputDef:
    def __init__(self, name, val):
        self.m_name = name
        self.m_val = val

    def __str__(self):
        return str(self.m_val)