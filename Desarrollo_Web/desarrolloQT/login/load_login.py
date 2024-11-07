import sys
from PyQt6.QtWidgets import QDialog,QApplication, QWidget, QMessageBox
from PyQt6 import uic
import os
from login.load_principal import Load_principal
from modelo.usuario import Usuario

dir = os.path.abspath(__file__)
dir = os.path.dirname(dir)
dir = os.path.dirname(dir)

ui = os.path.join(dir, "ui/login.ui")

class Load_login(QDialog):
    def __init__(self):
        super().__init__()
        self.inicializarUI()
        
    
    def inicializarUI(self):
        self.login = uic.loadUi(ui,self)
        self.login.setFixedSize(self.width(),self.height())
        self.login.lblMensaje.setText("")
        
        # Listener
        self.login.btnIngresar.clicked.connect(self.onClickBtnIngresar)
        
        self.show()
    
    def onClickBtnIngresar(self):
        usuario = Usuario()
        usuario.nickname = self.login.txtUsuario.text()
        usuario.password = self.login.txtPassword.text()
        
        if usuario.validarAcceso():
            self.login.close()
            self.principal = Load_principal(self.login)
            self.principal.show()
            
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")
    
    def registrar(self):
        pass
    
    
    def login(self):
        pass