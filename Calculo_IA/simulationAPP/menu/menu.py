from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
import os
from gradient.gradient import GradienteSimulacion

dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/interfaz.ui")



class MenuClass(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inicializarUI()
    
    
    def inicializarUI(self):
        self.menu = uic.loadUi(ui , self)
        self.setFixedSize(self.width(), self.height())

        self.menu.ecuation.setText("")
        self.menu.startSimulation.clicked.connect(self.simulation)
    
    
    def simulation(self):
        ecuation = self.menu.ecuation.text()
        GradienteSimulacion(ecuation)