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

from PyQt5.QtWidgets import QFileDialog, QMessageBox


class PyShowProject:

    def __init__(self, mainwindow):
        self._mainwindow = mainwindow

        self._filename = ''
        self.opened = False
        self.changed = False

        self._mainwindow._editor.textChanged.connect(self.changeEvent)

    def set_changed(self, val):

        if self.changed is not val:
            self.changed = val

            if self._filename:
                name = self._filename
            else:
                name = 'Untitled'

            if self.changed:
                self._mainwindow.setWindowTitle('PyShow - ' + name + ' *')
            else:
                self._mainwindow.setWindowTitle('PyShow - ' + name)

    def new(self):

        self.close()
        self.opened = True
        self.set_changed(False)

    def open(self):
        filename = QFileDialog.getOpenFileName(self._mainwindow,
                                               'Open Project',
                                               '',
                                               'PyShow Project (*.psp);;All Files(*)')[0]

        if filename:
            self.close()
            self._filename = filename
            file = open(self._filename, 'r')
            self._mainwindow._editor.setText(file.read())
            file.close()
            self.opened = True
            self.set_changed(False)
        else:
            QMessageBox.warning(self._mainwindow, "PyShow", "No project was opened!!!", QMessageBox.Ok)

    def save(self):

        # If no filename is set yet, ask for one
        if not self._filename:
            self._filename = QFileDialog.getSaveFileName(self._mainwindow,
                                                         'Save Project',
                                                         '',
                                                         'PyShow Project (*.psp)')[0]

        # Now save the file, but always check because the user could have
        # canceled
        if self._filename:
            file = open(self._filename, 'w')
            text = self._mainwindow._editor.toPlainText()
            file.write(text)
            file.close()
            self.opened = True
            self.set_changed(False)
        else:
            QMessageBox.warning(self._mainwindow, "PyShow", "The project was not saved!", QMessageBox.Ok)

    def close(self):

        self._filename = ""
        self._mainwindow._editor.setText('')
        self.opened = False
        self.set_changed(False)

    def changeEvent(self):

        self.set_changed(True)
