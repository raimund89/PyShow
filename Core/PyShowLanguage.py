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

from pyparsing import (Word, ParseException, alphas, nums, alphanums, Forward,
                       delimitedList, Literal, Group, Optional, OneOrMore,
                       quotedString, removeQuotes, Keyword, nestedExpr,
                       ParseFatalException, restOfLine)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QTextCharFormat, QFont, QSyntaxHighlighter

# TODO: function that tells the editor which lines have errors/warnings
# TODO: an actual parsing code
# TODO: style the parsing output as a dict/array combi for easy use

sectionList = ["beginTemplate",
               "endTemplate",
               "beginShow",
               "endShow",
               ]

functionList = ["setText",
                "addTextBlock",
                "newSlide"
                ]

actionList = ["pause"]


class PyShowParser():
    """Parser for the PyShow language"""

    def __init__(self, editor):
        self._editor = editor

        self._editor.textChanged.connect(self.parse)

        identifier = Word(alphas + "_", alphanums + "_")
        equal = Literal("=").suppress()
        string = quotedString.addParseAction(removeQuotes)
        integer = Word(nums).setParseAction(lambda s, l, t: [int(t[0])])
        setting = Group(identifier + equal + (integer | string))
        functor = identifier
        comment = Group(Literal("# ") + restOfLine).addParseAction(lambda s, l, t: {'comment': t[0][1]})

        self._expression = Forward()

        arg = integer | string | delimitedList(setting).addParseAction(self.format_settings)
        args = delimitedList(arg)

        normalline = ((functor +
                       Group(Literal("(").suppress() +
                             Optional(args) +
                             Literal(")").suppress()) +
                       Optional(comment)) | comment)

        template_begin = (Keyword("beginTemplate") +
                          Group(Literal("(").suppress() +
                                Optional(args) +
                                Literal(")").suppress()) +
                          Optional(comment))
        template_section = template_begin + Group(nestedExpr('{', '}', normalline))

        resourceset_begin = (Keyword("beginResourceSet") +
                             Group(Literal("(").suppress() +
                                   Optional(args) +
                                   Literal(")").suppress()) +
                             Optional(comment))
        resourceset_section = resourceset_begin + Group(nestedExpr('{', '}', normalline))

        show_begin = (Keyword("beginShow") +
                      Group(Literal("(").suppress() +
                            Optional(args) +
                            Literal(")").suppress()) +
                      Optional(comment))
        show_section = show_begin + Group(nestedExpr('{', '}', normalline))

        self._expression << OneOrMore(template_section |
                                      show_section |
                                      resourceset_section |
                                      comment)

    def parse(self):
        try:
            print(self._editor.toPlainText())
            parsed = self._expression.parseString(self._editor.toPlainText())
            parsed.pprint()
        except ParseException as pe:
            print("Error at line " +
                  str(pe.lineno) +
                  " column " +
                  str(pe.col) +
                  ": " +
                  pe.line)
        except ParseFatalException:
            print("Cannot parse right now!")

    def format_settings(self, s, l, t):
        return {'settings': {x[0]: x[1] for x in t}}


class PyShowEditorHighlighter(QSyntaxHighlighter):
    """The highlighter class providing the syntax highlighting"""

    # List of keywords
    operators = ['+', '-', '*', '/']
    comments = ['%', '#']

    def __init__(self, editor):
        super().__init__(editor)
        self.parent = editor
        self.highlightingRules = []

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.darkBlue)
        keyword.setFontWeight(QFont.Bold)

        for word in sectionList:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.blue)
        keyword.setFontWeight(QFont.Bold)

        for word in functionList:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.darkGreen)
        keyword.setFontWeight(QFont.Bold)

        for word in actionList:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        # Integers
        comment = QTextCharFormat()
        comment.setForeground(Qt.red)
        comment.setFontItalic(True)
        pattern = QRegularExpression("[0-9]")
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # Strings
        string = QTextCharFormat()
        string.setForeground(Qt.darkMagenta)
        string.setFontItalic(True)
        pattern = QRegularExpression("\".*?\"")
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)
        pattern = QRegularExpression("\'.*?\'")
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
        """Process the given text using the highlighting rules"""
        for rule in self.highlightingRules:
            iterator = rule.pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(),
                               match.capturedLength(),
                               rule.format)


class HighlightingRule():
    """A simple structure that contains the pattern and format for a rule"""

    def __init__(self, pattern, formatting):
        self.pattern = pattern
        self.format = formatting
