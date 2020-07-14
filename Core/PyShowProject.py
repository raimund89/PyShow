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
Class for opening and saving PyShow projects (*.psp).

PyShow projects currently only contain the main code file. This will be
extended soon to a data structure that can also contain images, multiple
scripts and other files related to the presentation.
"""

from PyQt5.QtWidgets import QFileDialog
import io
from zipfile import ZipFile


class PyShowProject:
    """Class that contains all the project hooks and information."""

    def __init__(self, mainwindow):
        self._mainwindow = mainwindow

        self._filename = ''
        self._lastsaved = ''
        self.opened = False

        self._mainwindow.editor.textChanged.connect(self.text_edited)

    def new(self):
        """Start a new project."""
        self.close()
        self.opened = True

    def open(self):
        """Open an existing project from file."""
        filename = QFileDialog.getOpenFileName(self._mainwindow,
                                               'Open Project',
                                               '',
                                               'PyShow Project (*.psp);;All Files(*)')[0]

        if filename:
            self.close()

            self._filename = filename

            with ZipFile(filename, 'r') as zip:
                with io.TextIOWrapper(zip.open('main.script')) as script:
                    text = script.read()

                    self._mainwindow.editor.setText(text)

                    self._lastsaved = text
                    self.text_edited()
                self.opened = True

    def save(self):
        """Save the existing project, if a project is open."""
        if not self.opened:
            return True

        # If no filename is set yet, ask for one
        if not self._filename:
            self._filename = QFileDialog.getSaveFileName(self._mainwindow,
                                                         'Save Project',
                                                         '',
                                                         'PyShow Project (*.psp)')[0]

        # Now save the file, but always check because the user could have
        # canceled
        if self._filename:
            text = self._mainwindow.editor.toPlainText()

            with ZipFile(self._filename, 'w') as zip:
                zip.writestr('main.script', text)

                self._lastsaved = text
                self.text_edited()
                self.opened = True

                return True

        return False

    def close(self):
        """Close the project, get the GUI in order after that."""
        self._filename = ""

        self._mainwindow.editor.setText('')

        self._lastsaved = ""
        self.opened = False
        self._mainwindow.enable_action('file_save', False)

    def changed(self):
        """Return whether the text was changed compared to the last save."""
        if self._lastsaved == self._mainwindow.editor.toPlainText():
            return False

        return True

    def text_edited(self):
        """Trigger when text in the editor is changed."""
        if self._filename:
            name = self._filename
        else:
            name = 'Untitled'

        if not self.changed():
            self._mainwindow.setWindowTitle('PyShow - ' + name)
            self._mainwindow.enable_action('file_save', False)
        else:
            self._mainwindow.setWindowTitle('PyShow - ' + name + '*')
            self._mainwindow.enable_action('file_save', True)

    def name(self):
        """Return the name of the current file, or Untitled if none."""
        if self._filename:
            return self._filename
        else:
            return 'Untitled'
