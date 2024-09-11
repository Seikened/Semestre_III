from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6 import uic
import os
from .mainInterfaz import *


dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/calculadora.ui")



class mainInterfaz(QMainWindow):
    def __init__(self, login):
        self.login = login
        super().__init__()
        self.iniciarUi()
    
    
    def iniciarUi(self):
        self.calculadora = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height())
        self.calculadora.calcularBtn.clicked.connect(self.imc)
    
    def validar(self,numero):

        try:
            float(numero)
            return True
        except ValueError:
            if numero.strip() == "":
                return False
            else:
                return False

    
    def imc(self):
        # calculamos el indice de masa corporal
        peso = self.calculadora.pesoIn.text()
        altura = self.calculadora.alturaIn.text()
        
        pesoValidado = self.validar(peso)
        alturaValidada = self.validar(altura)
        imc = 0
        
        if pesoValidado and alturaValidada:
            imc = float(peso) / (float(altura) ** 2)
            self.calculadora.imcOut.setText(str(imc))
        else:
            self.calculadora.imcOut.setText("Error")
            return False
        
        
        # Caos de bajo peso, Normal, Sobrepeso, Obesidad, obesidad mórbida
        
        if imc < 18.5:
            self.calculadora.interpretacion.setText("Bajo peso")
        elif imc >= 18.5 and imc < 24.9:
            self.calculadora.interpretacion.setText("Normal")
        elif imc >= 25 and imc < 29.9:
            self.calculadora.interpretacion.setText("Sobrepeso")
        elif imc >= 30 and imc < 34.9:
            self.calculadora.interpretacion.setText("Obesidad")
        else:
            self.calculadora.interpretacion.setText("Obesidad mórbida")
            