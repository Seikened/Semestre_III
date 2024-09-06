


class Usuario():
    def __init__(self):
        self.nickname = ""
        self.password = ""
        self.nombre = ""

    def validarAcceso(self):
        return True if self.nickname == "admin" and self.password == "admin" else False

        