
import sys
from PyQt6.QtWidgets import QApplication
from menu.menu import MenuClass


def main():
    app = QApplication(sys.argv)
    dialogo= MenuClass()
    dialogo.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()