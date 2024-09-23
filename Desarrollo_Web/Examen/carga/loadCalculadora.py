from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
import os
from modelo.calculadora import Calculadora

dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/calculadora.ui")

class CalculadoraInter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.operaciones = Calculadora()
        self.iniciarUi()
    
    def iniciarUi(self):
        self.calculadora = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height())  
        self.calculadora.mas.clicked.connect(self.opsuma)
        self.calculadora.menos.clicked.connect(self.opresta)
        self.calculadora.multi.clicked.connect(self.opmultiplicacion)
        self.calculadora.division.clicked.connect(self.opdivision)
        self.calculadora.residuo.clicked.connect(self.opresiduo)
        
        self.calculadora.clear.clicked.connect(self.opclear)
    
    def obtenerNumeros(self):
        try:
            numeroUno = float(self.calculadora.primer.text())
            numeroDos = float(self.calculadora.segundo.text())
        except ValueError:
            self.calculadora.resultado.setText("Error: Entrada no válida")
            return None, None
        return numeroUno, numeroDos
    
    def opsuma(self):
        numeroUno, numeroDos = self.obtenerNumeros()
        
        suma = Calculadora(numeroUno, numeroDos) 
        resultado = suma.suma()
        self.calculadora.resultado.setText(str(resultado))

    def opresta(self):
        numeroUno, numeroDos = self.obtenerNumeros()

        resta = Calculadora(numeroUno, numeroDos)  
        resultado = resta.resta()
        self.calculadora.resultado.setText(str(resultado))

    def opmultiplicacion(self):
        numeroUno, numeroDos = self.obtenerNumeros()

        multiplicacion = Calculadora(numeroUno, numeroDos)  
        resultado = multiplicacion.multiplicacion()
        self.calculadora.resultado.setText(str(resultado))
        
    def opdivision(self):
        numeroUno, numeroDos = self.obtenerNumeros()

        division = Calculadora(numeroUno, numeroDos)  
        resultado = division.division()
        self.calculadora.resultado.setText(str(resultado))
        
    def opresiduo(self):
        numeroUno, numeroDos = self.obtenerNumeros()
        residuo = Calculadora(numeroUno, numeroDos)  
        resultado = residuo.residuo()
        self.calculadora.resultado.setText(str(resultado))
        
    def opclear(self):
        self.calculadora.primer.setText("")
        self.calculadora.segundo.setText("")
        self.calculadora.resultado.setText("")