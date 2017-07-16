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

from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QTextCursor


class PyShowEditor(QTextEdit):

    def __init__(self):
        super().__init__()
        self.lineNumberArea = PyShowEditorLineNumberArea(self)

        self.document().blockCountChanged.connect(self.updatelinenumberWidth)
        self.verticalScrollBar().valueChanged.connect(self.updatelinenumbers)
        self.textChanged.connect(self.updatelinenumbers)
        self.cursorPositionChanged.connect(self.updatelinenumbers)
        
        self.updatelinenumberWidth()

        self.setStyleSheet("border: none;"
                           "font-family: Courier New;"
                           "font-size: 9pt;")

    def linenumberWidth(self):
        digits = 1
        count = max(1, self.document().blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 25 + self.fontMetrics().width('9') * digits
        return space

    def updatelinenumberWidth(self):
        self.setViewportMargins(self.linenumberWidth(), 0, 0, 0)

    def updatelinenumbers(self):
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition())

        rect = self.contentsRect()
        self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        self.updatelinenumberWidth()

        ychange = self.verticalScrollBar().sliderPosition()
        if ychange:
            self.lineNumberArea.scroll(0, ychange)
        
        first_block_id = self.getFirstVisibleBlockId()
        if first_block_id == 0 or self.textCursor().block().blockNumber() == first_block_id:
            self.verticalScrollBar().setSliderPosition(ychange - self.document().documentMargin())

    def getFirstVisibleBlockId(self):
        curs = QTextCursor(self.document())
        curs.movePosition(QTextCursor.Start)

        for i in range(0, self.document().blockCount()):
            block = curs.block()

            r1 = self.viewport().geometry()
            r2 = self.document().documentLayout().blockBoundingRect(block).translated(self.viewport().geometry().x(), self.viewport().geometry().y() - self.verticalScrollBar().sliderPosition()).toRect()

            if r1.contains(r2, True):
                return i

            curs.movePosition(QTextCursor.NextBlock)

        return 0

    def paintLineNumbers(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        blockNumber = self.getFirstVisibleBlockId()
        block = self.document().findBlockByNumber(blockNumber)
        if blockNumber > 0:
            prev_block = self.document().findBlockByNumber(blockNumber - 1)
            translate_y = -self.verticalScrollBar().sliderPosition()
        else:
            prev_block = block
            translate_y = 0

        top = self.viewport().geometry().top()

        if blockNumber == 0:
            additional_margin = self.document().documentMargin() - self.verticalScrollBar().sliderPosition()
        else:
            additional_margin = self.document().documentLayout().blockBoundingRect(prev_block).translated(0, translate_y).intersected(this().viewport().geometry().height())

        top += additional_margin

        bottom = top + self.document().documentLayout().blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)

                if self.textCursor().blockNumber() == blockNumber:
                    painter.setPen(QColor("#090"))
                else:
                    painter.setPen(QColor("#333"))

                painter.drawText(-5, top, self.lineNumberArea.width(), self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.document().documentLayout().blockBoundingRect(block).height()
            blockNumber += 1

        self.highlightCurrentLine()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        contents = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(contents.left(), contents.top(), self.linenumberWidth(), contents.height()))

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#FFFF00")

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            self.setExtraSelections(extraSelections)


class PyShowEditorLineNumberArea(QWidget):

    def __init__(self, editor):
        super().__init__(editor)

        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.linenumberWidth(), 0)

    def paintEvent(self, event):
        self._editor.paintLineNumbers(event)
