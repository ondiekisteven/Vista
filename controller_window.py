import json
import shutil

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
)

from app_settings import APP_NAME, DATA_DIR, load_settings, save_settings
from helpers import resource_path


CONTROLLER_STYLE = """
QWidget {
    background: #0f1115;
    color: #eef2f7;
    font-family: Segoe UI;
    font-size: 13px;
}

QTabWidget::pane {
    border: 0;
    margin-top: 8px;
}

QTabBar::tab {
    background: #171b22;
    color: #aeb7c4;
    border: 1px solid #262d38;
    border-bottom: 0;
    padding: 10px 18px;
    margin-right: 6px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
}

QTabBar::tab:selected {
    background: #202631;
    color: #ffffff;
}

QTabBar::tab:hover {
    color: #ffffff;
    background: #1c222c;
}

QWidget#Panel {
    background: #171b22;
    border: 1px solid #262d38;
    border-radius: 8px;
}

QWidget#SettingsPanel {
    background: #171b22;
    border: 1px solid #262d38;
    border-radius: 8px;
}

QLabel#SectionTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}

QLabel#MutedText {
    color: #8f9aaa;
    font-size: 12px;
}

QLineEdit,
QSpinBox {
    background: #10141b;
    color: #f7f9fc;
    border: 1px solid #2b3442;
    border-radius: 6px;
    padding: 8px 10px;
    selection-background-color: #2f6fed;
}

QLineEdit:focus,
QSpinBox:focus {
    border-color: #4f8cff;
}

QSpinBox::up-button,
QSpinBox::down-button {
    width: 20px;
    border: 0;
    background: #202631;
}

QListWidget {
    background: #10141b;
    border: 1px solid #2b3442;
    border-radius: 8px;
    outline: 0;
    padding: 6px;
}

QListWidget::item {
    color: #dfe6ef;
    border-radius: 6px;
    padding: 9px 10px;
    margin: 2px;
}

QListWidget::item:hover {
    background: #1d2531;
}

QListWidget::item:selected {
    background: #2f6fed;
    color: #ffffff;
}

QPushButton {
    background: #2f6fed;
    color: #ffffff;
    border: 0;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: #3f7df1;
}

QPushButton:disabled {
    background: #242a34;
    color: #6f7886;
}

QCheckBox {
    spacing: 8px;
    color: #dfe6ef;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #3a4554;
    background: #10141b;
}

QCheckBox::indicator:checked {
    background: #2f6fed;
    border-color: #2f6fed;
}

QSplitter::handle {
    background: #0f1115;
}

QSplitter::handle:horizontal {
    width: 10px;
}
"""


