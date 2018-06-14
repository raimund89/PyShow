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
import collections


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
        scale = rect.width()/self._size[0]

        # We know the cursor position and the parsed data. We want to know
        # which line corresponds to the cursor position, so we can find the
        # last newSlide-statement and prepare the preview from there.
        if self._data is not None and self._cursor is not None:
            data = self._data[self._cursor[0]]["contents"]

            # Try to find the last newSlide command
            i = 0
            while (data[self._cursor[1]-i]["name"] != "newSlide" and
                   self._cursor[1]-i > -1):
                i += 1

            # Try to find the next pause command
            j = 0
            while (data[self._cursor[1]+j]["name"] != "pause" and
                   self._cursor[1]+j < len(data)-1):
                j += 1

            # If there is a newSlide command, find the template. Otherwise
            # we can continue anyway, but there will be no loaded objects.
            # Same goes for an unfound template, it will just throw a lot of
            # errors down the line...
            template = None
            if data[self._cursor[1]-i]["name"] != "newSlide":
                print("WARNING: no newSlide in block!")
            else:
                # Check if the template exists
                for block in self._data:
                    if (block["name"] == "beginTemplate" and
                        block["args"][0] == data[self._cursor[1]-i]["args"][0]):
                        template = block["contents"]
                        break
                if template is None:
                    print("ERROR: template %s not found" % (data[self._cursor[1]-i]["args"][0]))
                    return

            # If there is a template, load the objects in a dict
            objects = {}

            if template:
                # Run through the template and fill a dict with all standard
                # objects. This list can be appended later by the script if
                # new objects are created on the fly
                for setting in template:
                    if setting["name"] == "setBackgroundColor":
                        objects["background_color"] = QColor(setting["args"][0])
                    else:
                        prefix = ''
                        if setting["name"] == "addTextBlock":
                            prefix = 'text_'
                        objects[prefix + setting["args"][0]] = argstodict(setting["args"][1:])

                print(objects)

            # Work through all the commands until the cursor, putting all
            # commands to execute in another dict, so changes in the same
            # object are overwritten and only the final form is shown
            drawingcommands = collections.OrderedDict()

            for k in range(i+j):
                command = data[self._cursor[1]-i+k+1]

                if command["name"] == "setText" or command["name"] == "addTextBlock":
                    # Search the object list for this text object
                    name = "text_" + command["args"][0]
                    text = objects.get(name)

                    # If the object exists and we're in addTextBlock: conflict
                    if text and command["name"] == "addTextBlock":
                        print("ERROR: redefinition of object %s" % (command["args"][0]))
                        continue
                    # If the object doesn't exist and we are trying to access
                    # it: conflict
                    elif text is None and command["name"] == "setText":
                        print("ERROR: text object %s undefined" % (command["args"][0]))
                        continue
                    # Else, if we are in addTextBlock, we can add it. No case
                    # for if we are in setText, because that's no problem.
                    elif command["name"] == "addTextBlock":
                        objects[name] = argstodict(command["args"][1:])
                        text = objects.get(name)

                    # If the object is not in the drawing list, add the
                    # template version to the drawing list first, so all
                    # settings are loaded
                    if not drawingcommands.get(name):
                        print('Not yet in the drawing list')
                        # Add the command to the drawing list
                        drawingcommands[name] = {}
                        obj = drawingcommands[name]

                        obj["type"] = "text"

                        changeText(obj, text, scale)

                    # Now change the settings according to this command
                    drawingcommands.move_to_end(name)

                    # Make all changes accessible through a dict structure
                    changes = argstodict(command["args"][1:])
                    print(changes)

                    # Now loop through the changes to make them
                    changeText(drawingcommands[name], changes, scale)

                elif command["name"] == "setBackgroundColor":
                    print(command["args"][0])
                    objects["background_color"] = QColor(command["args"][0])
                elif command["name"] == "pause":
                    pass
                else:
                    print("WARNING: command '%s' unknown" % (command["name"]))

            # First, treat the background separately, if set
            if objects.get("background_color"):
                color = objects["background_color"]
                painter.fillRect(QRect(0,
                                       0,
                                       rect.width(),
                                       rect.height()),
                                 color)

            # Now go through the drawing list, and execute
            for entry in drawingcommands:
                task = drawingcommands[entry]
                if task["type"] == "text":
                    painter.setFont(task["font"])
                    painter.setPen(QPen(QColor(task["color"])))
                    painter.drawText(QPoint(task["x"], task["y"]),task["text"])
        # Finish drawing
        painter.end()

def argstodict(args):
    obj = {}
    for entry in args:
        if len(entry) == 2:
            obj[entry[0][0]] = entry[1]
        else:
            print("ERROR: value without a key!")

    return obj

def changeText(entry, changes, scale):
    # Make the font object
    if entry.get("font"):
        font = entry["font"]
    else:
        font = QFont()

    if changes.get("fontname"):
        font.setFamily(changes["fontname"])

    if changes.get("fontsize"):
        font.setPointSizeF(changes["fontsize"]*scale)

    # Font decorations allowed:
    # i - Italic
    # b - Bold
    # u - Underline
    # f - Fixed pitch
    # k - Kerning
    # o - Overline
    # s - Strike out
    if changes.get("decoration"):
        if "i" in changes["decoration"]:
            font.setItalic(True)
        if "b" in changes["decoration"]:
            font.setBold(True)
        if "u" in changes["decoration"]:
            font.setUnderline(True)
        if "f" in changes["decoration"]:
            font.setFixedPitch(True)
        if "k" in changes["decoration"]:
            font.setKerning(True)
        if "o" in changes["decoration"]:
            font.setOverline(True)
        if "s" in changes["decoration"]:
            font.setStrikeOut(True)

    # Other properties
    # Capitalization
    # Hinting
    # Letter Spacing
    # Stretch
    # Style, Stylehint, Stylename, Stylestrategy
    # Word spacing
    # Weight

    entry["font"] = font

    # Set the text color
    # TODO: the pen pattern, thickness, shadow, etc.
    entry["color"] = (changes["color"] if changes.get("color") else (entry["color"] if "color" in entry else "#000"))

    entry["x"] = (changes["x"]*scale if "x" in changes else (entry["x"] if "x" in entry else 0.0))
    entry["y"] = (changes["y"]*scale if "y" in changes else (entry["y"] if "y" in entry else 0.0))

    entry["text"] = changes["text"] if "text" in changes else (entry["text"] if "text" in entry else "")
