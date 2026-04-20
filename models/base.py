# Acá iría la clase donde debería tener lógica común, como un get, save, delete, etc. Es algo que importarán y extenderán el resto de modelos. De momento solo le agregué el parámetro "table" así como 3 métodos básicos porque no tengo idea de qué más agregarle

class Model:
    def __init__(self, table):
        self.table = table

    def get(self):
        pass

    def get_by_id(cls, id):
        pass

    def getAll(cls):
        pass

    def save(self):
        pass

    def update(self):
        pass

    def del(self):
        pass
