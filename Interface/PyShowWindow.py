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

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QSplitter, QWidget
from Interface.PyShowRibbon import PyShowRibbon, PyShowRibbonPushButton
from Interface.PyShowIcons import PyShowIcons
from Interface.PyShowStatusbar import PyShowStatusbar
from Interface.PyShowEditor import PyShowEditor


class PyShowWindow(QMainWindow):
    """The main PyShow window, containing all UI components"""

    def __init__(self, args):
        super().__init__()

        self._actions = {}
        self._icons = PyShowIcons()

        self.init_actions()
        self.init_ui()

    def init_actions(self):
        """Initialize all actions that can be performed in this window"""
        # New file action
        action = QAction(self._icons.icon("file_new"), "New\nproject", self)
        action.triggered.connect(self.on_file_new)
        self.addAction(action)
        self._actions['file_new'] = action
        # Open file action
        action = QAction(self._icons.icon("file_open"), "Open...", self)
        action.triggered.connect(self.on_file_open)
        self.addAction(action)
        self._actions['file_open'] = action
        # Save file action
        action = QAction(self._icons.icon("file_save"), "Save", self)
        action.triggered.connect(self.on_file_save)
        self.addAction(action)
        self._actions['file_save'] = action
        # Print file
        action = QAction(self._icons.icon("file_print"), "Print", self)
        action.triggered.connect(self.on_file_print)
        self.addAction(action)
        self._actions['file_print'] = action
        
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
        self._statusbar = PyShowStatusbar()
        self.setStatusBar(self._statusbar)

        # Divide window with a splitter
        self._splitter = QSplitter()
        self._splitter.setStyleSheet("QSplitter::handle {"
                                         "width: 1px;"
                                         "border: 1px solid #DDD;"
                                     "}")
        self.setCentralWidget(self._splitter)

        # Project manager
        # Editor
        self._editor = PyShowEditor()
        self._splitter.addWidget(self._editor)

        # Preview window
        self._preview = QWidget()
        self._preview.setStyleSheet("border: none;background-color: #F9F9F9")
        self._splitter.addWidget(self._preview)

    def init_ribbon(self):
        """Initialize the Ribbon bar with all components in it"""
        self._ribbon = PyShowRibbon(self)
        self.addToolBar(self._ribbon)

        self._ribbon_file = self._ribbon.add_tab('File')
        self._ribbon_home = self._ribbon.add_tab('Home')
        self._ribbon_insert = self._ribbon.add_tab('Insert')
        self._ribbon_animations = self._ribbon.add_tab('Animations')

        file_opensave = self._ribbon_file.add_pane('Open/Save')
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_new'], 3))
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_open'], 3))
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_save'], 3))

        file_print = self._ribbon_file.add_pane('Printing')
        file_print.add_widget(PyShowRibbonPushButton(self, self._actions['file_print'], 3))

    def on_file_new(self):
        pass

    def on_file_open(self):
        pass

    def on_file_save(self):
        pass

    def on_file_print(self):
        pass
