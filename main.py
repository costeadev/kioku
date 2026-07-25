import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPlainTextEdit
from PySide6.QtGui import QFontDatabase


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kioku")

        editor = QPlainTextEdit()

        self.setCentralWidget(editor)

if __name__ == "__main__":
    app = QApplication([])

    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
            font_id = QFontDatabase.addApplicationFont("fonts/ComicRelief-Regular.ttf")
            families = QFontDatabase.applicationFontFamilies(font_id)
            print(families)
    except FileNotFoundError:
        print("Style file not found, running with default theme.")

    window = MainWindow()
    window.setFixedSize(QSize(600, 600))
    window.show()

    app.exec()
