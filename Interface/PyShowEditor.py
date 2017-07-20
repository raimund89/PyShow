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
from PyQt5.QtCore import QRect, Qt, QSize, QRegularExpression
from PyQt5.QtGui import (QPainter, QColor, QTextFormat, QTextCursor,
                         QTextCharFormat, QFont, QSyntaxHighlighter)


class PyShowEditor(QTextEdit):
    """The main editor for the PyShow software"""

    def __init__(self):
        super().__init__()
        self.line_number_area = PyShowEditorLineNumberArea(self)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self.setLineWrapMode(QTextEdit.NoWrap)

        self.document().blockCountChanged.connect(self.updatelinenumberwidth)
        self.verticalScrollBar().valueChanged.connect(self.updatelinenumbers)
        self.textChanged.connect(self.updatelinenumbers)
        self.cursorPositionChanged.connect(self.updatelinenumbers)

        self.updatelinenumberwidth()

        self.setStyleSheet("PyShowEditor {"
                           "border: none;"
                           "font-family: Courier New;"
                           "font-size: 9pt;"
                           "}"
                           "QScrollBar:horizontal{"
                               "background: #DDD;"
                               "border: none;"
                               "padding: 0px 18px 0px 18px;"
                               "margin-right:2px;"
                           "}"
                           "QScrollBar:handle:horizontal {"
                               "background: white;"
                               "border: 1px solid #AAA;"
                               "min-width: 16px;"
                           "}"
                           "QScrollBar:add-line:horizontal {"
                               "background: white;"
                               "border: 1px solid #AAA;"
                               "subcontrol-position: right;"
                               "subcontrol-origin: padding;"
                               "width: 16px;"
                           "}"
                           "QScrollBar:sub-line:horizontal {"
                               "background: white;"
                               "border: 1px solid #AAA;"
                               "subcontrol-position: left;"
                               "subcontrol-origin: padding;"
                               "width: 16px;"
                           "}")

        # Now enable the syntax highlighting
        self._highlighter = PyShowEditorHighlighter(self)

    def linenumber_width(self):
        """Calculate the width of the line number area"""
        digits = 1
        count = max(1, self.document().blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 25 + self.fontMetrics().width('9') * digits
        return space

    def updatelinenumberwidth(self):
        """Update the viewport from the line number area width"""
        self.setViewportMargins(self.linenumber_width(), 0, 0, 0)

    def updatelinenumbers(self):
        """Update the line numbers after any change in the viewport"""
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition())

        rect = self.contentsRect()
        self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        self.updatelinenumberwidth()

        ychange = self.verticalScrollBar().sliderPosition()
        if ychange:
            self.line_number_area.scroll(0, ychange)

        first_block_id = self.getFirstVisibleBlockId()
        if first_block_id == 0 or self.textCursor().block().blockNumber() == first_block_id:
            self.verticalScrollBar().setSliderPosition(ychange - self.document().documentMargin())

    def getFirstVisibleBlockId(self):
        """Get the ID of the first visible text block in the editor"""
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
        """Actually paint the numbers in the line number area"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block_number = self.getFirstVisibleBlockId()
        block = self.document().findBlockByNumber(block_number)
        if block_number > 0:
            prev_block = self.document().findBlockByNumber(block_number - 1)
            translate_y = -self.verticalScrollBar().sliderPosition()
        else:
            prev_block = block
            translate_y = 0

        top = self.viewport().geometry().top()

        if block_number == 0:
            additional_margin = self.document().documentMargin() - self.verticalScrollBar().sliderPosition()
        else:
            additional_margin = self.document().documentLayout().blockBoundingRect(prev_block).translated(0, translate_y).intersected(self.viewport().geometry().height())

        top += additional_margin

        bottom = top + self.document().documentLayout().blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                if self.textCursor().blockNumber() == block_number:
                    painter.setPen(QColor("#090"))
                else:
                    painter.setPen(QColor("#333"))

                painter.drawText(-5, top, self.line_number_area.width(), self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.document().documentLayout().blockBoundingRect(block).height()
            block_number += 1

        self.highlight_current_line()

    def resizeEvent(self, event):
        """React to a resize event"""
        super().resizeEvent(event)

        contents = self.contentsRect()
        self.line_number_area.setGeometry(QRect(contents.left(), contents.top(), self.linenumber_width(), contents.height()))

    def highlight_current_line(self):
        """Highlight the entire active line in the editor area"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#FFFF00")

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            self.setExtraSelections(extra_selections)


class PyShowEditorLineNumberArea(QWidget):
    """The line number area in the main PyShow editor"""

    def __init__(self, editor):
        super().__init__(editor)

        self._editor = editor

    def sizeHint(self):
        """Return the size of the line number area"""
        return QSize(self._editor.linenumber_width(), 0)

    def paintEvent(self, event):
        """A paint request is triggered, so pass it on"""
        self._editor.paintLineNumbers(event)


class PyShowEditorHighlighter(QSyntaxHighlighter):
    """The highlighter class providing the syntax highlighting"""

    # List of keywords
    keywords = ['text', 'number', 'function']
    operators = ['+', '-', '*', '/']
    comments = ['%', '#']

    def __init__(self, editor):
        super().__init__(editor)
        self.parent = editor
        self.highlightingRules = []

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.darkBlue)
        keyword.setFontWeight(QFont.Bold)

        for word in self.keywords:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        # Strings
        string = QTextCharFormat()
        string.setForeground(Qt.darkMagenta)
        string.setFontItalic(True)
        pattern = QRegularExpression("\".*\"")
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)
        pattern = QRegularExpression("\'.*\'")
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)

        # Comments
        comment = QTextCharFormat()
        comment.setForeground(Qt.darkGray)
        comment.setFontItalic(True)
        pattern = QRegularExpression("#[^\n]*")
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            matchIterator = rule.pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(match.capturedStart(),
                               match.capturedLength(),
                               rule.format)


class HighlightingRule():
    """A simple structure that contains the pattern and format for a rule"""

    def __init__(self, pattern, formatting):
        self.pattern = pattern
        self.format = formatting
