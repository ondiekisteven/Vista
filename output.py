from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter

from app_settings import load_settings
from helpers import PresentationRenderer, resource_path


class OutputWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        self.setWindowTitle("Presentation Output")
        self.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))

        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = PresentationRenderer()

        # self.label.setAlignment(Qt.AlignCenter)

        # self.label.setWordWrap(True)

        self.label.setStyleSheet("""
            color:white;
            background:transparent;
        """)

        layout.addWidget(self.label)
        self.apply_settings(self.settings)

    def apply_settings(self, settings):
        self.settings = settings

        self.resize(
            settings["output_width"],
            settings["output_height"]
        )

        self.label.min_font_size = settings["min_font_size"]
        self.label.max_font_size = settings["max_font_size"]

        self.setStyleSheet("background: transparent;")

        self.label.update()
        self.update()

    def paintEvent(self, event):
        if self.settings["transparent_output"]:
            return

        painter = QPainter(self)
        painter.fillRect(
            self.rect(),
            QColor(self.settings["background_color"])
        )

    def update_text(self, text):
        self.label.set_text(text)
