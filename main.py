import os
import sys
import subprocess
from functools import partial

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QGridLayout, QToolButton, QScrollArea, QLineEdit, \
    QVBoxLayout
from PyQt6.QtGui import QIcon


class AppController:
    def __init__(self):
        self.app_path = ["/System/Applications", "/Applications", f"{os.path.expanduser('~')}/Applications"]
        self.apps = []

    @staticmethod
    def get_app_icon(path):
        for entry in os.scandir(f"{path}/Contents/Resources"):
            if entry.name.endswith(".icns"):
                return entry.path
        return "empty"

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

    @staticmethod
    def open_app(name, gui):
        subprocess.run(['open', '-a', name])
        gui.close()


class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()

        self.controller = AppController()

        self.apps = self.controller.get_apps()
        self.vbox_widget = QWidget()
        self.vbox = QVBoxLayout(self.vbox_widget)
        self.scroll_widget = QWidget()
        self.scroll = QScrollArea()
        self.grid = QGridLayout(self.scroll_widget)

        self.edit = QLineEdit()
        self.vbox.addWidget(self.edit)
        self.edit.textChanged.connect(self.get_change_text)

        self.init_ui()
        self.insert_apps(self.apps)

    def clear_all_apps(self):
        item_list = list(range(self.grid.count()))
        item_list.reverse()
        for idx in item_list:
            item = self.grid.itemAt(idx)
            self.grid.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

    def get_change_text(self, text):
        self.clear_all_apps()
        if text == "":
            self.insert_apps(self.apps)
            return
        text = text.lower()
        apps = []
        for name, icon in self.apps:
            if text in name.lower():
                apps.append((name, icon))
        self.insert_apps(apps)

    def insert_apps(self, apps):
        row = 0
        col = 0
        icon_width = (self.width() - (50 * 6)) // 5
        icon_height = (self.height() - (50 * 6)) // 5
        for name, icon in apps:
            button = QToolButton()
            button.setText(name)
            button.clicked.connect(partial(self.controller.open_app, button.text(), self))
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
        self.grid.setSpacing(50)

    def init_ui(self):
        self.vbox.addWidget(self.scroll)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.vbox_widget)
        self.showFullScreen()

    def mousePressEvent(self, event):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Launcher()
    ex.show()
    sys.exit(app.exec())
