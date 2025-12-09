from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QScrollArea, QPushButton, QLabel, QMessageBox, QFrame,
                             QHBoxLayout, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
import win32serviceutil
import win32service


class ServiceDescription:
    def __init__(self, description="", impact="", safety=""):
        self.description = description
        self.impact = impact
        self.safety = safety


def parse_services_list(content):
    services = {}
    for line in content.split('\n'):
        if line.strip():
            parts = line.split(',')
            if len(parts) == 2:
                services[parts[1].strip()] = parts[0].strip()
    return services


def parse_descriptions(content):
    descriptions = {}
    current_service = None
    current_desc = {"description": "", "impact": "", "safety": ""}

    for line in content.split('\n'):
        if line.strip():
            if line[0].isdigit():  # New service entry
                if current_service:
                    descriptions[current_service] = ServiceDescription(
                        current_desc["description"],
                        current_desc["impact"],
                        current_desc["safety"]
                    )
                service_info = line.split('(')
                if len(service_info) > 1:
                    current_service = service_info[1].split(')')[0].strip()
                    current_desc = {"description": "", "impact": "", "safety": ""}
            elif line.startswith('•'):
                line = line.strip('•').strip()
                if line.startswith('Описание:'):
                    current_desc["description"] = line.replace('Описание:', '').strip()
                elif line.startswith('Если отключить:'):
                    current_desc["impact"] = line.replace('Если отключить:', '').strip()
                elif line.startswith('Безопасно ли это:'):
                    current_desc["safety"] = line.replace('Безопасно ли это:', '').strip()

    if current_service:
        descriptions[current_service] = ServiceDescription(
            current_desc["description"],
            current_desc["impact"],
            current_desc["safety"]
        )
    return descriptions


def get_service_startup_type(service_name):
    try:
        scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        service_handle = win32service.OpenService(scm, service_name, win32service.SERVICE_QUERY_CONFIG)

        config = win32service.QueryServiceConfig(service_handle)
        startup_type = config[1]  # Индекс 1 содержит тип запуска

        startup_map = {
            win32service.SERVICE_AUTO_START: "Автоматически",
            win32service.SERVICE_DEMAND_START: "Вручную",
            win32service.SERVICE_DISABLED: "Отключена",
            0x2: "Автоматически (отложенный запуск)"  # SERVICE_AUTO_START | SERVICE_DELAYED_AUTO_START
        }

        win32service.CloseServiceHandle(service_handle)
        win32service.CloseServiceHandle(scm)

        return startup_map.get(startup_type, "Неизвестно")
    except:
        return "Неизвестно"


def get_service_state(service_name):
    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        state_map = {
            win32service.SERVICE_RUNNING: "Выполняется",
            win32service.SERVICE_STOPPED: "Остановлена"
        }
        return state_map.get(status, "Неизвестно")
    except:
        return "Неизвестно"


