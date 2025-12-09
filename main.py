from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QLabel, QWidget, QStackedWidget, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.QtGui import QIcon
from services import ServicesPage
from clean import CleanPage
from uwp_app import UWPAppsPage
from registry import RegistryPage
from network import NetworkPage
from privacy import PrivacyPage
from autorun import AutorunPage
from powersave import PowerSavePage
from miscellaneous import MiscellaneousPage
from customization import CustomizationPage
from home import HomePage
from admin import AdminWarningWidget, is_admin
import sys


class SidebarItem(QWidget):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 5, 5)

        # Создаем иконку и метку
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(icon_path).pixmap(42, 42))
        self.text_label = QLabel(text)

        # Важно: изначально скрываем текст
        self.text_label.setVisible(False)

        # Добавляем их в layout
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # Стилизация
        self.text_label.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")

    def setTextVisible(self, visible):
        self.text_label.setVisible(visible)


class HoverSidebar(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        self.expanded_width = 210
        self.collapsed_width = 74
        self.is_expanded = False
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.collapse)

        # Начальное состояние - свернуто
        self.setFixedWidth(self.collapsed_width)

        # Отключаем вертикальный ползунок
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Настройка стилей
        self.setStyleSheet("""
            QListWidget {
                background-color: #121212;
                color: white;
                border: 1px solid;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                font-family: Arial, sans-serif;
                outline: none;
            }
            QListWidget::item {
                padding: 0px;
                margin: 2px 0;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
            QListWidget::item:selected {
                background-color: #333333;
                border-left: 2px solid #B3B3B3;
                border-radius: 5px;
            }
        """)

    def add_item_with_icon(self, icon_path, text):
        item = QListWidgetItem(self)
        widget = SidebarItem(icon_path, text)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
        return widget

    def enterEvent(self, event):
        self.hover_timer.stop()
        self.expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_timer.start(500)
        super().leaveEvent(event)

    def expand(self):
        if not self.is_expanded:
            self.animation = QPropertyAnimation(self, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()
            self.is_expanded = True

            # Показываем текст для всех элементов
            for i in range(self.count()):
                item = self.item(i)
                widget = self.itemWidget(item)
                if isinstance(widget, SidebarItem):
                    widget.setTextVisible(True)

    def collapse(self):
        if self.is_expanded:
            self.animation = QPropertyAnimation(self, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.is_expanded = False

            # Скрываем текст для всех элементов
            for i in range(self.count()):
                item = self.item(i)
                widget = self.itemWidget(item)
                if isinstance(widget, SidebarItem):
                    widget.setTextVisible(False)


class WinTuner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinTuner")
        self.setGeometry(100, 100, 900, 600)

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layouts
        main_layout = QHBoxLayout()
        self.content_stack = QStackedWidget()

        # Создаем боковое меню с иконками
        self.sidebar = HoverSidebar()

        # Определяем пути к иконкам и тексты пунктов меню
        menu_items = [
            ("icons/logo.png", "Главная"),
            ("icons/misc.png", "Разное"),
            ("icons/services.png", "Службы"),
            ("icons/clean.png", "Очистка"),
            ("icons/uwp.png", "UWP App"),
            ("icons/registr.png", "Реестр"),
            ("icons/network.png", "Настройка сети"),
            ("icons/interface.png", "Кастомизация"),
            ("icons/privacy.png", "Приватность"),
            ("icons/auto_launch.png", "Автозагрузка"),
            ("icons/power_supply.png", "Электропитание")
        ]

        # Добавляем элементы в меню
        for icon_path, text in menu_items:
            self.sidebar.add_item_with_icon(icon_path, text)

        # Добавляем sidebar в layout
        main_layout.addWidget(self.sidebar)

        self.home_page = HomePage()
        self.content_stack.addWidget(self.home_page)

        if not is_admin():
            self.admin_warning_widget = AdminWarningWidget()
            self.content_stack.addWidget(self.admin_warning_widget)
        else:
            # Страницы контента
            self.miscellaneous_page = MiscellaneousPage()
            self.content_stack.addWidget(self.miscellaneous_page)

            self.services_page = ServicesPage()
            self.content_stack.addWidget(self.services_page)

            self.clean_page = CleanPage()
            self.content_stack.addWidget(self.clean_page)

            self.uwp_page = UWPAppsPage()
            self.content_stack.addWidget(self.uwp_page)

            self.registry_page = RegistryPage()
            self.content_stack.addWidget(self.registry_page)

            self.network_page = NetworkPage()
            self.content_stack.addWidget(self.network_page)

            self.customization_page = CustomizationPage()
            self.content_stack.addWidget(self.customization_page)

            self.privacy_page = PrivacyPage()
            self.content_stack.addWidget(self.privacy_page)

            self.autorun_page = AutorunPage()
            self.content_stack.addWidget(self.autorun_page)

            self.powersave_page = PowerSavePage()
            self.content_stack.addWidget(self.powersave_page)

        # Добавляем content stack в layout
        main_layout.addWidget(self.content_stack)

        # Устанавливаем главный layout
        self.central_widget.setLayout(main_layout)

        # Подключаем выбор в sidebar
        self.sidebar.currentRowChanged.connect(self.display_page)

        # Применяем стили
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QLabel {
                font-family: Arial, sans-serif;
            }
        """)

    def display_page(self, index):
        self.content_stack.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WinTuner()
    window.show()
    sys.exit(app.exec_())