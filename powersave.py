from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QFrame, QHBoxLayout, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os
import json

# Путь к файлу настроек
SETTINGS_FILE = "source/power_settings.json"


class PowerWorker(QThread):
    result = pyqtSignal(str, bool)

    def __init__(self, action, scheme_guid=None, scheme_name=None):
        super().__init__()
        self.action = action
        self.scheme_guid = scheme_guid
        self.scheme_name = scheme_name

    def run(self):
        success = False
        message = ""

        try:
            if self.action == "unlock_hidden":
                subprocess.run(['powercfg', '-duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'],
                               check=True, capture_output=True)
                message = "Скрытая схема разблокирована"
                success = True

            elif self.action == "set_scheme" and self.scheme_guid:
                subprocess.run(['powercfg', '/setactive', self.scheme_guid], check=True)
                message = f"Активирована схема: {self.scheme_name}" if self.scheme_name else "Схема активирована"
                success = True

            elif self.action == "disable_hibernate":
                subprocess.run(['powercfg', '/hibernate', 'off'], check=True, capture_output=True)
                message = "Гибернация отключена"
                success = True

            elif self.action == "disable_usb_suspend":
                subprocess.run(
                    ['powercfg', '/SETACVALUEINDEX', 'SCHEME_CURRENT', '2a737441-1930-4402-8d77-b644a9c36b3c',
                     '0012ee47-9041-4b5d-9b77-535fba8b1442', '0'], check=True)
                subprocess.run(
                    ['powercfg', '/SETDCVALUEINDEX', 'SCHEME_CURRENT', '2a737441-1930-4402-8d77-b644a9c36b3c',
                     '0012ee47-9041-4b5d-9b77-535fba8b1442', '0'], check=True)
                subprocess.run(['powercfg', '-S', 'SCHEME_CURRENT'], check=True)
                message = "USB Selective Suspend отключен"
                success = True

            elif self.action == "disable_cstates":
                subprocess.run(['powercfg', '/SETACVALUEINDEX', 'SCHEME_CURRENT', 'SUB_PROCESSOR',
                                '5d76a2ca-e8c0-402f-a133-2158492d58ad', '0'],
                               check=True)
                subprocess.run(['powercfg', '/SETDCVALUEINDEX', 'SCHEME_CURRENT', 'SUB_PROCESSOR',
                                '5d76a2ca-e8c0-402f-a133-2158492d58ad', '0'],
                               check=True)
                subprocess.run(['powercfg', '-S', 'SCHEME_CURRENT'], check=True)
                message = "C-States отключены"
                success = True

            elif self.action == "disable_pcie":
                subprocess.run(['powercfg', '/SETACVALUEINDEX', 'SCHEME_CURRENT', 'SUB_PCIEXPRESS',
                                '501a4d13-42af-4429-9fd1-a8218c792e20',
                                '0'], check=True)
                subprocess.run(['powercfg', '/SETDCVALUEINDEX', 'SCHEME_CURRENT', 'SUB_PCIEXPRESS',
                                '501a4d13-42af-4429-9fd1-a8218c792e20',
                                '0'], check=True)
                subprocess.run(['powercfg', '-S', 'SCHEME_CURRENT'], check=True)
                message = "Энергосбережение PCIe отключено"
                success = True

        except subprocess.CalledProcessError as e:
            message = f"Ошибка: {str(e)}"
            success = False

        self.result.emit(message, success)


