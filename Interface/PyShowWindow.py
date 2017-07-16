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

from PyQt5.QtWidgets import QMainWindow
from Interface.PyShowRibbon import PyShowRibbon
from Interface.PyShowIcons import PyShowIcons


class PyShowWindow(QMainWindow):
    """The main PyShow window, containing all UI components"""

    def __init__(self, args):
        super().__init__()

        self._icons = PyShowIcons()
        self.init_ui()

    def init_ui(self):
        """Initialize the window settings and all UI components"""

        # Some basic setup for the window
        self.setWindowTitle('PyShow')
        self.resize(1280, 800)
        self.showMaximized()
        self.show()

        # Adding the different UI components

        # Ribbonbar
        self.init_ribbon()

        # Statusbar
        # Project manager
        # Editor
        # Preview window

    def init_ribbon(self):
        """Initialize the Ribbon bar with all components in it"""
        self._ribbon = PyShowRibbon(self)
        self.addToolBar(self._ribbon)

        self._ribbon_file = self._ribbon.add_tab('File')
        self._ribbon_home = self._ribbon.add_tab('Home')
        self._ribbon_insert = self._ribbon.add_tab('Insert')
        self._ribbon_animations = self._ribbon.add_tab('Animations')

        self._ribbon_file.add_pane('Open/Save')
