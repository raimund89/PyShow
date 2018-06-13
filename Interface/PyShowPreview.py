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
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen
from PyQt5.QtCore import QRect, Qt, QPoint


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

    def refresh(self, data, cursor):
        """Called when an update of the GUI is necessary"""
        self._slide.refresh(data, cursor)


class PyShowSlide(QWidget):
    """The actual slide inside the preview widget"""

    def __init__(self, parent):
        super().__init__(parent)

        self._parent = parent

        self._size = (0, 0)

        self._cursor = None
        self._data = None

    def set_size(self, width, height):
        """Set the slide size in pixels"""
        self._size = (width, height)
        self._parent.resizeEvent()

    def size(self):
        """Returns the slide size in pixels"""
        return self._size

    def refresh(self, data, cursor):
        """Refresh the preview with new parsed data or cursor position"""
        self._data = data
        self._cursor = cursor
        self.update()

    def paintEvent(self, event):
        """Called when the slide preview needs to be updated"""

        print("Redrawing preview")

        painter = QPainter()
        painter.begin(self)

        # Define slide area
        rect = self.geometry()
        print(rect)
        scaled = rect.width()/self._size[0]
        print(scaled)

        # We know the cursor position and the parsed data. We want to know
        # which line corresponds to the cursor position, so we can find the
        # last newSlide-statement and prepare the preview from there.
        if self._data is not None and self._cursor is not None:
            data = self._data[self._cursor[0]]["contents"]
            i = 0
            while (data[self._cursor[1]-i]["name"] != "newSlide" and
                   self._cursor[1]-i > -1):
                i += 1

            if data[self._cursor[1]-i]["name"] != "newSlide":
                print("ERROR: no newSlide in block!")
                painter.end()
                return

            # Check if the template exists
            template = None
            for block in self._data:
                print(block["name"])
                print(block["args"])
                if (block["name"] == "beginTemplate" and
                    block["args"][0] == data[self._cursor[1]-i]["args"][0]):
                    template = block["contents"]
                    break

            if template is None:
                print("ERROR: no template with this name!")
                painter.end()
                return

            # Run through the template and fill a dict with all standard
            # objects. This list can be appended later by the script if
            # new objects are created on the fly
            objects = {}
            for setting in template:
                if setting["name"] == "setBackgroundColor":
                    objects["background_color"] = QColor(setting["args"][0])
                elif setting["name"] == "addTextBlock":
                    objects["text_" + setting["args"][0]] = {}
                    for entry in setting["args"][1:]:
                        if len(entry) == 2:
                            objects["text_" + setting["args"][0]][entry[0][0]] = entry[1]
                        else:
                            print("ERROR: value without a key!")

            print(objects)

            # The background
            if objects["background_color"]:
                color = objects["background_color"]
            else:
                color = QColor('#FFF')

            # Draw a rect for the background
            painter.fillRect(QRect(0,
                                   0,
                                   rect.width(),
                                   rect.height()),
                             color)

            painter.fillRect(QRect(100*scaled,
                                   100*scaled,
                                   1700*scaled,
                                   800*scaled),
                             QColor('#00F'))

            # Work through all the commands until the cursor
            for j in range(i):
                print(j+1)
                command = data[self._cursor[1]-i+j+1]

                if command["name"] == "setText":
                    # Search the object list for this text object
                    text = objects.get("text_" + command["args"][0])
                    if text is None:
                        print("ERROR: text object %s undefined" % (command["args"][0]))

                    font = QFont(text["fontname"], int(text["fontsize"])*scaled)
                    painter.setFont(font)
                    if text["color"]:
                        painter.setPen(QPen(QColor(text["color"])))
                    painter.drawText(QPoint(int(text["x"])*scaled, int(text["y"]))*scaled,
                                     command["args"][1])
                else:
                    print("WARNING: command '%s' unknown" % (command["name"]))

        # Finish drawing
        painter.end()
