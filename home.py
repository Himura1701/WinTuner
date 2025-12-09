from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ASCII Art
        ascii_art = r"""
 __      __                     ______                                    
/\ \  __/\ \    __             /\__  _\                                   
\ \ \/\ \ \ \  /\_\     ___    \/_/\ \/   __  __    ___       __    _ __  
 \ \ \ \ \ \ \ \/\ \  /' _ `\     \ \ \  /\ \/\ \ /' _ `\   /'__`\ /\`'__\
  \ \ \_/ \_\ \ \ \ \ /\ \/\ \     \ \ \ \ \ \_\ \/\ \/\ \ /\  __/ \ \ \/ 
   \ `\___x___/  \ \_\\ \_\ \_\     \ \_\ \ \____/\ \_\ \_\\ \____\ \ \_\ 
    '\/__//__/    \/_/ \/_/\/_/      \/_/  \/___/  \/_/\/_/ \/____/  \/_/ 
               """

        # Main layout
        layout = QVBoxLayout()

        # ASCII Art Label with HTML pre-formatting
        ascii_art_label = QLabel(
            f'<pre style="font-family: \'Courier New\', monospace; background-color: black; font-weight: bold; font-size: 16px; color: #2C3E50; text-align: center;">{ascii_art}</pre>')
        ascii_art_label.setAlignment(Qt.AlignCenter)

        # Alert Label
        alert_label = QLabel("Примечание: перед использованием данной программы обязательно создайте точку востановления!\n"+
                             "Автор программы не несет никакой ответственности за любые убытки, вызванные использованием данной программы.")
        alert_label.setAlignment(Qt.AlignCenter)
        alert_label.setStyleSheet("color: #2C3E50; font-weight: bold; margin-top: 20px; font-size: 10px; background-color: black;")

        version_label = QLabel("Alpha Version 1.0 by Himura")
        version_label.setFont(QFont('Arial', 7))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #2C3E50; font-weight: bold; margin-top: 20px; background-color: black;")

        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(ascii_art_label)
        layout.addWidget(alert_label)
        layout.addWidget(version_label)
        layout.addStretch(1)

        # Set layout
        self.setLayout(layout)

        # Style the page
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)