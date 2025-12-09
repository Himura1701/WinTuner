from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class AdminWarningWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        admin_layout = QVBoxLayout(self)
        admin_layout.setContentsMargins(0, 0, 0, 10)

        warning_label = QLabel(
            "Для выполнения этой операции требуются права администратора.\n"
            "Пожалуйста, запустите программу от имени администратора."
        )
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setStyleSheet("""
            QLabel {
                color: #D35400;
                font-size: 14px;
                padding: 20px;
                background-color: #121212;
                border: 1px solid;
                border-radius: 5px;
            }
        """)

        restart_btn = QPushButton("Перезапустить как администратор")
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #D35400;
            }
        """)
        restart_btn.clicked.connect(self.restart_as_admin)

        admin_layout.addWidget(warning_label)
        admin_layout.addWidget(restart_btn)

    @staticmethod
    def restart_as_admin():
        if sys.platform == 'win32':
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )
            sys.exit(0)
