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

# TODO: Combine icons if different sizes in one QIcon
# TODO: add white app icon, and check which is better with taskbar color.

"""
Class for all icons in the program.

Loads all necessary icons to run the application at the same time, so cleans
up the code by not doing this in every single class where an icon is needed.
"""

from PyQt6.QtGui import QIcon, QPixmap


class PyShowIcons:
    """Container for all icons needed by PyShow."""

    def __init__(self):
        self._icons = {}

        self.load_icon("pyshow_icon")
        self.load_icon("file_new")
        self.load_icon("file_open")
        self.load_icon("file_save")
        self.load_icon("file_print")

    def load_icon(self, name):
        """Load an icon from file."""
        self._icons[name] = QIcon()
        self._icons[name].addPixmap(QPixmap("Icons/"+name+"_32.png"),
                                    QIcon.Mode.Normal)

    def icon(self, name):
        """Return the icon with the specified name."""
        try:
            return self._icons[name]
        except KeyError:
            print("Icon " + name + " not found")
