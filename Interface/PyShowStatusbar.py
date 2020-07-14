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
Class responsible for the status bar.

Populates the status bar, and updates any fields according to events happening
in the application. Also Capslock, Numlock and Scrolllock are indicated
"""

# TODO: Indicate capslock, numlock and scrolllock

from PyQt5.QtWidgets import QStatusBar


class PyShowStatusbar(QStatusBar):
    """The statusbar in the PyShow main window."""

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: white;"
                           "border-top: 1px solid #DDD;"
                           "height: 20px;")
