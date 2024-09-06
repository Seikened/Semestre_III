from login.load_login import Load_login
import sys
from PyQt6.QtWidgets import QApplication



def main():
    app = QApplication(sys.argv)
    dialogo= Load_login()
    dialogo.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()