from PySide6.QtCore import QSize, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout, \
    QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QFontDatabase, QColor


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.sidebar_width = 250
        self.sidebar_open = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar container
        self.top_bar = QWidget()
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)

        self.button = QPushButton("☰")
        self.button.clicked.connect(self.toggle_sidebar)

        top_layout.addWidget(self.button)
        top_layout.addWidget(QLabel("Writing Zone"))
        top_layout.addStretch()

        main_layout.addWidget(self.top_bar)

        # Content container
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Editor
        self.editor = QPlainTextEdit()
        content_layout.addWidget(self.editor)

        main_layout.addWidget(content)

        # Sidebar
        self.sidebar = QFrame(self)
        self.sidebar.setFixedWidth(self.sidebar_width)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(3, 0)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.sidebar.setGraphicsEffect(shadow)

        # Animation
        self.animation = QPropertyAnimation(self.sidebar, b"pos")
        self.animation.setDuration(250)

        # Object names for QSS
        content.setObjectName("content")
        self.top_bar.setObjectName("topBar")
        self.editor.setObjectName("editor")
        self.sidebar.setObjectName("sidebar")

    def resizeEvent(self, event):
        super().resizeEvent(event)

        y = self.top_bar.height()

        # Update sidebar size
        self.sidebar.resize(
            self.sidebar_width,
            self.height() - y
        )

        # Keep it in the correct position
        x = 0 if self.sidebar_open else -self.sidebar_width
        self.sidebar.move(x, y)

    def toggle_sidebar(self):
        y = self.top_bar.height()

        if self.sidebar_open:
            start = QPoint(0, y)
            end = QPoint(-self.sidebar_width, y)
        else:
            start = QPoint(-self.sidebar_width, y)
            end = QPoint(0, y)

        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

        self.sidebar_open = not self.sidebar_open

if __name__ == "__main__":
    app = QApplication([])

    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())

            QFontDatabase.addApplicationFont(
                "fonts/ComicRelief-Regular.ttf"
            )
    except FileNotFoundError:
        print("Style file not found, running with default theme.")

    window = Window()
    window.resize(900, 600)
    window.show()

    app.exec()
