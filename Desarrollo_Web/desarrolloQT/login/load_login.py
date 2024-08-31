import sys
from PyQt6.QtWidgets import QDialog,QApplication, QWidget
from PyQt6 import uic
import os

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
        self.show()

def main():
    app = QApplication(sys.argv)
    dialogo= Load_login()
    dialogo.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()