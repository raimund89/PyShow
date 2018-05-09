"""
    PyShow - a slide show IDE and scripting language
    Copyright (C) 2017  Raimond Frentrop

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QLinearGradient
from PyQt5.QtCore import QRect, Qt


class PyShowPreview(QWidget):
    """The preview area in the PyShow window"""

    def __init__(self, parent):
        super().__init__(parent)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self._splitter = parent
        self._slide = PyShowSlide(self)

    def initialize(self):
        """Initialize the preview size (and splitter width) and slide size"""
        rect = self._splitter.geometry()
        self.setGeometry(0, 0, rect.width()*0.75, rect.height())

        # Set the slide size
        self._slide.set_size(1920, 1080)

    def get_slide_rect(self):
        """Returns the geometry of the slide in the preview"""

        # Define slide area
        rect = self.geometry()
        x = 50
        width = rect.width()-100
        height = width*(self._slide.size()[1]/self._slide.size()[0])
        y = rect.height()/2 - height/2

        if y < 50:
            y = 50
            height = rect.height()-100
            width = height*(self._slide.size()[0]/self._slide.size()[1])
            x = rect.width()/2 - width/2

        return QRect(x, y, width, height)

    def resizeEvent(self, event=None):
        """Called when the preview needs to be resized"""

        rect = self.get_slide_rect()
        self._slide.setGeometry(rect.x(),
                                rect.y(),
                                rect.width(),
                                rect.height())

    def paintEvent(self, event):
        """Called when the preview needs to be updated"""

        painter = QPainter()
        painter.begin(self)

        # Define slide area
        rect = self.geometry()
        sliderect = self.get_slide_rect()

        # Draw a rect for the background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, QColor("#FAFAFA"))
        painter.fillRect(QRect(0, 0, rect.width(), rect.height()), gradient)

        # Now draw a border around the slide
        painter.setPen(Qt.lightGray)
        painter.drawRect(QRect(sliderect.x()-1,
                               sliderect.y()-1,
                               sliderect.width()+1,
                               sliderect.height()+1))

        # Finish drawing
        painter.end()


class PyShowSlide(QWidget):
    """The actual slide inside the preview widget"""

    def __init__(self, parent):
        super().__init__(parent)

        self._parent = parent

        self._size = (0, 0)

    def set_size(self, width, height):
        """Set the slide size in pixels"""
        self._size = (width, height)
        self._parent.resizeEvent()

    def size(self):
        """Returns the slide size in pixels"""
        return self._size

    def paintEvent(self, event):
        """Called when the slide preview needs to be updated"""

        print("Redrawing preview")

        painter = QPainter()
        painter.begin(self)

        # Define slide area
        rect = self.geometry()

        # Draw a rect for the background
        painter.fillRect(QRect(0,
                               0,
                               rect.width(),
                               rect.height()),
                         QColor("#FFF"))

        # Finish drawing
        painter.end()
