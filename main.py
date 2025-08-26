import os
import sys
import subprocess
from functools import partial

import qdarktheme
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QGridLayout, QToolButton, QScrollArea, QLineEdit, \
    QVBoxLayout, QStackedWidget
from PyQt6.QtGui import QIcon


def open_app(name, gui):
    subprocess.run(['open', '-a', name])
    gui.close()


class AppController:
    def __init__(self):
        self.app_path = ["/System/Applications", "/Applications", f"{os.path.expanduser('~')}/Applications"]
        self.apps = []

    @staticmethod
    def get_app_icon(path):
        for entry in os.scandir(f"{path}/Contents/Resources"):
            if entry.name.endswith(".icns"):
                return entry.path
        return "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertNoteIcon.icns"

    def search_apps(self, path):
        for entry in os.scandir(path):
            if entry.name.endswith(".app"):
                self.apps.append((entry.name.strip(".app"), self.get_app_icon(entry.path)))
            elif entry.is_dir():
                self.search_apps(entry.path)

    def get_apps(self):
        for path in self.app_path:
            self.search_apps(path)
        return self.apps


class DisplayAppWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scroll_widget = QWidget()
        self.scroll = QScrollArea()
        self.grid = QGridLayout(self.scroll_widget)
        self.init_ui()

    def clear_all_apps(self):
        item_list = list(range(self.grid.count()))
        item_list.reverse()
        for idx in item_list:
            item = self.grid.itemAt(idx)
            self.grid.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

    def insert_apps(self, apps):
        row = 0
        col = 0
        icon_width = (self.width() - (10 * 6)) // 5
        icon_height = (self.height() - (10 * 6)) // 5
        for name, icon in apps:
            button = QToolButton()
            button.setText(name)
            button.clicked.connect(partial(open_app, button.text(), self))
            self.grid.addWidget(button, row, col)
            if icon == 'empty':
                continue
            load_icon = QIcon(icon)
            button.setIcon(load_icon)
            button.setIconSize(QSize(icon_width, icon_height))
            button.setToolButtonStyle(button.toolButtonStyle().ToolButtonTextUnderIcon)
            col += 1
            if col >= 5:
                row += 1
                col = 0
        self.grid.setSpacing(10)

    def init_ui(self):
        self.scroll.setWidget(self.scroll_widget)
        self.scroll.setWidgetResizable(True)


class LaunchPad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked = QStackedWidget()
        self.vbox_widget = QWidget()
        self.vbox = QVBoxLayout(self.vbox_widget)
        self.all_app_widget = DisplayAppWidget()
        self.search_app_widget = DisplayAppWidget()
        self.app_controller = AppController()
        self.apps = self.app_controller.get_apps()

        self.edit = QLineEdit()

        self.init_ui()

    def get_search_value(self, text):
        if text == "":
            self.stacked.setCurrentIndex(0)
            return
        self.stacked.setCurrentIndex(1)
        self.search_app_widget.clear_all_apps()
        text = text.lower()
        apps = []
        for name, icon in self.apps:
            if text in name.lower():
                apps.append((name, icon))
        self.search_app_widget.insert_apps(apps)

    def init_ui(self):
        self.edit.textChanged.connect(self.get_search_value)
        self.all_app_widget.insert_apps(self.apps)
        self.vbox.addWidget(self.edit)
        self.stacked.addWidget(self.all_app_widget.scroll)
        self.stacked.addWidget(self.search_app_widget.scroll)
        self.vbox.addWidget(self.stacked)
        self.setCentralWidget(self.vbox_widget)
        self.showFullScreen()

    def mousePressEvent(self, event):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    launch = LaunchPad()
    launch.show()
    sys.exit(app.exec())
