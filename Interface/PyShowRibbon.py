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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QToolBar, QTabWidget, QWidget, QHBoxLayout)


class PyShowRibbon(QToolBar):
    """The RibbonBar for the PyShow main window"""

    def __init__(self, parent):
        super().__init__()

        # Remember the parent so we can interact with it
        self._parent = parent

        # Remove the moving handle
        self.setMovable(False)

        # To make this toolbar a ribbonbar, the whole toolbar is filled
        # with a tabwidget, that actually contains all buttons and stuff
        self._widget = QTabWidget(self)
        self._widget.setMaximumHeight(115)
        self._widget.setMinimumHeight(115)
        self.addWidget(self._widget)

        self.makeup()

    def add_tab(self, name):
        """Add a new tab to the RibbonBar"""
        # Make a new ribbon tab widget
        tab = PyShowRibbonTab(self)
        # Give the tab a name so we can activate it later when necessary
        tab.setObjectName('tab_' + name)
        # Add the tab to the ribbon
        self._widget.addTab(tab, name)
        return tab

    def set_active(self, name):
        """Set a tab of the RibbonBar as active"""
        # Select a tab by name
        self.setCurrentWidget(self.findChild('tab_' + name))

    def makeup(self):
        """Style the RibbonBar so it looks cool"""

        # The top-most widget
        self.setStyleSheet("background-color: white;"
                           "border: none;"
                           "padding: 0;")

        # The tab view widget
        self._widget.setStyleSheet("QTabWidget:pane {"
                                       "background-color: white;"
                                       "border-top: 1px solid #DDD;"
                                       "border-bottom: 1px solid #DDD;"
                                       "top: -1px;"
                                       "margin: 0px;"
                                       "padding: 0px;"
                                       "}"
                                   "QTabBar { "
                                       "font-size: 10pt;"
                                   "}"
                                   "QTabBar::tab{"
                                       "background-color: white;"
                                       "padding: 6px 12px 6px 12px;"
                                       "margin-right: 4px;"
                                       "color: #333;"
                                       "border: 1px solid #FFF;"
                                       "border-bottom: 1px solid #DDD;"
                                   "}"
                                   "QTabBar::tab::hover{"
                                       "color: #D15E00;"
                                   "}"
                                   "QTabBar::tab::selected{"
                                       "border: 1px solid #DDD;"
                                       "border-bottom: 1px solid #FFF;"
                                       "color: #D15E00;"
                                   "}"
                                   "QTabWidget::tab-bar{left:2px;}")

        # Style of the tab headers
        # self._widget


class PyShowRibbonTab(QWidget):
    """Tab that can reside in the RibbonBar"""

    def __init__(self, parent):
        super().__init__()

        # Remember the parent so we can interact with it
        self._parent = parent

        # The ribbon tab is filled horizontally with panels containing controls
        layout = QHBoxLayout()
        # No margins
        layout.setContentsMargins(0, 0, 0, 0)
        # No spacing between items in the layout
        layout.setSpacing(0)
        # Don't spread the widgets over the whole length
        layout.setAlignment(Qt.AlignLeft)

        # Add the layout to the ribbon tab
        self.setLayout(layout)

        self.makeup()

    def add_pane(self, name):
        """Add a pane to the tab, which contains controls"""
        pass

    def add_spacer(self):
        """Add a spacer between the panes"""
        pass

    def makeup(self):
        """Style the tab so it looks cool"""

        pass
