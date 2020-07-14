# PyShow - a slide show IDE and scripting language.
#
# Copyright (C) 2017  Raimond Frentrop
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Class to interpret the presentation language used in PyShow.

It uses QRegularExpressions to make a map of the code and allow the editor
to highlight everything in the proper way.
"""

from pyparsing import (Word, ParseException, alphas, nums, Forward,
                       delimitedList, Literal, Group, Optional, ZeroOrMore,
                       OneOrMore, LineEnd, SkipTo, Combine, QuotedString)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QTextCharFormat, QFont, QSyntaxHighlighter

# TODO: function that tells the editor which lines have errors/warnings
# TODO: enable inline comments

sectionList = ["beginTemplate",
               "beginShow",
               "resources"
               ]

template_functions = {
                      "setBackgroundColor": "",
                      "addTextBox": "text",
                      "addBulletList": "list"
                      }
show_functions = {"newSlide": "",
                  "setTextBox": "text",
                  "setBulletList": "list",
                  }

resource_functions = {
                      "image": "loadImage",
                      "video": "loadVideo",
                      "audio": "loadAudio"
                      }

actionList = ["pause"]


class PyShowParser():
    """Parser for the PyShow language."""

    def __init__(self, editor):
        self._editor = editor

        self._editor.textChanged.connect(self.parse)

        identifier = Word(alphas + "_", alphas + nums + "_")
        eq = Literal("=").suppress()
        string = (QuotedString("'", escChar="\\", multiline=True) |
                  QuotedString('"', escChar="\\", multiline=True))
        minus = Optional("-")
        num = Word(nums)
        int_value = Combine(minus + num).setParseAction(lambda s, l, t: [int(t[0])])
        float_value = Combine(minus + Optional(num) + "." + num).setParseAction(lambda s, l, t: [float(t[0])])
        number = float_value | int_value
        functor = identifier.setParseAction(lambda loc, tok: (tok[0], loc))
        lbr = Literal('{').suppress()
        rbr = Literal('}').suppress()
        lp = Literal('(').suppress()
        rp = Literal(')').suppress()
        lbk = Literal('[').suppress()
        rbk = Literal(']').suppress()

        strlist = Group(lbk + Optional(delimitedList(string)) + rbk)
        setting = (Group(identifier("key") +
                         eq +
                         (number | string | strlist)("value")))
        comment = Group(Literal("#") + SkipTo(LineEnd())).suppress()

        self._expression = Forward()

        arg = Group(self._expression) | string | setting | number
        args = Group(lp + Optional(delimitedList(arg)) + rp)("args")

        command = Group(functor("name") + args)

        script = Group(functor("name") + args +
                       lbr +
                       ZeroOrMore(command | comment.suppress())("contents") +
                       rbr)
        self._expression << OneOrMore(script | comment.suppress())

    def parse(self):
        """Parse the text currently in the editor."""
        text = self._editor.toPlainText()

        if len(text) == 0:
            return

        try:
            parsed = self._expression.parseString(text.replace('\t', ' '),
                                                  parseAll=True)
            # print(parsed.dump())
            return parsed
        except ParseException as pe:
            # TODO: Make the editor highlight the line with wrong code
            print(pe)
            return


class PyShowEditorHighlighter(QSyntaxHighlighter):
    """The highlighter class providing the syntax highlighting."""

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

        for word in show_functions:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.darkRed)
        keyword.setFontWeight(QFont.Bold)

        for word in template_functions:
            pattern = QRegularExpression("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        keyword = QTextCharFormat()
        keyword.setForeground(Qt.darkYellow)
        keyword.setFontWeight(QFont.Bold)

        for word in resource_functions:
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
        pattern = QRegularExpression(r"(\"|').*?((?<!\\)(\1))")
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)

        # Comments
        comment = QTextCharFormat()
        comment.setForeground(Qt.darkGray)
        comment.setFontItalic(True)
        pattern = QRegularExpression("((?<!('|\"))#)[^\n]*")
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

    def highlightBlock(self, text):
        """Process the given text using the highlighting rules."""
        for rule in self.highlightingRules:
            iterator = rule.pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(),
                               match.capturedLength(),
                               rule.format)


class HighlightingRule():
    """A simple structure that contains the pattern and format for a rule."""

    def __init__(self, pattern, formatting):
        self.pattern = pattern
        self.format = formatting
