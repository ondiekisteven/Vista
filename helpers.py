import json
from pathlib import Path
import sys

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont,
    QPainterPath,
    QTextOption,
    QFontMetrics
)
from PySide6.QtCore import Qt, QRectF
from bs4 import BeautifulSoup
import re


def insert_chorus_after_each_verse(lyrics: str) -> str:
    """
    Rearranges a hymn so the chorus appears after every verse.

    Supports markers such as:
      CHORUS:
      Chorus:
    """

    stanzas = [
        stanza.strip()
        for stanza in lyrics.strip().split("\n\n")
        if stanza.strip()
    ]

    chorus = None
    verses = []

    chorus_pattern = re.compile(
        r'^(CHORUS|Chorus)\s*:?',
        re.IGNORECASE
    )

    for stanza in stanzas:
        if chorus_pattern.match(stanza):
            chorus = stanza
        else:
            verses.append(stanza)

    if chorus is None:
        return lyrics

    result = []

    for i, verse in enumerate(verses):
        result.append(verse)

        # Don't append after the final verse
        # if i < len(verses) - 1:
        result.append(chorus)

    return "\n\n".join(result)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Convert <br> tags to newlines
    for br in soup.find_all("br"):
        br.replace_with("\n")

    # Get plain text
    text = soup.get_text()

    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.splitlines()]

    # Remove empty lines at the beginning/end while preserving internal ones
    return "\n".join(lines).strip()


def clean_song_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        songs = json.load(f)

    for song in songs:
        if "lyrics" in song:
            song["lyrics"] = insert_chorus_after_each_verse(song["lyrics"])

            if song['title'] in song['lyrics']: 
                print(f"cleaning {song['title']}")
                song['lyrics'] = song['lyrics'].replace(song['title'], '')

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    print(f"Cleaned {len(songs)} songs.")


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).parent / relative_path


class PresentationRenderer(QWidget):

    def __init__(self):
        super().__init__()

        self.text = ""

        self.font_family = "Arial"

        self.max_font_size = 120
        self.min_font_size = 12

        self.margin = 40

        self.outline_width = 5

        self.text_color = QColor("white")
        self.outline_color = QColor("black")

        self.shadow_enabled = True
        self.shadow_offset = (4, 4)
        self.shadow_color = QColor(0, 0, 0, 150)

    def set_text(self, text):
        self.text = text
        self.update()

    def resizeEvent(self, event):
        self.update()

    def paintEvent(self, event):

        if not self.text.strip():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        font = self.find_best_font()

        painter.setFont(font)

        rect = self.rect().adjusted(
            self.margin,
            self.margin,
            -self.margin,
            -self.margin
        )

        option = QTextOption()
        option.setWrapMode(QTextOption.WordWrap)
        option.setAlignment(Qt.AlignCenter)

        metrics = QFontMetrics(font)

        lines = self.wrap_text(metrics, rect.width())

        total_height = len(lines) * metrics.lineSpacing()

        start_y = rect.center().y() - total_height / 2 + metrics.ascent()

        y = start_y

        for line in lines:

            width = metrics.horizontalAdvance(line)

            x = rect.center().x() - width / 2

            path = QPainterPath()
            path.addText(x, y, font, line)

            if self.shadow_enabled:

                shadow = QPainterPath()
                shadow.addText(
                    x + self.shadow_offset[0],
                    y + self.shadow_offset[1],
                    font,
                    line
                )

                painter.fillPath(
                    shadow,
                    self.shadow_color
                )

            pen = QPen(self.outline_color)
            pen.setWidth(self.outline_width)

            painter.strokePath(path, pen)

            painter.fillPath(path, self.text_color)

            y += metrics.lineSpacing()

    def find_best_font(self):

        low = self.min_font_size
        high = self.max_font_size

        best = low

        while low <= high:

            mid = (low + high) // 2

            font = QFont(self.font_family, mid)
            font.setBold(True)

            if self.text_fits(font):
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        font = QFont(self.font_family, best)
        font.setBold(True)

        return font

    def text_fits(self, font):

        metrics = QFontMetrics(font)

        width = self.width() - self.margin * 2

        lines = self.wrap_text(metrics, width)

        height = len(lines) * metrics.lineSpacing()

        return height <= (self.height() - self.margin * 2)

    def wrap_text(self, metrics, max_width):

        words = self.text.split()

        if not words:
            return []

        lines = []

        current = ""

        for word in words:

            trial = word if current == "" else current + " " + word

            if metrics.horizontalAdvance(trial) <= max_width:

                current = trial

            else:

                if current:
                    lines.append(current)

                current = word

        if current:
            lines.append(current)

        return lines