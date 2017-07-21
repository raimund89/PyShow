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

from pyparsing import Word, Optional, ParseException
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QTextCharFormat, QFont, QSyntaxHighlighter


class PyShowParser():

    def __init__(self, editor):
        self._editor = editor


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
