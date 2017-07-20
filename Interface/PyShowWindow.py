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

from PyQt5.QtWidgets import (QMainWindow, QAction, QMenu, QSplitter,
                             QWidget, QMessageBox)
from Interface.PyShowRibbon import PyShowRibbon, PyShowRibbonPushButton
from Interface.PyShowIcons import PyShowIcons
from Interface.PyShowStatusbar import PyShowStatusbar
from Interface.PyShowEditor import PyShowEditor
from Interface.PyShowPreview import PyShowPreview
from Core.PyShowProject import PyShowProject


class PyShowWindow(QMainWindow):
    """The main PyShow window, containing all UI components"""

    def __init__(self, args):
        super().__init__()

        self._actions = {}
        self._icons = PyShowIcons()
        self._project = None

        self.init_actions()
        self.init_ui()

    def init_actions(self):
        """Initialize all actions that can be performed in this window"""
        # New file action
        action = QAction(self._icons.icon("file_new"), "New\nproject", self)
        action.setShortcut('Ctrl+N')
        action.triggered.connect(self.on_file_new)
        self.addAction(action)
        self._actions['file_new'] = action
        # Open file action
        action = QAction(self._icons.icon("file_open"), "Open...", self)
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self.on_file_open)
        self.addAction(action)
        self._actions['file_open'] = action
        # Save file action
        action = QAction(self._icons.icon("file_save"), "Save", self)
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self.on_file_save)
        self.addAction(action)
        self._actions['file_save'] = action
        # Print file
        action = QAction(self._icons.icon("file_print"), "Print", self)
        action.setShortcut('Ctrl+P')
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
        self._splitter.setChildrenCollapsible(False)
        self._splitter.setStyleSheet("QSplitter::handle {"
                                         "width: 1px;"
                                         "border: 1px solid #DDD;"
                                     "}")
        self.setCentralWidget(self._splitter)

        # Project manager
        # Editor
        self.editor = PyShowEditor()
        # The project must be defined here, after the editor has been made
        self._project = PyShowProject(self)
        self._project.new()
        self._splitter.addWidget(self.editor)

        # Preview window
        self._preview = PyShowPreview(self._splitter)
        self._splitter.addWidget(self._preview)
        self._preview.initialize()

    def init_ribbon(self):
        """Initialize the Ribbon bar with all components in it"""
        self._ribbon = PyShowRibbon(self)
        self.addToolBar(self._ribbon)

        self._ribbon.add_tab('File')
        self._ribbon.add_tab('Home')
        self._ribbon.add_tab('Insert')
        self._ribbon.add_tab('Animations')

        file_opensave = self._ribbon["File"].add_pane('Open/Save')
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_new'], 3))
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_open'], 3))
        file_opensave.add_widget(PyShowRibbonPushButton(self, self._actions['file_save'], 3))

        file_print = self._ribbon["File"].add_pane('Printing')
        file_print.add_widget(PyShowRibbonPushButton(self, self._actions['file_print'], 3))

    def on_file_new(self):
        """Closing any current project and beginning a new project"""

        # If we have an open project, first close it
        if self._project.opened and self._project.changed():
            reply = QMessageBox.warning(self, "PyShow", "Do you want to save the current project?\n\nIf you don't save before opening a new project, all changes will be lost!", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self._project.save()

        self._project.new()

    def on_file_open(self):
        """Closing any current project and opening an existing project"""

        # If we have an open project, first close it
        if self._project.opened and self._project.changed():
            reply = QMessageBox.warning(self, "PyShow", "Do you want to save the current project?\n\nIf you don't save before opening a new project, all changes will be lost!", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self._project.save()

        self._project.open()

    def on_file_save(self):
        """Saving the currently open project"""

        self._project.save()

    def on_file_print(self):
        """Open the printing wizard and print the current project"""
        pass

    def closeEvent(self, event):
        """Called when user closes the PyShow main window"""

        # If we have an open project, first close it
        if self._project.opened and self._project.changed():
            reply = QMessageBox.warning(self, "PyShow", "Do you want to save the current project?\n\nIf you don't save before opening a new project, all changes will be lost!", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                if not self._project.save():
                    event.ignore()
                    return

        self._project.close()
