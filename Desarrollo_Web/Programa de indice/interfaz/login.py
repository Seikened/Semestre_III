from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6 import uic
import os
from .mainInterfaz import mainInterfaz


dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/interfaz.ui")



class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.iniciarUi()
    
    
    def iniciarUi(self):
        self.login = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height())
        self.login.ingresar.clicked.connect(self.entrar)
    
    def entrar(self):
        self.login.close()
        self.principal = mainInterfaz(self.login)
        self.principal.show()