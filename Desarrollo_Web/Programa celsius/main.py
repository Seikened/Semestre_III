from convertir.convertir import ConvertirCelsiusFahrenheit
import sys
from PyQt6.QtWidgets import QApplication



def main():
    app = QApplication(sys.argv)
    dialogo= ConvertirCelsiusFahrenheit()
    dialogo.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()