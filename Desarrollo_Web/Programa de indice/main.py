from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys
from interfaz.login import Login


def main():
    app = QApplication(sys.argv)
    login= Login()
    login.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main