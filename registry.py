import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
                             QComboBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import QThread, pyqtSignal
import winreg
import logging
from enum import Enum
from datetime import datetime
import os
import time


class ProblemSeverity(Enum):
    CRITICAL = 3
    HIGH = 2
    LOW = 1


class ScanThread(QThread):
    problem_found = pyqtSignal(str, str, str, str, ProblemSeverity)
    scan_completed = pyqtSignal()
    progress_update = pyqtSignal(int)

    def __init__(self, min_severity):
        super().__init__()
        self.min_severity = min_severity
        self.scanner = RegistryScanner()

    def run(self):
        def problem_callback(hive, path, name, value, severity):
            self.problem_found.emit(hive, path, name, value, severity)

        progress_buffer = 0
        last_update_time = time.time()

        def progress_callback(result):
            nonlocal progress_buffer, last_update_time
            progress_buffer += 1
            current_time = time.time()
            if current_time - last_update_time > 0.1 or progress_buffer > 100:  # Обновляем каждые 100 мс или 100 шагов
                self.progress_update.emit(progress_buffer)
                progress_buffer = 0
                last_update_time = current_time

        self.scanner.scan_with_callback(problem_callback, progress_callback, self.min_severity)
        self.scan_completed.emit()


class BackupThread(QThread):
    backup_completed = pyqtSignal(bool, str)

    def __init__(self, backup_file):
        super().__init__()
        self.backup_file = backup_file

    def run(self):
        try:
            result = subprocess.run(
                ['reg', 'export', 'HKLM', self.backup_file, '/y'],
                capture_output=True,
                text=True,
                check=True
            )
            self.backup_completed.emit(True, "Резервная копия реестра успешно создана.")
        except subprocess.CalledProcessError as e:
            error_message = f"Ошибка при создании резервной копии: {e.stderr}"
            logging.error(error_message)
            self.backup_completed.emit(False, error_message)


