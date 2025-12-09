import winreg
import os
import wmi
import pythoncom
import win32api
from win32com.client import Dispatch
from typing import Dict, Optional, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QHBoxLayout, QMessageBox, QLineEdit,
                             QComboBox, QLabel, QSplitter, QTextEdit, QSizePolicy, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class AutorunPage(QWidget):
    """Страница управления автозагрузкой в стиле WinTuner."""

    update_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.items_data: Dict[str, dict] = {}
        self.init_ui()
        self.load_autorun_entries()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # Верхняя часть: фильтры и дерево
        top_widget = QWidget()
        top_layout = QVBoxLayout()

        # Панель фильтров
        filter_layout = QHBoxLayout()
        self._setup_search_bar(filter_layout)
        self._setup_filter_combo(filter_layout)
        self._setup_sort_combo(filter_layout)
        top_layout.addLayout(filter_layout)

        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #444444;
            }
        """)
        top_layout.addWidget(self.progress_bar)

        # Дерево автозагрузки
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Выбрать", "Элемент", "Путь", "Тип", "Состояние"])
        self.tree.setColumnWidth(0, 100)  # Колонка для чекбокса
        self.tree.setColumnWidth(1, 350)
        self.tree.setColumnWidth(2, 550)
        self.tree.setColumnWidth(3, 100)
        self.tree.setSortingEnabled(True)
        self.tree.itemClicked.connect(self.show_item_info)  # Отображение информации при клике
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QTreeWidget::item:hover {
                background-color: #333333;
            }
            QTreeWidget::item:selected {
                background-color: #444444;
            }
            QHeaderView::section {
            background-color: #1E1E1E;
            color: white;
            padding: 5px;
            border: 1px solid #555555;
        }
        """)
        top_layout.addWidget(self.tree)
        top_widget.setLayout(top_layout)

        # Нижняя часть: информация об элементе
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setFont(QFont("Arial", 12))
        self.info_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333333;
                border-radius: 5px;
            }
        """)
        self.info_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Настройка splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(self.info_display)
        splitter.setSizes([400, 200])
        splitter.setStyleSheet("QSplitter::handle { background-color: #333333; }")
        main_layout.addWidget(splitter)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self._setup_buttons(button_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #121212;")
        self.update_signal.connect(self.load_autorun_entries)

    def _setup_search_bar(self, layout: QHBoxLayout):
        search_label = QLabel("Поиск:")
        search_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени или пути...")
        self.search_input.textChanged.connect(self.filter_items)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.search_input)

    def _setup_filter_combo(self, layout: QHBoxLayout):
        filter_label = QLabel("Фильтр:")
        filter_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(filter_label)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "Включено", "Отключено"])
        self.filter_combo.currentTextChanged.connect(self.filter_items)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: white;
                selection-background-color: #444444;
            }
        """)
        layout.addWidget(self.filter_combo)

    def _setup_sort_combo(self, layout: QHBoxLayout):
        sort_label = QLabel("Сортировка:")
        sort_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(sort_label)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Имя", "Путь", "Тип"])
        self.sort_combo.currentTextChanged.connect(self.sort_items)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #2A2A2A;
                color: white;
                selection-background-color: #444444;
            }
        """)
        layout.addWidget(self.sort_combo)

    def _setup_buttons(self, layout: QHBoxLayout):
        buttons = [
            ("Включить", self.enable_items),
            ("Отключить", self.disable_items),
            ("Удалить", self.delete_items),
            ("Обновить", self.load_autorun_entries)
        ]
        btn_style = """
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #444444; }
            QPushButton:pressed { background-color: #555555; }
        """
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        layout.addStretch()

    def load_autorun_entries(self):
        """Загрузка элементов автозагрузки с индикатором прогресса."""
        self.tree.clear()
        self.items_data.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 4)
        self.progress_bar.setValue(0)

        categories = {
            "Реестр (Run)": self._fetch_registry_entries,
            "Службы": self._fetch_services,
            "Планировщик задач": self._fetch_scheduled_tasks,
            "Папка автозагрузки": self._fetch_startup_folder
        }

        progress = 0
        for category_name, fetch_method in categories.items():
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(1, category_name)  # Сдвигаем название из-за чекбокса
            category_item.setBackground(1, QColor("#2A2A2A"))
            fetch_method(category_item)
            progress += 1
            self.progress_bar.setValue(progress)

        self.tree.expandAll()
        self.filter_items()
        self.progress_bar.setVisible(False)

    def _fetch_registry_entries(self, parent_item: QTreeWidgetItem):
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
        ]

        for hive, subkey in reg_paths:
            try:
                with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            item = QTreeWidgetItem(parent_item)
                            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                            item.setCheckState(0, Qt.Unchecked)
                            item.setText(1, name)
                            item.setText(2, value)
                            item.setText(3, "Реестр")
                            item.setText(4, "Включено")
                            item.setData(0, Qt.UserRole, (hive, subkey, name))
                            self.items_data[f"registry_{name}"] = {
                                "item": item, "path": value, "type": "registry"
                            }
                            i += 1
                        except OSError:
                            break
            except OSError:
                pass

    def _fetch_services(self, parent_item: QTreeWidgetItem):
        try:
            c = wmi.WMI()
            for service in c.Win32_Service():
                if service.StartMode in ["Auto", "Manual", "Disabled"]:
                    item = QTreeWidgetItem(parent_item)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(1, service.DisplayName)
                    item.setText(2, service.PathName)
                    item.setText(3, "Служба")
                    item.setText(4, "Включено" if service.StartMode == "Auto" else "Отключено")
                    item.setData(0, Qt.UserRole, service.Name)
                    self.items_data[f"service_{service.Name}"] = {
                        "item": item, "path": service.PathName, "type": "service"
                    }
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки служб: {str(e)}")

    def _fetch_scheduled_tasks(self, parent_item: QTreeWidgetItem):
        try:
            pythoncom.CoInitialize()
            scheduler = Dispatch('Schedule.Service')
            scheduler.Connect()
            folders = [scheduler.GetFolder('\\')]

            while folders:
                folder = folders.pop(0)
                for task in folder.GetTasks(1):
                    item = QTreeWidgetItem(parent_item)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(1, task.Name)
                    item.setText(2, task.Path)
                    item.setText(3, "Задача")
                    item.setText(4, "Включено" if task.Enabled else "Отключено")
                    item.setData(0, Qt.UserRole, task.Path)
                    self.items_data[f"task_{task.Path}"] = {
                        "item": item, "path": task.Path, "type": "task"
                    }
                for subfolder in folder.GetFolders(0):
                    folders.append(subfolder)
            pythoncom.CoUninitialize()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки задач: {str(e)}")

    def _fetch_startup_folder(self, parent_item: QTreeWidgetItem):
        startup_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup")
        try:
            for filename in os.listdir(startup_path):
                full_path = os.path.join(startup_path, filename)
                if os.path.isfile(full_path):
                    item = QTreeWidgetItem(parent_item)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.Unchecked)
                    item.setText(1, filename)
                    item.setText(2, full_path)
                    item.setText(3, "Папка")
                    item.setText(4, "Включено")
                    item.setData(0, Qt.UserRole, full_path)
                    self.items_data[f"startup_{filename}"] = {
                        "item": item, "path": full_path, "type": "startup"
                    }
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки папки: {str(e)}")

    def filter_items(self):
        search_text = self.search_input.text().lower()
        filter_state = self.filter_combo.currentText()

        for i in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(i)
            for j in range(category.childCount()):
                item = category.child(j)
                name = item.text(1).lower()
                path = item.text(2).lower()
                state = item.text(4)
                state_match = (filter_state == "Все" or state == filter_state)
                search_match = (search_text in name or search_text in path)
                item.setHidden(not (state_match and search_match))

    def sort_items(self):
        column_map = {"Имя": 1, "Путь": 2, "Тип": 3}  # Сдвинуты из-за чекбокса
        self.tree.sortItems(column_map[self.sort_combo.currentText()], Qt.AscendingOrder)

    def show_item_info(self, item: QTreeWidgetItem, column: int):
        """Отображение информации о кликнутом элементе."""
        self.info_display.clear()
        if not item or item.childCount() > 0:  # Пропускаем категории
            return

        item_key = self._get_item_key(item)
        if not item_key or item_key not in self.items_data:
            return

        data = self.items_data[item_key]
        info = (
            f"Имя: {item.text(1)}\n"
            f"Путь: {data['path']}\n"
            f"Тип: {item.text(3)}\n"
            f"Состояние: {item.text(4)}\n"
        )

        try:
            if data["type"] == "service":
                c = wmi.WMI()
                service = c.Win32_Service(Name=item.data(0, Qt.UserRole))[0]
                info += f"Описание: {service.Description or 'Нет описания'}\n"
            elif data["type"] in ["registry", "startup"]:
                if os.path.exists(data["path"]):
                    file_info = win32api.GetFileVersionInfo(data["path"], "\\")
                    version = f"{file_info['FileVersionMS'] >> 16}.{file_info['FileVersionMS'] & 0xFFFF}." \
                              f"{file_info['FileVersionLS'] >> 16}.{file_info['FileVersionLS'] & 0xFFFF}"
                    info += f"Версия файла: {version}\n"
                else:
                    info += "Версия файла: Файл не найден\n"
        except Exception as e:
            info += f"Доп. информация: Ошибка получения ({str(e)})\n"

        self.info_display.setText(info)

    def _get_item_key(self, item: QTreeWidgetItem) -> Optional[str]:
        item_type = item.text(3)
        if item_type == "Реестр":
            return f"registry_{item.text(1)}"
        elif item_type == "Служба":
            return f"service_{item.data(0, Qt.UserRole)}"
        elif item_type == "Задача":
            return f"task_{item.data(0, Qt.UserRole)}"
        elif item_type == "Папка":
            return f"startup_{item.text(1)}"
        return None

    def enable_items(self):
        """Включение отмеченных элементов автозагрузки."""
        items = self._validate_checked_items()
        if not items:
            return

        errors = []
        for item in items:
            item_type, data = item.text(3), item.data(0, Qt.UserRole)
            try:
                if item_type == "Реестр":
                    continue  # Включение реестра вручную не поддерживается
                elif item_type == "Служба":
                    c = wmi.WMI()
                    service = c.Win32_Service(Name=data)[0]
                    service.ChangeStartMode("Automatic")
                    item.setText(4, "Включено")
                elif item_type == "Задача":
                    pythoncom.CoInitialize()
                    scheduler = Dispatch('Schedule.Service')
                    scheduler.Connect()
                    task = scheduler.GetFolder('\\').GetTask(data)
                    task.Enabled = True
                    item.setText(4, "Включено")
                    pythoncom.CoUninitialize()
                elif item_type == "Папка":
                    continue  # Включение файлов вручную не поддерживается
            except Exception as e:
                errors.append(f"Элемент '{item.text(1)}': {str(e)}")

        if errors:
            QMessageBox.warning(self, "Ошибки", "Не удалось включить некоторые элементы:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Успех", f"Включено {len(items)} элементов.")
        self.update_signal.emit()

    def disable_items(self):
        """Отключение отмеченных элементов автозагрузки."""
        items = self._validate_checked_items()
        if not items:
            return

        errors = []
        for item in items:
            item_type, data = item.text(3), item.data(0, Qt.UserRole)
            try:
                if item_type == "Реестр":
                    hive, subkey, name = data
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, name)
                    item.setText(4, "Отключено")
                elif item_type == "Служба":
                    c = wmi.WMI()
                    service = c.Win32_Service(Name=data)[0]
                    service.ChangeStartMode("Disabled")
                    item.setText(4, "Отключено")
                elif item_type == "Задача":
                    pythoncom.CoInitialize()
                    scheduler = Dispatch('Schedule.Service')
                    scheduler.Connect()
                    task = scheduler.GetFolder('\\').GetTask(data)
                    task.Enabled = False
                    item.setText(4, "Отключено")
                    pythoncom.CoUninitialize()
                elif item_type == "Папка":
                    os.remove(data)
                    item.setText(4, "Отключено")
            except Exception as e:
                errors.append(f"Элемент '{item.text(1)}': {str(e)}")

        if errors:
            QMessageBox.warning(self, "Ошибки", "Не удалось отключить некоторые элементы:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Успех", f"Отключено {len(items)} элементов.")
        self.update_signal.emit()

    def delete_items(self):
        """Удаление отмеченных элементов автозагрузки."""
        items = self._validate_checked_items()
        if not items:
            return

        item_names = [item.text(1) for item in items]
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы уверены, что хотите удалить {len(items)} элементов?\n" + "\n".join(
                                         item_names),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        errors = []
        for item in items:
            item_type, data = item.text(3), item.data(0, Qt.UserRole)
            item_key = self._get_item_key(item)
            if not item_key:
                continue

            try:
                if item_type == "Реестр":
                    hive, subkey, name = data
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, name)
                elif item_type == "Служба":
                    continue  # Удаление служб не поддерживается
                elif item_type == "Задача":
                    pythoncom.CoInitialize()
                    scheduler = Dispatch('Schedule.Service')
                    scheduler.Connect()
                    folder = scheduler.GetFolder('\\')
                    task_name = data.split('\\')[-1]
                    folder.DeleteTask(task_name, 0)
                    pythoncom.CoUninitialize()
                elif item_type == "Папка":
                    if os.path.exists(data):
                        os.remove(data)
                    else:
                        raise FileNotFoundError("Файл уже удален или перемещен")

                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                if item_key in self.items_data:
                    del self.items_data[item_key]
            except Exception as e:
                errors.append(f"Элемент '{item.text(1)}': {str(e)}")

        if errors:
            QMessageBox.warning(self, "Ошибки", "Не удалось удалить некоторые элементы:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Успех", f"Удалено {len(items)} элементов.")
        self.update_signal.emit()

    def _validate_checked_items(self) -> Optional[List[QTreeWidgetItem]]:
        """Проверка отмеченных элементов."""
        checked_items = []
        for i in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(i)
            for j in range(category.childCount()):
                item = category.child(j)
                if item.checkState(0) == Qt.Checked:
                    checked_items.append(item)

        if not checked_items:
            QMessageBox.warning(self, "Ошибка", "Отметьте хотя бы один элемент для действия.")
            return None
        return checked_items
