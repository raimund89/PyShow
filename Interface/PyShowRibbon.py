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
Class responsible for populating the window ribbon.

Many apps nowadays use this ribbon style, and especially in an office
application like this, it's very useful. The code styles the ribbon according
to the menu specified by the application window.
"""

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QToolBar, QTabWidget, QWidget, QHBoxLayout,
                             QVBoxLayout, QLabel, QToolButton)
from PyQt5.QtGui import QPainter, QColor


class PyShowRibbon(QToolBar):
    """The RibbonBar for the PyShow main window."""

    def __init__(self, parent):
        super().__init__()

        # Remember the parent so we can interact with it
        self._parent = parent

        # Remove the moving handle
        self.setMovable(False)

        # To make this toolbar a ribbonbar, the whole toolbar is filled
        # with a tabwidget, that actually contains all buttons and stuff
        self._widget = QTabWidget(self)
        self._widget.setMaximumHeight(125)
        self._widget.setMinimumHeight(125)
        self.addWidget(self._widget)

        self.makeup()

    def add_tab(self, name):
        """Add a new tab to the RibbonBar."""
        # Make a new ribbon tab widget
        tab = PyShowRibbonTab(self)
        # Give the tab a name so we can activate it later when necessary
        tab.setObjectName('tab_' + name)
        # Add the tab to the ribbon
        self._widget.addTab(tab, name)

        # Now add a spacer tab. This is a hack, but the only one
        # I know of right now that works
        spacer = QWidget()
        spacer.setObjectName('spacer_' + name)
        self._widget.setTabEnabled(self._widget.addTab(spacer, 'spacer'),
                                   False)

        return tab

    def set_active(self, name):
        """Set a tab of the RibbonBar as active."""
        # Select a tab by name
        self.setCurrentWidget(self.findChild(PyShowRibbonTab, 'tab_' + name))

    def makeup(self):
        """Style the RibbonBar so it looks cool."""
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
                                   "color: #333;"
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
                                   "QTabBar::tab::disabled {"
                                   "width: 4px;"
                                   "margin: 0px;"
                                   "padding: 0px;"
                                   "background: transparent;"
                                   "color: transparent;"
                                   "}"
                                   "QTabWidget::tab-bar{left:2px;}")

    def __getitem__(self, name):
        """Get a tab by name."""
        return self.findChild(PyShowRibbonTab, 'tab_' + name)


class PyShowRibbonTab(QWidget):
    """Tab that can reside in the RibbonBar."""

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
        """Add a pane to the tab, which contains controls."""
        pane = PyShowRibbonPane(self, name)
        self.layout().addWidget(pane)
        return pane

    def makeup(self):
        """Style the tab so it looks cool."""
        pass


class PyShowRibbonPane(QWidget):
    """A pane in the ribbon tab, to organize the controls on the tab."""

    def __init__(self, parent, name):
        super().__init__(parent)

        # The pane consists of a horizontal layout that contains
        # all the controls, within a vertical layout that
        # contains this horizontal layout and the name of the pane

        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container)

        vertical_widget = QWidget(self)
        container.addWidget(vertical_widget)
        container.addWidget(PyShowRibbonSeparator(self))

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 0, 5, 0)
        vertical_widget.setLayout(vbox)

        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666;margin-bottom:2px;")

        content = QWidget(self)

        vbox.addWidget(content, 100)
        vbox.addWidget(label)

        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignLeft)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.contentLayout = content_layout
        content.setLayout(content_layout)

    def add_widget(self, widget):
        """Add a control to the ribbon pane."""
        self.contentLayout.addWidget(widget, 0, Qt.AlignTop)


class PyShowRibbonSeparator(QWidget):
    """The separator between ribbon panes."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumHeight(85)
        self.setMaximumHeight(85)
        self.setMinimumWidth(1)
        self.setMaximumWidth(1)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, event):
        """Paint the single separator line."""
        qp = QPainter()
        qp.begin(self)
        qp.fillRect(event.rect(), QColor("#DDDDDD"))
        qp.end()


class PyShowRibbonPushButton(QToolButton):
    """A simple push button for in the ribbon pane."""

    def __init__(self, owner, action, style):
        super().__init__(owner)

        self._action = action
        self.clicked.connect(self._action.trigger)
        self.update_button()
        self._action.changed.connect(self.update_button)

        self.setToolButtonStyle(style)
        self.setIconSize(QSize(32, 32))

        self.setStyleSheet("QToolButton {"
                           "border: 1px solid transparent;"
                           "margin: 2px 2px 0px 2px;"
                           "min-height:70px;"
                           "}"
                           "QToolButton:hover {"
                           "border: 1px solid #999;"
                           "background-color: #ffaf87;"
                           "}"
                           "QToolButton:pressed {"
                           "border: 1px solid #666;"
                           "background-color: #ff9966;"
                           "}"
                           "QToolButton:checked {"
                           "border: 1px solid transparent;"
                           "background-color: #ffaf87;"
                           "}")

    def update_button(self):
        """Update the button due to an external change."""
        self.setText(self._action.text())
        self.setIcon(self._action.icon())
        self.setEnabled(self._action.isEnabled())
        self.setCheckable(self._action.isCheckable())
        self.setChecked(self._action.isChecked())