class ServiceWidget(QFrame):
    def __init__(self, service_name, display_name="", is_optimal=False, service_desc=None, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.display_name = display_name or service_name
        self.is_optimal = is_optimal
        self.service_desc = service_desc
        self.setFrameShape(QFrame.StyledPanel)
        self.expanded = False

        # Базовый стиль для всего виджета
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

        # Создаем контейнер для заголовка
        self.header_container = QFrame(self)
        self.header_container.setStyleSheet("""
                    QFrame { 
                        background-color: transparent; 
                        border: none;
                        border-radius: 5px;
                    }
                """)

        # Header layout
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.display_name)
        self.name_label.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #cccccc;""")

        header_layout.addWidget(self.name_label)
        header_layout.addStretch()

        # Status layout
        status_layout = QVBoxLayout()

        # Startup Type
        self.startup_type_label = QLabel()
        self.startup_type_label.setStyleSheet("font-size: 11px; color: white; font-weight: bold;")

        # Service State
        self.state_label = QLabel()
        self.state_label.setStyleSheet("font-size: 11px; color: white; font-weight: bold;")

        status_layout.addWidget(self.startup_type_label)
        status_layout.addWidget(self.state_label)

        header_layout.addLayout(status_layout)

        # Добавляем контейнер заголовка в основной layout
        self.main_layout.addWidget(self.header_container)

        # Если это оптимальный сервис, добавляем зеленую полосу слева
        if self.is_optimal:
            self.setStyleSheet("""
                        QFrame { 
                            background-color: #292929; 
                            border: 1px solid #292929; 
                            border-radius: 5px; 
                            border-left: 6px solid #1e8449;
                            margin: 2px;
                        }
                        QFrame:hover {
                            background-color: #333333;
                        }
                    """)

        # Обновляем информацию о службе
        self.update_service_info()

        # Details widget setup
        self.details_widget = QWidget()
        self.details_widget.setStyleSheet("background-color: transparent")
        self.details_layout = QVBoxLayout(self.details_widget)

        if self.service_desc:
            desc_widget = QWidget()
            desc_widget.setStyleSheet("margin: 0,10,0,0; border: 1px solid #1e1e1e;")
            desc_layout = QVBoxLayout(desc_widget)

            if self.service_desc.description:
                desc_label = QLabel(f'''
                    <span style="color:#4D90D5; font-size: 12px;">Описание</span>: {self.service_desc.description}''')
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("""
                    color: white; font-size: 12px; font-weight: bold; border: none;""")
                desc_layout.addWidget(desc_label)

            if self.service_desc.impact:
                impact_label = QLabel(
                    f'''<span style="color:#FFA500; 
                    font-size: 12px;">Если отключить</span>: {self.service_desc.impact}''')
                impact_label.setWordWrap(True)
                impact_label.setStyleSheet("""
                    color: white; font-size: 12px; font-weight: bold; border: none;""")
                desc_layout.addWidget(impact_label)

            if self.service_desc.safety:
                safety_label = QLabel(f'''
                    <span style="color:#32CD32; font-size: 12px;">Безопасность</span>: {self.service_desc.safety}''')
                safety_label.setWordWrap(True)
                safety_label.setStyleSheet("""
                    color: white; font-size: 12px; font-weight: bold; border: none;""")
                desc_layout.addWidget(safety_label)

            self.details_layout.addWidget(desc_widget)

        buttons_layout = QHBoxLayout()

        self.start_button = QPushButton("Запустить")
        self.stop_button = QPushButton("Остановить")
        self.disable_button = QPushButton("Отключить")
        self.auto_button = QPushButton("Автоматически")
        self.manual_button = QPushButton("Вручную")

        self.start_button.setStyleSheet("""
            QPushButton{
                color: #8ac44b;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;  
                border: 1px solid #8ac44b;
            }
            QPushButton:hover{
                border: 1px solid #70a636;
                color: #70a636;
            }
        """)
        self.stop_button.setStyleSheet("""
            QPushButton{
                color: #f8981d;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;
                border: 1px solid #f8981d;
            }
            QPushButton:hover{
                border: 1px solid #f8861d;
                color: #f8861d;
            }
        """)
        self.disable_button.setStyleSheet("""
            QPushButton{
                color: #f04438;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;
                border: 1px solid #f04438;
            }
            QPushButton:hover{
                border: 1px solid #ee2e20;
                color: #ee2e20;
            }
        """)
        self.auto_button.setStyleSheet("""
            QPushButton{
                color: #913e98;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;
                border: 1px solid #913e98;
            }
            QPushButton:hover{
                border: 1px solid #803786;
                color: #803786;
            }
        """)
        self.manual_button.setStyleSheet("""
            QPushButton{
                color: #478ecc;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;
                border: 1px solid #478ecc;
            }
            QPushButton:hover{
                border: 1px solid #3682c3;
                color: #3682c3;
            }
        """)

        for button in [self.start_button, self.stop_button, self.disable_button,
                       self.auto_button, self.manual_button]:
            buttons_layout.addWidget(button)

        self.details_layout.addLayout(buttons_layout)
        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)

        # Connect signals
        self.start_button.clicked.connect(self.start_service)
        self.stop_button.clicked.connect(self.stop_service)
        self.disable_button.clicked.connect(self.disable_service)
        self.auto_button.clicked.connect(lambda: self.change_startup_type(win32service.SERVICE_AUTO_START))
        self.manual_button.clicked.connect(lambda: self.change_startup_type(win32service.SERVICE_DEMAND_START))

        self.setCursor(Qt.PointingHandCursor)

    def update_service_info(self):
        startup_type = get_service_startup_type(self.service_name)
        state = get_service_state(self.service_name)

        self.startup_type_label.setText(f"Тип запуска: {startup_type}")
        self.state_label.setText(f"Состояние: {state}")

    def change_startup_type(self, startup_type):
        try:
            scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            service_handle = win32service.OpenService(scm, self.service_name, win32service.SERVICE_CHANGE_CONFIG)
            win32service.ChangeServiceConfig(
                service_handle,
                win32service.SERVICE_NO_CHANGE,
                startup_type,
                win32service.SERVICE_NO_CHANGE,
                None,
                None,
                False,
                None,
                None,
                None,
                None
            )
            win32service.CloseServiceHandle(service_handle)
            win32service.CloseServiceHandle(scm)
            QTimer.singleShot(1000, self.update_service_info)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось изменить тип запуска: {str(e)}")

    def disable_service(self):
        self.change_startup_type(win32service.SERVICE_DISABLED)
        QTimer.singleShot(1000, self.update_service_info)

    def start_service(self):
        try:
            win32serviceutil.StartService(self.service_name)
            QTimer.singleShot(1000, self.update_service_info)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось запустить службу: {str(e)}")

    def stop_service(self):
        try:
            win32serviceutil.StopService(self.service_name)
            QTimer.singleShot(1000, self.update_service_info)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось остановить службу: {str(e)}")

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.details_widget.setVisible(self.expanded)


class ServicesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border-radius: 5px;
            }
        """)

        # Load services list and descriptions
        self.optimal_services = parse_services_list(open('source/services_list.txt', encoding='utf-8').read())
        try:
            with open('source/service_description.txt', encoding='utf-8') as f:
                self.service_descriptions = parse_descriptions(f.read())
        except:
            self.service_descriptions = {}

        # Create search bar and button container
        self.top_container = QWidget()
        self.top_layout = QHBoxLayout(self.top_container)

        # Add search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск службы...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #292929;
                color: white;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
                margin-right: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #505050;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_services)

        self.highlight_button = QPushButton("Сначала оптимальные")
        self.highlight_button.setStyleSheet("""
            QPushButton {
                background-color: #1e8449;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229955;
            }
            QPushButton:pressed {
                background-color: #219A52;
            }
        """)
        self.highlight_button.clicked.connect(self.reorganize_services)

        # Add widgets to top layout
        self.top_layout.addWidget(self.search_bar, stretch=1)
        self.top_layout.addWidget(self.highlight_button)
        self.layout.addWidget(self.top_container)
        self.service_widgets = []

        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        # Container for services
        self.container = QWidget()
        self.services_layout = QVBoxLayout(self.container)
        self.load_services()

        self.services_layout.addStretch()
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

        # Store all service widgets for filtering

    def filter_services(self, text):
        search_text = text.lower()

        for widget in self.service_widgets:
            if isinstance(widget, ServiceWidget):
                matches = (search_text in widget.service_name.lower() or
                           search_text in widget.display_name.lower())
                widget.setVisible(matches)

    def load_services(self):
        try:
            scm = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ENUMERATE_SERVICE
            )

            services = win32service.EnumServicesStatus(
                scm,
                win32service.SERVICE_WIN32,
                win32service.SERVICE_STATE_ALL
            )

            for service in services:
                service_name = service[0]
                display_name = service[1]
                is_optimal = service_name in self.optimal_services
                service_desc = self.service_descriptions.get(service_name)

                service_widget = ServiceWidget(
                    service_name,
                    self.optimal_services.get(service_name, display_name),
                    is_optimal,
                    service_desc
                )
                self.services_layout.addWidget(service_widget)
                self.service_widgets.append(service_widget)  # Store widget reference

            win32service.CloseServiceHandle(scm)

        except Exception as e:
            error_message = QLabel(
                f"Ошибка при получении списка служб:\n{str(e)}\n\n"
                "Убедитесь, что программа запущена с правами администратора."
            )
            error_message.setStyleSheet("""
                QLabel {
                    color: #C0392B;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #FADBD8;
                    border: 1px solid #F5B7B1;
                    border-radius: 5px;
                }
            """)
            error_message.setWordWrap(True)
            self.services_layout.addWidget(error_message)

    def reorganize_services(self):
        # Clear service widgets list
        self.service_widgets.clear()

        # Remove all widgets except the stretch at the end
        while self.services_layout.count() > 1:
            item = self.services_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reload services with optimal ones first
        try:
            scm = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ENUMERATE_SERVICE
            )

            services = win32service.EnumServicesStatus(
                scm,
                win32service.SERVICE_WIN32,
                win32service.SERVICE_STATE_ALL
            )

            # Sort services - optimal first
            sorted_services = sorted(
                services,
                key=lambda x: (x[0] not in self.optimal_services, x[0].lower())
            )

            for service in sorted_services:
                service_name = service[0]
                display_name = service[1]
                is_optimal = service_name in self.optimal_services
                service_desc = self.service_descriptions.get(service_name)
                service_widget = ServiceWidget(
                    service_name,
                    self.optimal_services.get(service_name, display_name),
                    is_optimal,
                    service_desc
                )
                self.services_layout.insertWidget(self.services_layout.count() - 1, service_widget)
                self.service_widgets.append(service_widget)  # Store widget reference

            win32service.CloseServiceHandle(scm)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось перезагрузить список служб: {str(e)}")