class RegistryScanner:
    def __init__(self):
        self.log_file = f"logs/registry/registry_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.setup_logging()

        # Расширил список критических расширений
        self.critical_extensions = {'.dll', '.sys', '.drv', '.exe', '.ocx', '.ax', '.cpl'}

        # Добавил больше критических путей и уточнил их приоритеты
        self.critical_paths = {
            'System32': ProblemSeverity.CRITICAL,
            'SysWOW64': ProblemSeverity.CRITICAL,
            'drivers': ProblemSeverity.CRITICAL,
            'Windows': ProblemSeverity.HIGH,
            'Program Files': ProblemSeverity.HIGH,
            'Program Files (x86)': ProblemSeverity.HIGH,
            'Common Files': ProblemSeverity.HIGH,
            'AppData': ProblemSeverity.HIGH,
            'Temp': ProblemSeverity.HIGH
        }

        # Добавил проверку на специфические шаблоны в значениях
        self.suspicious_patterns = [
            '%SystemRoot%',
            '%ProgramFiles%',
            '%WinDir%',
            '%AppData%',
            '%Temp%',
            '%CommonProgramFiles%'
        ]

        self.skip_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
            r"SOFTWARE\Microsoft\Windows NT",
            r"SOFTWARE\Classes\*",
            r"SYSTEM\CurrentControlSet\Services",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            r"SOFTWARE\Classes\CLSID",
            r"SOFTWARE\Classes\TypeLib",
            r"SOFTWARE\Classes\Interface",
            r"SOFTWARE\Classes\AppID",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies",
            r"SOFTWARE\Microsoft\Windows Defender",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings",
            r"SOFTWARE\Microsoft\Direct3D",
            r"SOFTWARE\Microsoft\DirectDraw",
            r"SOFTWARE\Microsoft\DirectInput",
            r"SOFTWARE\Microsoft\DirectMusic",
            r"SOFTWARE\Microsoft\DirectPlay",
            r"SOFTWARE\Microsoft\DirectShow",
            r"SOFTWARE\Microsoft\DirectX",
            r"SYSTEM\CurrentControlSet\Control",
            r"SYSTEM\CurrentControlSet\Enum",
            r"SYSTEM\CurrentControlSet\Hardware Profiles",
        ]

        # Добавил исключения для валидных путей
        self.valid_paths = {
            r"C:\Windows",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Users"
        }

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def is_valid_path(self, path: str) -> bool:
        """Проверяет, является ли путь потенциально валидным."""
        if not path:
            return True

        # Проверка на UNC пути
        if path.startswith('\\\\'):
            return True

        # Проверка на переменные окружения
        expanded_path = os.path.expandvars(path)
        if expanded_path != path:  # если путь содержит переменные окружения
            path = expanded_path

        # Проверка на базовые валидные пути
        return any(path.lower().startswith(valid_path.lower()) for valid_path in self.valid_paths)

    def determine_severity(self, path: str, value: str) -> ProblemSeverity:
        """Улучшенное определение серьезности проблемы."""
        _, ext = os.path.splitext(value.lower())

        # Проверка на критические расширения
        if ext in self.critical_extensions:
            return ProblemSeverity.CRITICAL

        # Проверка на подозрительные шаблоны
        if any(pattern.lower() in value.lower() for pattern in self.suspicious_patterns):
            return ProblemSeverity.HIGH

        # Проверка на критические пути
        for critical_path, severity in self.critical_paths.items():
            if critical_path.lower() in value.lower():
                return severity

        # Проверка на исполняемые файлы в нестандартных местах
        if value.lower().endswith(('.exe', '.dll')) and not self.is_valid_path(value):
            return ProblemSeverity.HIGH

        return ProblemSeverity.LOW

    def validate_path(self, value: str) -> bool:
        """Проверяет, действительно ли путь является проблемным."""
        if not value or len(value) < 2:
            return True

        # Игнорируем URL и сетевые пути
        if value.startswith(('http://', 'https://', '\\\\', 'www.')):
            return True

        # Проверяем существование пути
        expanded_value = os.path.expandvars(value)
        if os.path.exists(expanded_value):
            return True

        # Проверяем, является ли путь потенциально валидным
        return self.is_valid_path(expanded_value)

    def scan_with_callback(self, problem_callback, progress_callback, min_severity):
        hives = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER
        }

        total_keys = 0
        processed_keys = 0

        for hive_name, hive in hives.items():
            try:
                self._scan_key_with_callback(
                    hive, "SOFTWARE", hive_name,
                    problem_callback, progress_callback,
                    min_severity, total_keys, processed_keys
                )
            except Exception as e:
                logging.error(f"Error scanning {hive_name}: {str(e)}")

    def _scan_key_with_callback(self, hive, path, hive_name, problem_callback,
                                progress_callback, min_severity, total_keys, processed_keys):
        try:
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)

            try:
                i = 0
                while True:
                    name, value, type_ = winreg.EnumValue(key, i)
                    if type_ == winreg.REG_SZ and value:
                        if ('\\' in value or '/' in value) and value.strip():
                            expanded_value = os.path.expandvars(value)
                            if not self.validate_path(expanded_value):
                                severity = self.determine_severity(path, expanded_value)
                                if severity.value >= min_severity.value:
                                    problem_callback(hive_name, path, name, value, severity)
                    i += 1
            except WindowsError:
                pass

            processed_keys += 1
            progress_callback(processed_keys)

            try:
                i = 0
                while True:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey_path = f"{path}\\{subkey_name}"

                    if not any(subkey_path.startswith(skip_path) for skip_path in self.skip_paths):
                        self._scan_key_with_callback(
                            hive, subkey_path, hive_name,
                            problem_callback, progress_callback,
                            min_severity, total_keys, processed_keys
                        )
                    i += 1
            except WindowsError:
                pass

            winreg.CloseKey(key)
        except WindowsError as e:
            logging.error(f"Error scanning {path}: {str(e)}")

    @staticmethod
    def delete_value(hive, path, name):
        try:
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            logging.info(f"Deleted value: {path}\\{name}")
            return True
        except WindowsError as e:
            logging.error(f"Error deleting {path}: {str(e)}")
            return False


class RegistryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_thread = None
        self.scan_thread = None
        self.results_table = None
        self.progress_bar = None
        self.clean_button = None
        self.scan_button = None
        self.severity_combo = None
        self.select_all_button = None
        self.backup_button = None
        self.initUI()
        self.problems = []

    def initUI(self):
        layout = QVBoxLayout()
        # Верхняя панель управления
        control_panel = QHBoxLayout()

        # Выпадающий список для выбора серьезности проблем
        self.severity_combo = QComboBox()
        self.severity_combo.setStyleSheet("""background-color: transparent; color: white; border: 1px solid #2d2d2d;""")
        self.severity_combo.addItems(["Критичные", "Высокий приоритет", "Все проблемы"])
        filter_label = QLabel("Фильтр:")
        filter_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: white;
                font-weight: bold;
            }
        """)
        control_panel.addWidget(filter_label)
        control_panel.addWidget(self.severity_combo)

        # Кнопка сканирования
        self.scan_button = QPushButton("Начать сканирование")
        self.scan_button.setStyleSheet("""
            QPushButton{
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: #1e8449;
                border: 1px solid #1e8449;
            }
            QPushButton:hover{
                border: 1px solid #196f3e;
                background-color: #196f3e;
            }""")
        self.scan_button.clicked.connect(self.start_scan)
        control_panel.addWidget(self.scan_button)

        # Кнопка выбора всех элементов
        self.select_all_button = QPushButton("Выбрать все")
        self.select_all_button.clicked.connect(self.select_all_items)
        self.select_all_button.setEnabled(True)
        self.select_all_button.setStyleSheet("""
            QPushButton{
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: #34495e;
                border: 1px solid #34495e;
            }
            QPushButton:hover{
                border: 1px solid #2b3c4e;
                background-color: #2b3c4e;
            }
        """)
        control_panel.addWidget(self.select_all_button)

        # Кнопка очистки
        self.clean_button = QPushButton("Очистить выбранное")
        self.clean_button.clicked.connect(self.clean_selected)
        self.clean_button.setStyleSheet("""
            QPushButton{
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: #f04438;
                border: 1px solid #f04438;
            }
            QPushButton:hover{
                border: 1px solid #ee2e20;
                background-color: #ee2e20;  
            }
        """)
        self.clean_button.setEnabled(False)
        control_panel.addWidget(self.clean_button)

        # Кнопка создания копии реестра
        self.backup_button = QPushButton("Создать копию реестра")
        self.backup_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        font-weight: bold;
                        background-color: #E67E22;
                        border: 1px solid #E67E22;
                        padding: 5px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #d67118;
                    }""")
        self.backup_button.clicked.connect(self.create_registry_backup)
        control_panel.addWidget(self.backup_button)

        control_panel.addStretch()
        layout.addLayout(control_panel)
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Устанавливаем неопределенный тип
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Расположение", "Путь", "Имя", "Значение"])
        self.results_table.setColumnWidth(0, 150)  # Расположение
        self.results_table.setColumnWidth(1, 545)  # Путь
        self.results_table.setColumnWidth(2, 150)  # Имя
        self.results_table.setColumnWidth(3, 400)  # Значение
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.MultiSelection)

        # Стилизация таблицы
        self.results_table.setStyleSheet("""
                   QTableWidget {
                       background-color: #121212;
                       gridline-color: #2d2d2d;
                       color: #ffffff;
                   }
                   QTableWidget::item {
                       padding: 5px;
                   }
                   QHeaderView::section {
                       background-color: #141414;
                       color: white;
                       padding: 5px;
                       border: 1px solid #2d2d2d;
                   }
                   QTableWidget::item:selected {
                       background-color: #2980b9;
                   }
               """)
        layout.addWidget(self.results_table)
        self.setLayout(layout)

        # Стилизация
        self.setStyleSheet("""
                    QWidget {
                        background-color: #121212;
                        border-radius: 5px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton {
                        background-color: #2C3E50;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                        margin: 0 2px;  /* Added margin between buttons */
                    }
                    QPushButton:disabled {
                        background-color: #95a5a6;
                    }
                    QPushButton:hover {
                        background-color: #34495e;
                    }
                    QTableWidget {
                        border: 1px solid #2d2d2d;
                        gridline-color: #2d2d2d;
                    }
                    QHeaderView::section {
                        background-color: #2C3E50;
                        color: white;
                        padding: 5px;
                    }
                    QComboBox {
                        border: 1px solid #bdc3c7;
                        border-radius: 3px;
                        padding: 5px;
                    }
                """)

    def select_all_items(self):
        """Переключает выбор всех строк в таблице результатов."""
        if self.results_table.selectedItems():
            self.results_table.clearSelection()
            self.select_all_button.setText("Выбрать все")
        else:
            self.results_table.selectAll()
            self.select_all_button.setText("Отменить выбор")

    def create_registry_backup(self):
        """Создает резервную копию реестра Windows в выбранном пользователем месте."""
        try:
            # Получаем путь к рабочему столу пользователя
            default_path = os.path.join(os.getenv('USERPROFILE'), 'Desktop')

            # Генерируем имя файла с текущей датой и временем
            default_filename = f'registry_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.reg'

            # Открываем диалог выбора файла
            backup_file, _ = QFileDialog.getSaveFileName(
                self,
                "Выберите место для сохранения резервной копии реестра",
                os.path.join(default_path, default_filename),
                "Registry Files (*.reg)"
            )

            if backup_file:
                self.backup_thread = BackupThread(backup_file)
                self.backup_thread.backup_completed.connect(self.on_backup_completed)
                self.backup_thread.start()

                # Отключаем кнопку на время создания копии
                self.backup_button.setEnabled(False)
                self.backup_button.setText("Создание копии...")

        except Exception as e:
            logging.error(f"Ошибка при создании резервной копии: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию: {str(e)}")

    def on_backup_completed(self, success, message):
        self.backup_button.setEnabled(True)
        self.backup_button.setText("Создать копию реестра")

        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)

    def start_scan(self):
        self.results_table.setRowCount(0)
        self.problems.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.select_all_button.setEnabled(False)

        severity_map = {
            0: ProblemSeverity.CRITICAL,
            1: ProblemSeverity.HIGH,
            2: ProblemSeverity.LOW
        }
        min_severity = severity_map[self.severity_combo.currentIndex()]

        self.scan_thread = ScanThread(min_severity)
        self.scan_thread.problem_found.connect(self.add_problem)
        self.scan_thread.progress_update.connect(self.update_progress)
        self.scan_thread.scan_completed.connect(self.scan_completed)
        self.scan_thread.start()

    def update_progress(self, value):
        current_value = self.progress_bar.value()
        self.progress_bar.setValue(current_value + value)

    def add_problem(self, hive, path, name, value, severity):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        self.results_table.setItem(row, 0, QTableWidgetItem(hive))
        self.results_table.setItem(row, 1, QTableWidgetItem(path))
        self.results_table.setItem(row, 2, QTableWidgetItem(name))
        self.results_table.setItem(row, 3, QTableWidgetItem(value))

        # Сохраняем проблему в списке
        self.problems.append((hive, path, name, value, severity))

    def scan_completed(self):
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)
        self.select_all_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Сканирование завершено",
                                f"Найдено проблем: {len(self.problems)}")

    def clean_selected(self):
        selected_rows = set(item.row() for item in self.results_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите записи для очистки")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить выбранные записи?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            scanner = RegistryScanner()
            removed = 0

            for row in sorted(selected_rows, reverse=True):
                hive_name, path, name, _, _ = self.problems[row]
                hive = winreg.HKEY_LOCAL_MACHINE if hive_name == "HKEY_LOCAL_MACHINE" else winreg.HKEY_CURRENT_USER

                if scanner.delete_value(hive, path, name):
                    self.results_table.removeRow(row)
                    del self.problems[row]
                    removed += 1

            QMessageBox.information(self, "Очистка завершена",
                                    f"Успешно удалено записей: {removed}")