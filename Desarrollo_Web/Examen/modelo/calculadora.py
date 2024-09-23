class Calculadora():
    def __init__(self, numeroUno=0, numeroDos=0):
        self.numeroUno = numeroUno
        self.numeroDos = numeroDos
        self.resultado = 0
        
    def suma(self):
        self.resultado = self.numeroUno + self.numeroDos
        return self.resultado
    
    def resta(self):
        self.resultado = self.numeroUno - self.numeroDos
        return self.resultado
    
    def multiplicacion(self):
        self.resultado = self.numeroUno * self.numeroDos
        return self.resultado
    
    def division(self):
        if self.numeroDos == 0:
            return "Error: División por cero"
        self.resultado = self.numeroUno / self.numeroDos
        return self.resultado
    
    def residuo(self):
        if self.numeroDos == 0:
            return "Error: División por cero"
        self.resultado = self.numeroUno % self.numeroDos
        return self.resultado
    