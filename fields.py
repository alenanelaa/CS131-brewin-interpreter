#class for brewin fields within a class
class field:
    def __init__(self, name, t, val):
        self.m_name = name
        self.type = t
        self.m_val = val

    def __str__(self):
        return str(self.m_val)

    def setname(self, name):
        self.m_name = name

    def setvalue(self, val):
        self.m_val = val

    def getname(self):
        return self.m_name

    def getvalue(self):
        return self.m_val