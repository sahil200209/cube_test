from PySide6.QtWidgets import QApplication
from gui.win_main import WinMain
import sys
import os

if __name__ == "__main__":
    app = QApplication( sys.argv )

    window = WinMain( )
    window.show()

    sys.exit( app.exec())