from PySide6.QtCore import QSize, QPropertyAnimation, QPoint, Qt, QTimer, QDateTime, QDate, QEvent
from PySide6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QVBoxLayout, \
    QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect, QMainWindow, QListWidget, QDateEdit, QCalendarWidget
from PySide6.QtGui import QFontDatabase, QColor
from pathlib import Path

journal_dir = Path("journal")

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.today = QDate.currentDate()
        self.cached_entries = None
        self.current_entry = None
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

        self.current_entry_label = QLabel("No entry loaded.")
        top_layout.addWidget(self.current_entry_label)
        top_layout.addStretch()

        main_layout.addWidget(self.top_bar)

        # Content container
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Text editor
        self.text_edit = QPlainTextEdit()
        self.text_edit.viewport().installEventFilter(self)

        content_layout.addWidget(self.text_edit)

        main_layout.addWidget(content)

        # Sidebar
        self.sidebar = QFrame(self)
        self.sidebar.setFixedWidth(self.sidebar_width)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(3, 0)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.sidebar.setGraphicsEffect(shadow)

        sidebar_layout = QVBoxLayout(self.sidebar)

        sidebar_title = QLabel("Journal")
        sidebar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sidebar_layout.addWidget(sidebar_title)

        self.new_entry_button = QPushButton("New Entry")
        sidebar_layout.addWidget(self.new_entry_button)

        self.list_widget = QListWidget()
        sidebar_layout.addWidget(self.list_widget)

        # Animation
        self.animation = QPropertyAnimation(self.sidebar, b"pos")
        self.animation.setDuration(250)

        # Object names for QSS
        content.setObjectName("content")
        self.top_bar.setObjectName("topBar")
        self.text_edit.setObjectName("textEdit")
        self.sidebar.setObjectName("sidebar")

        # Run auto-save timer
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_entry)
        self.text_edit.textChanged.connect(self.on_text_changed)

        if journal_dir.exists():
            print("Journal directory found, trying to cache entries...")
            self.recache_entries()
        else:
            journal_dir.mkdir(exist_ok=True)
            print("Journal directory didn't exist, creating...")

        self.list_widget.itemClicked.connect(self.on_entry_clicked)

        self.calendar = QCalendarWidget()
        self.calendar.hide()

        self.new_entry_button.clicked.connect(self.calendar.show)
        self.calendar.clicked.connect(self.on_date_selected)


    def closeEvent(self, event):
        self.save_entry()
        event.accept()

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

    def on_date_selected(self, date):
        self.calendar.hide()
        self.current_entry = date.toString("yyyy-MM-dd")
        self.save_entry()
        self.recache_entries()

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

    def recache_entries(self):
        try:
            self.cached_entries = sorted(journal_dir.glob("*.md"))

            self.list_widget.clear()

            if self.cached_entries:
                for file in self.cached_entries:
                    self.list_widget.addItem(file.stem)
                print("Entries cached!")
            else:
                print("Couldn't find any entries")

        except FileNotFoundError:
            print("[ERROR] Couldn't cache files")

    def on_entry_clicked(self, entry):
        self.current_entry = entry.text()
        self.load_entry()

    def save_entry(self):
       if self.current_entry:
            with open(f"journal/{self.current_entry}.md", "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())
            print("Auto save...")

    def load_entry(self):
        try:
            with open(f"journal/{self.current_entry}.md", "r", encoding="utf-8") as file:
                self.text_edit.setPlainText(file.read())
            self.current_entry_label.setText(self.current_entry)
        except FileNotFoundError:
            print("No files to load")

    def on_text_changed(self):
        self.save_timer.start(5000)

    def eventFilter(self, obj, event):
        if obj is self.text_edit.viewport() and self.sidebar_open and event.type() == QEvent.Type.MouseButtonPress:
            self.toggle_sidebar()

        return super().eventFilter(obj, event)

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