class PowerWidget(QFrame):
    def __init__(self, action_type, title, description, impact, safety):
        super().__init__()
        self.worker = None
        self.action_type = action_type
        self.expanded = False
        self.pow_file = None

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame { 
                background-color: #292929; 
                border: 1px solid #2d2d2d; 
                border-radius: 5px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #333333;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        header_layout = QHBoxLayout()

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #cccccc;
        """)

        self.status_label = QLabel("Не задано")
        self.status_label.setStyleSheet("font-size: 12px; color: white; font-weight: bold;")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        self.main_layout.addLayout(header_layout)

        self.details_widget = QWidget()
        self.details_widget.setStyleSheet("background-color: transparent")
        self.details_layout = QVBoxLayout(self.details_widget)

        info_widget = QWidget()
        info_widget.setStyleSheet("margin: 0,10,0,0; border: 1px solid #1e1e1e;")
        info_layout = QVBoxLayout(info_widget)

        desc_label = QLabel(f'<span style="color:#4D90D5; font-size: 12px;">Описание</span>: {description}')
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(desc_label)

        impact_label = QLabel(f'<span style="color:#FFA500; font-size: 12px;">Эффект</span>: {impact}')
        impact_label.setWordWrap(True)
        impact_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(impact_label)

        safety_label = QLabel(f'<span style="color:#32CD32; font-size: 12px;">Безопасность</span>: {safety}')
        safety_label.setWordWrap(True)
        safety_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(safety_label)

        self.details_layout.addWidget(info_widget)

        # Специальная обработка для выбора схемы
        if action_type == "set_scheme":
            button_layout = QHBoxLayout()

            self.balanced_btn = QPushButton("Сбалансированная")
            self.power_saver_btn = QPushButton("Экономия энергии")
            self.high_perf_btn = QPushButton("Высокая производительность")
            self.ultimate_btn = QPushButton("Максимальная производительность")

            buttons = [self.balanced_btn, self.power_saver_btn, self.high_perf_btn, self.ultimate_btn]
            for btn in buttons:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        font-weight: bold;
                        background-color: #1e8449;
                        border: 1px solid #1e8449;
                        padding: 5px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #196f3e;
                    }
                    QPushButton:disabled {
                        background-color: #666666;
                    }
                """)
                button_layout.addWidget(btn)

            self.balanced_btn.clicked.connect(
                lambda: self.start_action("381b4222-f694-41f0-9685-ff5bb260df2e", "Сбалансированная"))
            self.power_saver_btn.clicked.connect(
                lambda: self.start_action("a1841308-3541-4fab-bc81-f71556f20b4a", "Экономия энергии"))
            self.high_perf_btn.clicked.connect(
                lambda: self.start_action("8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "Высокая производительность"))
            self.ultimate_btn.clicked.connect(
                lambda: self.start_action("e9a42b02-d5df-448d-aa00-03f14749eb61", "Максимальная производительность"))

            self.details_layout.addLayout(button_layout)
        else:
            self.action_button = QPushButton("Выполнить")
            self.action_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    background-color: #1e8449;
                    border: 1px solid #1e8449;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #196f3e;
                }
                QPushButton:disabled {
                    background-color: #666666;
                }
            """)
            if action_type == "import_pow":
                self.action_button.setText("Импортировать .pow")
            self.action_button.clicked.connect(self.start_action)
            self.details_layout.addWidget(self.action_button)

        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)
        self.setCursor(Qt.PointingHandCursor)

        # Загрузка сохраненного статуса
        self.load_status()

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.details_widget.setVisible(self.expanded)

    def start_action(self, scheme_guid=None, scheme_name=None):
        if self.action_type == "set_scheme" and scheme_guid:
            for btn in [self.balanced_btn, self.power_saver_btn, self.high_perf_btn, self.ultimate_btn]:
                btn.setEnabled(False)
            self.status_label.setText("Активация схемы...")
            self.worker = PowerWorker("set_scheme", scheme_guid, scheme_name)
            self.worker.result.connect(self.action_finished)
            self.worker.start()

        elif self.action_type == "import_pow":
            self.action_button.setEnabled(False)
            self.pow_file, _ = QFileDialog.getOpenFileName(self, "Выберите .pow файл", "", "Power Scheme Files (*.pow)")
            if self.pow_file:
                try:
                    subprocess.run(['powercfg', '-import', self.pow_file], check=True)
                    self.status_label.setText(f"Импортировано: {os.path.basename(self.pow_file)}")
                    self.save_status(f"Импортировано: {os.path.basename(self.pow_file)}")
                except subprocess.CalledProcessError as e:
                    self.status_label.setText(f"Ошибка импорта: {str(e)}")
                    self.save_status(f"Ошибка импорта: {str(e)}")
            else:
                self.status_label.setText("Импорт отменен")
                self.save_status("Импорт отменен")
            self.action_button.setEnabled(True)

        else:
            self.action_button.setEnabled(False)
            self.status_label.setText("Выполняется...")
            self.worker = PowerWorker(self.action_type)
            self.worker.result.connect(self.action_finished)
            self.worker.start()

    def action_finished(self, message, success):
        self.status_label.setText(message)
        self.save_status(message)
        if self.action_type == "set_scheme":
            for btn in [self.balanced_btn, self.power_saver_btn, self.high_perf_btn, self.ultimate_btn]:
                btn.setEnabled(True)
        else:
            self.action_button.setEnabled(True)

    def save_status(self, status):
        """Сохранение статуса в файл"""
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)

        settings[self.action_type] = status
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    def load_status(self):
        """Загрузка сохраненного статуса"""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if self.action_type in settings:
                    self.status_label.setText(settings[self.action_type])


class PowerSavePage(QWidget):
    def __init__(self):
        super().__init__()
        self.admin_warning = None
        self.power_layout = None
        self.init_ui()
        self.setStyleSheet("background-color: #121212; border-radius: 5px;")

    def init_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
        """)

        container = QWidget()
        self.power_layout = QVBoxLayout(container)

        power_options = [
            {
                'type': 'unlock_hidden',
                'title': 'Разблокировать скрытую схему',
                'description': 'Разблокирует схему "Максимальная производительность"',
                'impact': 'Доступ к максимальной производительности системы',
                'safety': 'Безопасно'
            },
            {
                'type': 'set_scheme',
                'title': 'Выбрать схему питания',
                'description': 'Позволяет выбрать активную схему электропитания. Примечание: на некоторых устройствах схема "Максимальная производительность" может не отображаться',
                'impact': 'Изменение параметров энергопотребления',
                'safety': 'Безопасно'
            },
            {
                'type': 'import_pow',
                'title': 'Импорт .pow файла',
                'description': 'Импорт пользовательской схемы питания из файла. Готовые схемы электропитания в папке с программой',
                'impact': 'Добавление новой схемы питания',
                'safety': 'Безопасно при использовании проверенных файлов'
            },
            {
                'type': 'disable_hibernate',
                'title': 'Отключить гибернацию',
                'description': 'Отключает функцию гибернации Windows',
                'impact': 'Освобождение места на диске, отключение режима сна, может замедлить запуск системы',
                'safety': 'Безопасно'
            },
            {
                'type': 'disable_usb_suspend',
                'title': 'Отключить USB Selective Suspend',
                'description': 'Предотвращает отключение USB устройств для экономии энергии',
                'impact': 'Стабильная работа USB устройств',
                'safety': 'Безопасно, повышает энергопотребление'
            },
            {
                'type': 'disable_cstates',
                'title': 'Отключить C-States процессора',
                'description': 'Отключает энергосберегающие состояния процессора',
                'impact': 'Повышение производительности за счет увеличения потребления',
                'safety': 'Относительно безопасно. Увеличивает энергопотребление и тепловыделение, соответственно, возможно уменьшение срока службы процессора. Применять на свой страх и риск'
            },
            {
                'type': 'disable_pcie',
                'title': 'Отключить энергосбережение PCIe',
                'description': 'Отключает энергосбережение для PCIe устройств',
                'impact': 'Повышение производительности PCIe устройств',
                'safety': 'Относительно безопасно. Увеличивает энергопотребление и тепловыделение, соответственно, возможно уменьшение срока службы устройств. Применять на свой страх и риск'
            }
        ]

        for option in power_options:
            widget = PowerWidget(
                option['type'],
                option['title'],
                option['description'],
                option['impact'],
                option['safety']
            )
            self.power_layout.addWidget(widget)

        self.power_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
