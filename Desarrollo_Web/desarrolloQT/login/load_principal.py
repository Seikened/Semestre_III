import sys
from PyQt6.QtWidgets import QMainWindow, QDialog
from PyQt6 import uic
import os

dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/principal.ui")

class Load_principal(QMainWindow):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.inicializarUI()
        
        
    
    def inicializarUI(self):
        self.principal = uic.loadUi(ui,self)
        self.principal.setFixedSize(self.width(),self.height())
        
        # Listener
        self.principal.pushButton.clicked.connect(self.onClickBtnCerrar)
        
        self.show()
    
    def onClickBtnCerrar(self):
        self.principal.close()
        self.login.show()