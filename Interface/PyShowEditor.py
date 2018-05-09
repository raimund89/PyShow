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

import math
from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QTextCursor, QFont
from Core.PyShowLanguage import PyShowParser, PyShowEditorHighlighter

# TODO: Further styling of both scroll bars
# TODO: move out all the stylesheets to an external stylesheet
# TODO: try to simplify the line number code even more


class PyShowEditor(QTextEdit):
    """The main editor for the PyShow software"""

    def __init__(self):
        super().__init__()

        # Connect some signals of various subwidgets to this class
        self.verticalScrollBar().valueChanged.connect(self.updatelinenumbers)
        self.textChanged.connect(self.updatelinenumbers)
        self.cursorPositionChanged.connect(self.updatelinenumbers)
        self.cursorPositionChanged.connect(self.updatepreview)

        self.setStyleSheet("PyShowEditor {"
                           "border: none;"
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

        # Require a minimal width and height to function
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        # Set tab stop width to 4 characters
        fnt = self.font()
        fnt.setStyleHint(QFont.Monospace)
        fnt.setFamily("Courier New")
        fnt.setPointSize(9)
        self.setFont(fnt)
        self.setTabStopWidth(4*self.fontMetrics().width(' '))

        # No wrapping, just extend and show a scrollbar
        self.setLineWrapMode(QTextEdit.NoWrap)

        # Initialize the linenumber area
        self.line_number_area = PyShowEditorLineNumberArea(self)
        self.update_viewport()

        # Now enable the syntax highlighting
        self._highlighter = PyShowEditorHighlighter(self)

        # And enable the parser
        self._parser = PyShowParser(self)

    def update_viewport(self):
        """Update the viewport from the line number area width"""
        self.setViewportMargins(self.line_number_area.get_width(), 0, 0, 0)

    def updatelinenumbers(self):
        """Update the line numbers after any change in the viewport"""

        # This is a necessary step to avoid unexpected values for
        # the scrollbar position
        self.verticalScrollBar().\
            setSliderPosition(self.verticalScrollBar().sliderPosition())

        # Update the viewport, then request a paint update
        # of the line number area
        self.update_viewport()
        self.line_number_area.update(0,
                                     0,
                                     self.line_number_area.width(),
                                     self.height())

    def updatepreview(self):
        """Updating the preview depending on the cursor position"""
        pass

    def get_first_block_id(self):
        """Get the ID of the first visible text block in the editor"""

        # Ask for a cursor and set it to the beginning of the document
        curs = QTextCursor(self.document())
        curs.movePosition(QTextCursor.Start)

        # The geometry of the QTextEdit
        rect1 = self.viewport().geometry()
        translate_y = self.verticalScrollBar().sliderPosition()

        # Loop through the blocks (e.g. lines), and see if it is
        # visible in the viewport (could even be just a pixel)
        for i in range(0, self.document().blockCount()):
            block = curs.block()

            # Translate the block's bounding rect with the position
            # of the vertical scrollbar
            rect2 = self.document().documentLayout().blockBoundingRect(block).\
                translated(rect1.x(), rect1.y() - translate_y).toRect()

            # If the block is indeed completely visible in the viewport,
            # this is the first visible block, so return the index
            if rect1.intersects(rect2):
                return i

            # Otherwise move to the next block and repeat
            curs.movePosition(QTextCursor.NextBlock)

        return 0

    def paint_line_numbers(self, event):
        """Actually paint the numbers in the line number area"""

        # Get the painter instance for the line number area,
        # fill the line number area background and set it's font
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)
        painter.setFont(self.font())

        # Often used variables here to make the script more readable
        layout = self.document().documentLayout()
        top = self.viewport().geometry().top()
        translate_y = self.verticalScrollBar().sliderPosition()

        # Find the first visible block
        block_number = self.get_first_block_id()
        block = self.document().findBlockByNumber(block_number)

        # Determine the additional margin caused by the document margins
        # and any scrolling down. The scrolling needs to be taken into
        # account in all cases
        additional_margin = -translate_y
        if block_number > 0:
            # If block_number>0 we must have scrolled down, so
            # compensate for that
            rect = layout.blockBoundingRect(block.previous())
            additional_margin += rect.y() + rect.height()
        else:
            additional_margin += self.document().documentMargin()

        # Correct top and set bottom value
        top += additional_margin
        bottom = top + layout.blockBoundingRect(block).height()

        # For every block that is valid and has a top inside the viewport
        while block.isValid() and top <= event.rect().bottom():
            # If it is a visible block and it's bottom is
            # also inside the viewport
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                # The current line has a different color
                if self.textCursor().blockNumber() == block_number:
                    painter.setPen(QColor("#090"))
                else:
                    painter.setPen(QColor("#333"))

                painter.drawText(-5,
                                 top+1,
                                 self.line_number_area.width(),
                                 self.fontMetrics().height(),
                                 Qt.AlignRight,
                                 number)

            # Move to the next block
            block = block.next()
            top = bottom
            bottom = top + layout.blockBoundingRect(block).height()
            block_number += 1

        self.highlight_current_line()

    def resizeEvent(self, event):
        """React to a resize event"""

        # The QTextEdit should act on the event like it normally would
        super().resizeEvent(event)

        # The line number area has to be resized as well
        self.line_number_area.setGeometry(0,
                                          0,
                                          self.line_number_area.get_width(),
                                          self.height())

    def highlight_current_line(self):
        """Highlight the entire active line in the editor area"""

        # Make an extraSelection, set it's formatting properties,
        # and apply it to the entire line under the cursor
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#FFFF60"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()  # No multi-line selections
        self.setExtraSelections([selection])

    def wheelEvent(self, event):
        """Increase/decrease editor font size"""
        if event.modifiers() & Qt.ControlModifier:
            fnt = self.font()
            fntsize = fnt.pointSize()

            delta = event.angleDelta().y()
            if delta > 0:
                if fntsize == 72:  # Larger than this doesn't make any sense
                    return
                fnt.setPointSize(fntsize+1)
            else:
                if fntsize == 1:  # Point size of 0 is not supported
                    return
                fnt.setPointSize(fntsize-1)

            self.setFont(fnt)
            self.setTabStopWidth(4*self.fontMetrics().width(' '))
            self.updatelinenumbers()
        else:
            super().wheelEvent(event)

    def insertFromMimeData(self, source):
        """When the user pastes something from the clipboard, convert
           to plain text before doing that"""
        self.insertPlainText(source.text())

    def keyPressEvent(self, event):
        """If the user uses TAB, indent lines instead of replace by a TAB"""

        if event.key() != Qt.Key_Tab and event.key() != Qt.Key_Backtab:
            super().keyPressEvent(event)
            return

        # Get the current cursor
        cursor = self.textCursor()

        # If nothing is selected, just add or remove a TAB at the beginning
        # of the line
        if not cursor.hasSelection():
            cursor.movePosition(QTextCursor.StartOfBlock,
                                QTextCursor.MoveAnchor)

            if event.key() == Qt.Key_Tab:
                cursor.insertText("\t")
            elif event.key() == Qt.Key_Backtab:
                # Select first character to see if it is a TAB
                cursor.movePosition(QTextCursor.NextCharacter,
                                    QTextCursor.KeepAnchor)

                if cursor.selectedText() == "\t":
                    cursor.removeSelectedText()
            return

        # We have a selection, so first get the entire selection
        start_pos = cursor.anchor()
        end_pos = cursor.position()

        # If user selected from bottom to top, switch the two,
        # we work from bottom to top
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        cursor.setPosition(end_pos, QTextCursor.MoveAnchor)
        end_block = cursor.block().blockNumber()

        cursor.setPosition(start_pos, QTextCursor.MoveAnchor)
        start_block = cursor.block().blockNumber()

        # Let all the changes be in one editing block, so one single
        # 'Undo'/'Redo' action will change all of them at the same time
        cursor.beginEditBlock()

        for _ in range(0, end_block-start_block+1):
            cursor.movePosition(QTextCursor.StartOfBlock,
                                QTextCursor.MoveAnchor)

            if event.key() == Qt.Key_Tab:
                cursor.insertText("\t")
            elif event.key() == Qt.Key_Backtab:
                if not cursor.atBlockEnd():
                    # Select first character to see if it is a TAB
                    cursor.movePosition(QTextCursor.NextCharacter,
                                        QTextCursor.KeepAnchor)

                    print(cursor.selectedText())
                    if cursor.selectedText() == "\t":
                        cursor.removeSelectedText()

            cursor.movePosition(QTextCursor.NextBlock,
                                QTextCursor.MoveAnchor)

        cursor.endEditBlock()

        # Now we are going to completely select all the lines that
        # were changed from beginning to end

        cursor.setPosition(start_pos, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)

        while cursor.block().blockNumber() < end_block:
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)

        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        # Finally, set the new cursor
        self.setTextCursor(cursor)


class PyShowEditorLineNumberArea(QWidget):
    """The line number area in the main PyShow editor"""

    def __init__(self, editor):
        super().__init__(editor)

        self._editor = editor

    def get_width(self):
        """Calculate the width of the line number area"""
        digits = math.floor(math.log10(self._editor.document().blockCount()))+1
        return 25 + self._editor.fontMetrics().width('9') * digits

    def sizeHint(self):
        """Return the size of the line number area"""
        return QSize(self.get_width(), 0)

    def paintEvent(self, event):
        """A paint request is triggered, so pass it on"""
        self._editor.paint_line_numbers(event)
