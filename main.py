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

import sys
import ctypes
import os
from PyQt5.QtWidgets import QApplication
from Interface.PyShowWindow import PyShowWindow

if __name__ == '__main__':
    # Main entry point of PyShow
    app = QApplication(sys.argv)

    if os.name == 'nt':
        appid = u'pyshow.application'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    w = PyShowWindow(sys.argv)
    sys.exit(app.exec_())
