from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys
from PyQt6 import uic

from carga.loadCalculadora import CalculadoraInter



def main():

    app = QApplication(sys.argv)
    calculadora= CalculadoraInter()
    calculadora.show()
    sys.exit(app.exec())
    

if __name__ == '__main__':
    main()