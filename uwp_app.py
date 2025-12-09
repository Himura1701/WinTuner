from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QScrollArea, QFrame,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
import subprocess


class UWPAppDescription:
    def __init__(self, description="", safety=""):
        self.description = description
        self.safety = safety


def parse_uwp_descriptions(content):
    """
    Parse the UWP app descriptions from the text file
    """
    descriptions = {}
    current_app = None
    current_desc = {"description": "", "safety": ""}

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('Microsoft.'):
            # New app entry
            if current_app:
                descriptions[current_app] = UWPAppDescription(
                    current_desc["description"],
                    current_desc["safety"]
                )
                current_desc = {"description": "", "safety": ""}

            current_app = line
        elif line.startswith('- Описание:'):
            current_desc["description"] = line.replace('- Описание:', '').strip()
        elif line.startswith('- Безопасно ли удалять:'):
            current_desc["safety"] = line.replace('- Безопасно ли удалять:', '').strip()

    # Add the last app
    if current_app:
        descriptions[current_app] = UWPAppDescription(
            current_desc["description"],
            current_desc["safety"]
        )

    return descriptions


class UWPAppWidget(QFrame):
    def __init__(self, app_name, app_desc=None, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self.app_desc = app_desc
        self.expanded = False

        # Base styling for the widget
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

        # Header container
        self.header_container = QFrame(self)
        header_layout = QHBoxLayout(self.header_container)
        self.header_container.setStyleSheet("border: none; background-color: transparent;")

        # App name label
        self.name_label = QLabel(app_name)
        self.name_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #cccccc;
            border: none;
            background-color: transparent;
        """)
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()

        # Remove button
        self.remove_button = QPushButton("Удалить")
        self.remove_button.setStyleSheet("""
            QPushButton {
                color: #f04438;
                font-weight: bold;
                font-size: 13px;
                padding: 5px;
                border-radius: 5px;
                background-color: transparent;
                border: 1px solid #f04438;
            }
            QPushButton:hover {
                border: 1px solid #ee2e20;
                color: #ee2e20;
            }
        """)
        self.remove_button.clicked.connect(self.remove_app)
        header_layout.addWidget(self.remove_button)

        self.main_layout.addWidget(self.header_container)

        # Details widget
        if self.app_desc:
            details_widget = QWidget()
            details_layout = QVBoxLayout(details_widget)
            details_widget.setStyleSheet("""
                background-color: transparent; border: 1px solid #1e1e1e; margin: 5px; padding: 0px""")

            # Description section
            if self.app_desc.description:
                desc_label = QLabel(f'''
                    <span style="color:#4D90D5; font-size: 12px;">Описание</span>: {self.app_desc.description}''')
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("""
                    color: white; 
                    font-size: 12px; 
                    font-weight: bold; 
                    border: none;

                """)
                details_layout.addWidget(desc_label)

            # Safety section
            if self.app_desc.safety:
                safety_label = QLabel(f'''
                    <span style="color:#32CD32; font-size: 12px;">Безопасность</span>: {self.app_desc.safety}''')
                safety_label.setWordWrap(True)
                safety_label.setStyleSheet("""
                    color: white; 
                    font-size: 12px; 
                    font-weight: bold; 
                    border: none;
                """)
                details_layout.addWidget(safety_label)

            details_widget.hide()
            self.main_layout.addWidget(details_widget)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        # Toggle details visibility
        details_widget = self.main_layout.itemAt(1).widget() if self.main_layout.count() > 1 else None
        if details_widget:
            self.expanded = not self.expanded
            details_widget.setVisible(self.expanded)

    def remove_app(self):
        # Custom stylesheet for message boxes
        message_box_style = """
            QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #444444;
            }
            QMessageBox QPushButton:pressed {
                background-color: #555555;
            }
            QMessageBox QPushButton#qt_msgbox_yes_button {
                background-color: #f04438;
                color: white;
            }
            QMessageBox QPushButton#qt_msgbox_yes_button:hover {
                background-color: #ee2e20;
            }
            QMessageBox QPushButton#qt_msgbox_no_button {
                background-color: #333333;
                color: #ffffff;
            }
            QMessageBox QPushButton#qt_msgbox_no_button:hover {
                background-color: #444444;
            }
        """

        # Confirm removal
        msg_box = QMessageBox()
        msg_box.setStyleSheet(message_box_style)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Подтверждение удаления')
        msg_box.setText(f'Вы уверены, что хотите удалить приложение {self.app_name}?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            try:
                # Use PowerShell to remove the UWP app
                remove_command = f'Get-AppxPackage "{self.app_name}" -AllUsers | Remove-AppxPackage'
                subprocess.run(['powershell', '-Command', remove_command],
                               capture_output=True,
                               text=True,
                               check=True)

                # Success message
                success_msg = QMessageBox()
                success_msg.setStyleSheet(message_box_style)
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setWindowTitle('Успех')
                success_msg.setText(f'Приложение {self.app_name} было успешно удалено.')
                success_msg.exec_()

                # Hide the widget after successful removal
                self.setVisible(False)
            except subprocess.CalledProcessError as e:
                # Error message
                error_msg = QMessageBox()
                error_msg.setStyleSheet(message_box_style)
                error_msg.setIcon(QMessageBox.Warning)
                error_msg.setWindowTitle('Ошибка')
                error_msg.setText(f'Не удалось удалить приложение: {str(e)}')
                error_msg.exec_()


class UWPAppsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border-radius: 5px;
            }
        """)

        # Load UWP app descriptions
        try:
            with open('source/uwp_app_description.txt', encoding='utf-8') as f:
                self.uwp_descriptions = parse_uwp_descriptions(f.read())
        except Exception as e:
            print(f"Error loading UWP app descriptions: {e}")
            self.uwp_descriptions = {}

        # Add search bar
        self.top_container = QWidget()
        self.top_layout = QHBoxLayout(self.top_container)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск UWP приложения...")
        self.search_bar.setStyleSheet("""
                        QLineEdit {
                            background-color: #292929;
                            color: white;
                            border: 1px solid #404040;
                            border-radius: 3px;
                            padding: 5px;
                            font-size: 14px;
                        }
                        QLineEdit:focus {
                            border: 1px solid #505050;
                        }
                    """)
        self.search_bar.textChanged.connect(self.filter_apps)

        self.top_layout.addWidget(self.search_bar)
        self.layout.addWidget(self.top_container)
        self.app_widgets = []


        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        # Container for UWP apps
        self.container = QWidget()
        self.apps_layout = QVBoxLayout(self.container)
        self.load_uwp_apps()

        self.apps_layout.addStretch()
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def load_uwp_apps(self):
        # Load UWP apps and create widgets only for installed apps
        try:
            # Run PowerShell command to get list of installed UWP apps
            result = subprocess.run(
                ['powershell', '-Command', 'Get-AppxPackage | Select-Object Name'],
                capture_output=True,
                text=True,
                check=True
            )

            # Extract installed app names
            installed_apps = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            # Filter and create widgets only for installed apps
            for app_name, app_desc in self.uwp_descriptions.items():
                # Check if the full package name exists in the installed apps list
                if any(app_name in installed_app for installed_app in installed_apps):
                    uwp_app_widget = UWPAppWidget(app_name, app_desc)
                    self.apps_layout.addWidget(uwp_app_widget)
                    self.app_widgets.append(uwp_app_widget)

        except subprocess.CalledProcessError as e:
            print(f"Error retrieving installed UWP apps: {e}")

    def filter_apps(self, text):
        search_text = text.lower()

        try:
            # Get currently installed UWP apps
            result = subprocess.run(
                ['powershell', '-Command', 'Get-AppxPackage | Select-Object Name'],
                capture_output=True,
                text=True,
                check=True
            )

            # Extract installed app names
            installed_apps = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            # Filter widgets
            for widget in self.app_widgets:
                # Check two conditions:
                # 1. Search text matches the app name
                # 2. App is actually installed
                matches = (search_text in widget.app_name.lower() and
                           any(widget.app_name in installed_app for installed_app in installed_apps))

                widget.setVisible(matches)

        except subprocess.CalledProcessError as e:
            print(f"Error retrieving installed UWP apps during search: {e}")
            # Fallback to basic search if PowerShell command fails
            for widget in self.app_widgets:
                widget.setVisible(search_text in widget.app_name.lower())
