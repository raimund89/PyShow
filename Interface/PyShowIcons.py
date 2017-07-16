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

from PyQt5.QtGui import QIcon, QPixmap


class PyShowIcons:

    def __init__(self):
        self._icons = {}

        self.load_icon("file_new")
        self.load_icon("file_open")
        self.load_icon("file_save")
        self.load_icon("file_print")

    def load_icon(self, name):
        self._icons[name] = QIcon()
        self._icons[name].addPixmap(QPixmap("Icons/"+name+"_32.png"), QIcon.Normal)

    def icon(self, name):
        try:
            return self._icons[name]
        except KeyError:
            print("Icon " +name+ " not found")