class ControllerWindow(QWidget):

    def __init__(self, output):
        super().__init__()

        self.output = output
        self.settings = load_settings()

        self.songs = []
        self.filtered_songs = []
        self.current_slides = []

        self.setWindowTitle(APP_NAME)
        
        self.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))

        self.resize(1100, 700)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(CONTROLLER_STYLE)

        self.announcementMode = False
        self.currentSlideOnOutputIndex = None

        self.build_ui()

        self.load_library()

    ####################################################################
    # UI
    ####################################################################

    def build_ui(self):

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        root.addWidget(tabs)

        splitter = QSplitter(Qt.Horizontal)

        ###########################################################
        # LEFT SIDE (Song Library)
        ###########################################################

        left = self.build_song_left_pane()
        ###########################################################
        # RIGHT SIDE (Slides)
        ###########################################################

        right = QWidget()
        right.setObjectName("Panel")
        rightLayout = QVBoxLayout(right)
        rightLayout.setContentsMargins(18, 18, 18, 18)
        rightLayout.setSpacing(12)

        self.songTitle = QLabel("No Song Selected")
        self.songTitle.setObjectName("SectionTitle")

        self.slideCount = QLabel("0 slides")
        self.slideCount.setObjectName("MutedText")

        rightHeader = QHBoxLayout()
        rightHeader.addWidget(self.songTitle)
        rightHeader.addStretch()
        rightHeader.addWidget(self.slideCount)

        rightLayout.addLayout(rightHeader)

        self.slideList = QListWidget()
        self.slideList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.slideList.currentRowChanged.connect(
            self.slide_selected
        )

        rightLayout.addWidget(self.slideList)

        ###########################################################

        splitter.addWidget(left)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        tabs.addTab(splitter, "Songs")
        tabs.addTab(self.build_announcements_page(), "Announcements")
        tabs.addTab(self.build_settings_page(), "Settings")

    def build_song_left_pane(self):
        
        announcements = self.build_announcements_pane()
        
        left = QWidget()
        left.setObjectName("Panel")
        leftLayout = QVBoxLayout(left)
        leftLayout.setContentsMargins(18, 18, 18, 18)
        leftLayout.setSpacing(12)

        leftLayout.addWidget(announcements)

        title = QLabel("Songs")
        title.setObjectName("SectionTitle")

        self.songCount = QLabel("0 songs")
        self.songCount.setObjectName("MutedText")

        leftHeader = QHBoxLayout()
        leftHeader.addWidget(title)
        leftHeader.addStretch()
        leftHeader.addWidget(self.songCount)

        leftLayout.addLayout(leftHeader)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search songs...")
        self.search.textChanged.connect(self.filter_songs)

        leftLayout.addWidget(self.search)

        self.songList = QListWidget()
        self.songList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.songList.currentRowChanged.connect(
            self.song_selected
        )

        leftLayout.addWidget(self.songList)

        return left

    def build_announcements_pane(self):
        
        left = QWidget()
        left.setObjectName("AnnouncementsPanel")
        leftLayout = QVBoxLayout(left)
        leftLayout.setSpacing(12)

        title = QLabel("Announcements")
        title.setObjectName("SectionTitle")

        leftHeader = QHBoxLayout()
        leftHeader.addWidget(title)

        leftLayout.addLayout(leftHeader)

        self.announcementInput = QLineEdit()
        self.announcementInput.setPlaceholderText("Enter your announcement")


        # buttons layout
        buttonsLayout = QHBoxLayout(left)
        submitButton = QPushButton("Set Announcement")
        submitButton.clicked.connect(self.handle_new_announcement)

        addAnnouncementButton = QPushButton("Add Announcement")
        addAnnouncementButton.clicked.connect(self.handle_add_announcement)

        buttonsLayout.addWidget(submitButton)
        buttonsLayout.addWidget(addAnnouncementButton)

        leftLayout.addWidget(self.announcementInput)
        leftLayout.addLayout(buttonsLayout)


        return left


    def build_announcements_page(self):
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        panel = QWidget()
        panel.setObjectName("AnnouncementsPanel")
        panelLayout = QVBoxLayout(panel)
        panelLayout.setContentsMargins(22, 22, 22, 22)
        panelLayout.setSpacing(18)

        #title
        title = QLabel("Announcements")
        title.setObjectName("AnnouncementsTitle")

        description = QLabel("Add an announcement to the main output window")

        headerLayout = QVBoxLayout()
        headerLayout.addWidget(title)
        headerLayout.addWidget(description)

        panelLayout.addLayout(headerLayout)

        layout.addWidget(panel)

        return page

    def build_settings_page(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        panel = QWidget()
        panel.setObjectName("SettingsPanel")
        panelLayout = QVBoxLayout(panel)
        panelLayout.setContentsMargins(22, 22, 22, 22)
        panelLayout.setSpacing(18)

        title = QLabel("Output Settings")
        title.setObjectName("SectionTitle")
        panelLayout.addWidget(title)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)

        self.outputWidth = QSpinBox()
        self.outputWidth.setRange(200, 10000)
        self.outputWidth.setSuffix(" px")
        self.outputWidth.setValue(self.settings["output_width"])
        self.outputWidth.valueChanged.connect(self.settings_changed)
        form.addRow("Output width", self.outputWidth)

        self.outputHeight = QSpinBox()
        self.outputHeight.setRange(100, 10000)
        self.outputHeight.setSuffix(" px")
        self.outputHeight.setValue(self.settings["output_height"])
        self.outputHeight.valueChanged.connect(self.settings_changed)
        form.addRow("Output height", self.outputHeight)

        self.minFontSize = QSpinBox()
        self.minFontSize.setRange(6, 300)
        self.minFontSize.setSuffix(" pt")
        self.minFontSize.setValue(self.settings["min_font_size"])
        self.minFontSize.valueChanged.connect(self.settings_changed)
        form.addRow("Minimum font size", self.minFontSize)

        self.maxFontSize = QSpinBox()
        self.maxFontSize.setRange(6, 300)
        self.maxFontSize.setSuffix(" pt")
        self.maxFontSize.setValue(self.settings["max_font_size"])
        self.maxFontSize.valueChanged.connect(self.settings_changed)
        form.addRow("Maximum font size", self.maxFontSize)

        self.transparentOutput = QCheckBox("Transparent output window")
        self.transparentOutput.setChecked(self.settings["transparent_output"])
        self.transparentOutput.toggled.connect(self.settings_changed)
        self.transparentOutput.toggled.connect(self.update_background_controls)
        form.addRow("Background mode", self.transparentOutput)

        colorRow = QHBoxLayout()
        self.backgroundColorButton = QPushButton("Choose color")
        self.backgroundColorButton.clicked.connect(self.choose_background_color)

        self.backgroundColorPreview = QLabel()
        self.backgroundColorPreview.setFixedSize(52, 24)

        colorRow.addWidget(self.backgroundColorButton)
        colorRow.addWidget(self.backgroundColorPreview)
        colorRow.addStretch()
        form.addRow("Background color", colorRow)

        panelLayout.addLayout(form)
        panelLayout.addStretch()

        layout.addWidget(panel)
        layout.addStretch()

        self.update_background_controls()

        return page

    ####################################################################
    # Library
    ####################################################################

    def load_library(self):

        lyrics_file = DATA_DIR / "lyrics.json"

        # First run
        if not lyrics_file.exists():
            shutil.copy(
                resource_path("lyrics.json"),
                lyrics_file
            )

        with open(lyrics_file, "r", encoding="utf8") as f:
            self.songs = json.load(f)

        self.filtered_songs = self.songs.copy()

        self.populate_song_list()

    def populate_song_list(self):

        self.songList.clear()

        for song in self.filtered_songs:

            self.songList.addItem(song["title"])

        self.songCount.setText(f"{len(self.filtered_songs)} songs")

        # if self.songList.count():
        #     self.songList.setCurrentRow(0)

    ####################################################################
    # Search
    ####################################################################

    def filter_songs(self, text):

        text = text.lower()

        self.filtered_songs = [
            song
            for song in self.songs
            if text in song["title"].lower() or text in song["lyrics"].lower()
        ]

        self.populate_song_list()

    ####################################################################
    # Announcement
    ####################################################################

    def handle_new_announcement(self):

        text = self.announcementInput.text()

        self.current_slides.clear()
        self.slideList.clear()
        self.songTitle.setText("")

        self.current_slides.append(text)
        self.populate_slide_list()

        self.announcementMode = True


    def handle_add_announcement(self):

        text = self.announcementInput.text()

        self.songTitle.setText("")

        if self.announcementMode:
            currentSlideText = self.current_slides[self.currentSlideOnOutputIndex]
            currentSlideText += f"\n{text}"
            self.current_slides[self.currentSlideOnOutputIndex] = currentSlideText
            self.populate_slide_list()
            self.announcementMode = True
        else:
            self.handle_new_announcement()


    ####################################################################
    # Song Selection
    ####################################################################

    def song_selected(self, row):

        if row < 0:
            return

        song = self.filtered_songs[row]

        self.songTitle.setText(song["title"])

        self.current_slides = [
            slide.strip()
            for slide in song["lyrics"].split("\n\n")
            if slide.strip()
        ]
        self.current_slides.insert(0, song["title"])

        self.populate_slide_list()
        self.announcementMode = False

    def populate_slide_list(self):

        self.slideList.clear()

        font = QFont("Arial", 11)

        for slide in self.current_slides:

            item = QListWidgetItem(
                f"{slide}\n\n"
            )

            item.setData(Qt.UserRole, slide)

            item.setFont(font)

            size = item.sizeHint()
            size.setHeight(90)

            item.setSizeHint(size)

            self.slideList.addItem(item)

        if self.slideList.count():
            self.slideList.setCurrentRow(0)

        self.slideCount.setText(f"{self.slideList.count()} slides")

    ####################################################################
    # Slide Selection
    ####################################################################

    def slide_selected(self, row):

        if row < 0:
            return

        slide = self.current_slides[row]
        self.currentSlideOnOutputIndex = row
        # print(f"SLIDE: {slide}, type: {type(slide)}")

        self.output.update_text(slide)

    ####################################################################
    # Settings
    ####################################################################

    def settings_changed(self):

        if self.minFontSize.value() > self.maxFontSize.value():
            self.maxFontSize.setValue(self.minFontSize.value())

        self.settings.update({
            "output_width": self.outputWidth.value(),
            "output_height": self.outputHeight.value(),
            "min_font_size": self.minFontSize.value(),
            "max_font_size": self.maxFontSize.value(),
            "transparent_output": self.transparentOutput.isChecked(),
        })

        self.settings = save_settings(self.settings)
        self.output.apply_settings(self.settings)
        self.update_background_controls()

    def choose_background_color(self):

        color = QColorDialog.getColor(
            QColor(self.settings["background_color"]),
            self,
            "Choose Output Background"
        )

        if not color.isValid():
            return

        self.settings["background_color"] = color.name()
        self.settings = save_settings(self.settings)
        self.output.apply_settings(self.settings)
        self.update_background_controls()

    def update_background_controls(self):

        color = self.settings["background_color"]
        is_transparent = self.transparentOutput.isChecked()

        self.backgroundColorButton.setEnabled(not is_transparent)
        self.backgroundColorPreview.setEnabled(not is_transparent)
        self.backgroundColorPreview.setStyleSheet(
            f"background-color: {color}; border: 1px solid #888;"
        )


    def keyPressEvent(self, event):
        # all keyboard shortcuts

        if self.slideList.hasFocus():

            row = self.slideList.currentRow()

            if event.key() in (
                Qt.Key_Down,
                Qt.Key_PageDown,
                Qt.Key_Space,
            ):

                if row < self.slideList.count() - 1:
                    self.slideList.setCurrentRow(row + 1)

                return

            if event.key() in (
                Qt.Key_Up,
                Qt.Key_PageUp,
                Qt.Key_Backspace,
            ):

                if row > 0:
                    self.slideList.setCurrentRow(row - 1)

                return

            if event.key() == Qt.Key_Home:
                self.slideList.setCurrentRow(0)
                return

            if event.key() == Qt.Key_End:
                self.slideList.setCurrentRow(
                    self.slideList.count() - 1
                )
                return

        super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent):
        try:
            if self.output:
                self.output.close()
        finally:
            event.accept()
