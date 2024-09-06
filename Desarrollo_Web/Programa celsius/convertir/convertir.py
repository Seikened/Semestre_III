from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from modelos.red import ModeloCelsiusFahrenheit

dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/convertir.ui")


class ConvertirCelsiusFahrenheit(QDialog):
    def __init__(self):
        super().__init__()
        self.modelo = ModeloCelsiusFahrenheit()
        self.inicializarUI()

    def inicializarUI(self):
        # Cargar la UI
        self.convertirCelsius = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height())
        self.modelo.entrenar()

        # Listener: Cambié el nombre del método a convertir_temperatura
        self.convertirCelsius.convertir.clicked.connect(self.convertir_temperatura)

        self.show()
        
        
    def validar(self,numero):
        try:
            float(numero)
            return True
        except ValueError:
            if numero.strip() == "":
                self.label.setText("Ingrese un valor")
            else:
                self.label.setText("Ingrese un valor válido")
            return False

    def convertir_temperatura(self):
        # Obtener el valor de Celsius y convertir a Fahrenheit
        celsius = self.celsius.text()
        
        if not self.validar(celsius):
            return None

        fahrenheit = self.modelo.predecir(float(celsius))
        self.label.setText("Valor en Fahrenheit")
        # Mostrar el valor en el campo Fahrenheit
        self.farenheit.setText(str(fahrenheit))
        
    
    def clear(self):
        self.celsius.clear()
        self.farenheit.clear()
        self.celsius.setFocus()
    