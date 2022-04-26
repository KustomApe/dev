class Uranai():
    def __init__(self, name):
        self.name = name
        self.age = 31
    def bloodtypeO(self, name):
        print('あなたはO型')
    def bloodtypeA(self, name):
        print('あなたはA型')
    def bloodtypeB(self, name):
        print('あなたはB型')
    def bloodtypeAB(self, name):
        print('あなたはAB型')

one = Uranai()
print(one.name)
