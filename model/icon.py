class Icon():
    def __init__(self,name,endereco):
        self.name = name
        self.endereco = endereco
    
    def to_dict(self):
        return {'name': self.name, 'endereco': self.endereco}