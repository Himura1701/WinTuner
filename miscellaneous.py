from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os
import winreg
import json


# Путь для сохранения статуса
STATUS_FILE = "source/misc_status.json"


class ModifierWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, mod_type, revert=False):
        super().__init__()
        self.mod_type = mod_type
        self.revert = revert

    def run(self):
        try:
            if self.mod_type == "fso":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "GameDVR_FSEBehavior", 0, winreg.REG_DWORD, 0)
                else:
                    winreg.SetValueEx(key, "GameDVR_FSEBehavior", 0, winreg.REG_DWORD, 2)
                winreg.CloseKey(key)

            elif self.mod_type == "mpo":
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm", 0,
                                     winreg.KEY_SET_VALUE)
                if self.revert:
                    try:
                        winreg.DeleteValue(key, "OverlayTestMode")
                    except FileNotFoundError:
                        pass
                else:
                    winreg.SetValueEx(key, "OverlayTestMode", 0, winreg.REG_DWORD, 5)
                winreg.CloseKey(key)

            elif self.mod_type == "mouse_acc":
                if self.revert:
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 1 /f', shell=True,
                                   check=True)
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d 6 /f',
                                   shell=True, check=True)
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d 10 /f',
                                   shell=True, check=True)
                else:
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 0 /f', shell=True,
                                   check=True)
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d 0 /f',
                                   shell=True, check=True)
                    subprocess.run('REG add "HKCU\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d 0 /f',
                                   shell=True, check=True)

            elif self.mod_type == "gamemode":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", 0, winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 0)
                else:
                    winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)

            elif self.mod_type == "gpu_scheduling":
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 0,
                                     winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 1)
                else:
                    winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)
                winreg.CloseKey(key)

            elif self.mod_type == "core_isolation":
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity",
                                     0, winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 1)
                else:
                    winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)

            elif self.mod_type == "hpet":
                if self.revert:
                    subprocess.run('bcdedit /set useplatformclock true', shell=True, check=True)
                else:
                    subprocess.run('bcdedit /set useplatformclock false', shell=True, check=True)

            elif self.mod_type == "sticky_keys":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Accessibility\StickyKeys", 0,
                                     winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "510")
                else:
                    winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "506")
                winreg.CloseKey(key)

            elif self.mod_type == "firewall":
                if self.revert:
                    subprocess.run('netsh advfirewall set allprofiles state on', shell=True, check=True)
                else:
                    subprocess.run('netsh advfirewall set allprofiles state off', shell=True, check=True)

            elif self.mod_type == "scaling":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "LogPixels", 0, winreg.REG_DWORD, 96)
                else:
                    winreg.SetValueEx(key, "LogPixels", 0, winreg.REG_DWORD, 96)
                winreg.CloseKey(key)

            elif self.mod_type == "background_apps":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", 0,
                                     winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 0)
                else:
                    winreg.SetValueEx(key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)

            elif self.mod_type == "performance":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 0,
                                     winreg.KEY_SET_VALUE)
                if self.revert:
                    winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 1)
                else:
                    winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
                winreg.CloseKey(key)

            elif self.mod_type == "defender":
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender", 0,
                                         winreg.KEY_SET_VALUE)
                except FileNotFoundError:
                    winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender")
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender", 0,
                                         winreg.KEY_SET_VALUE)
                if self.revert:
                    try:
                        winreg.DeleteValue(key, "DisableAntiSpyware")
                    except FileNotFoundError:
                        pass
                else:
                    winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)

            elif self.mod_type == "spectre_meltdown":
                if self.revert:
                    subprocess.run(
                        'REG delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverride /f',
                        shell=True, check=True)
                    subprocess.run(
                        'REG delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverrideMask /f',
                        shell=True, check=True)
                else:
                    subprocess.run(
                        'REG add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverride /t REG_DWORD /d 3 /f',
                        shell=True, check=True)
                    subprocess.run(
                        'REG add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v FeatureSettingsOverrideMask /t REG_DWORD /d 3 /f',
                        shell=True, check=True)

            elif self.mod_type == "trim":
                if self.revert:
                    subprocess.run('fsutil behavior set DisableDeleteNotify 0', shell=True, check=True)
                else:
                    subprocess.run('fsutil behavior set DisableDeleteNotify 1', shell=True, check=True)

            self.finished.emit(f"{self.mod_type} {'reverted' if self.revert else 'applied'} successfully")
        except Exception as e:
            self.finished.emit(f"Error in {self.mod_type}: {str(e)}")


class ModifierWidget(QFrame):
    def __init__(self, mod_type, title, description, impact, safety):
        super().__init__()
        self.mod_type = mod_type
        self.worker = None
        self.is_applied = self.load_status()

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
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
        self.status_label = QLabel("Применено" if self.is_applied else "Не задано")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #90EE90;  
        """)
        if not self.is_applied:
            self.status_label.setStyleSheet("""
                font-size: 12px;
                font-weight: bold;
                color: #FF6B6B;  
            """)
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

        self.button = QPushButton("Вернуть стандартное значение" if self.is_applied else "Применить")
        self.update_button_style()
        self.button.clicked.connect(self.start_modification)
        self.details_layout.addWidget(self.button)

        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.details_widget.setVisible(not self.details_widget.isVisible())

    def load_status(self):
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    status = json.load(f)
                    return status.get(self.mod_type, False)
        except:
            pass
        return False

    def save_status(self, applied):
        status = {}
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                status = json.load(f)
        status[self.mod_type] = applied
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f)

    def start_modification(self):
        self.button.setEnabled(False)
        self.status_label.setText("Применение..." if not self.is_applied else "Восстановление...")

        self.worker = ModifierWorker(self.mod_type, revert=self.is_applied)
        self.worker.finished.connect(self.modification_finished)
        self.worker.start()

    def update_button_style(self):
        if self.button.text() == "Применить":
            self.button.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 5px;
                    background-color: #1e8449;
                    border: 1px solid #1e8449;
                }
                QPushButton:hover {
                    background-color: #196f3e;
                }
                QPushButton:pressed {
                    background-color: #219A52;
                }
                QPushButton:disabled {
                    background-color: #666666;
                }
            """)
        else:
            self.button.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 5px;
                    background-color: #d32f2f;
                    border: 1px solid #d32f2f;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
                QPushButton:pressed {
                    background-color: #f44336;
                }
                QPushButton:disabled {
                    background-color: #666666;
                }
            """)

    def modification_finished(self, message):
        self.button.setEnabled(True)
        if "successfully" in message:
            self.is_applied = not self.is_applied
            self.save_status(self.is_applied)
            self.button.setText("Вернуть стандартное значение" if self.is_applied else "Применить")
            self.update_button_style()
            self.status_label.setText("Применено" if self.is_applied else "Не задано")
            self.status_label.setStyleSheet("""
                font-size: 12px;
                font-weight: bold;
                color: #90EE90;
            """ if self.is_applied else """
                font-size: 12px;
                font-weight: bold;
                color: #FF6B6B;
            """)
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("""
                font-size: 12px;
                font-weight: bold;
                color: #FF6B6B;
            """)


class MiscellaneousPage(QWidget):
    def __init__(self):
        super().__init__()
        self.admin_warning = None
        self.init_ui()
        self.setStyleSheet("background-color: #121212; border-radius: 5px;")

    def init_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #121212; }")

        container = QWidget()
        self.misc_layout = QVBoxLayout(container)

        # Добавляем виджет для создания точки восстановления
        restore_point_widget = self.create_restore_point_widget()
        self.misc_layout.addWidget(restore_point_widget)

        modifiers = [
            {"type": "fso", "title": "Отключить FSO",
            "description": "Отключает полноэкранные оптимизации Windows, которые могут вызывать проблемы совместимости в некоторых старых играх и приложениях.",
            "impact": "Улучшает совместимость старых игр, может устранить мерцание экрана или проблемы с производительностью.",
            "safety": "Безопасно для большинства систем, не влияет на современные приложения."},
            {"type": "mpo", "title": "Отключить MPO",
             "description": "Отключает Multi Plane Overlay, технологию обработки графики, которая может вызывать задержки или артефакты в играх.",
             "impact": "Уменьшает лаги и графические ошибки в играх, особенно на системах с несколькими мониторами.",
             "safety": "Безопасно, но может повлиять на некоторые функции отображения."},
            {"type": "mouse_acc", "title": "Отключить акселерацию мыши",
             "description": "Убирает ускорение мыши (повышенную точность установки указателя), делая движение курсора более предсказуемым.",
             "impact": "Улучшает точность управления в играх и графических приложениях, устраняет неравномерность движения.",
             "safety": "Безопасно, предпочтительно для геймеров."},
            {"type": "gamemode", "title": "Включить Game Mode",
             "description": "Активирует игровой режим Windows, оптимизирующий распределение ресурсов для повышения производительности в играх.",
             "impact": "Увеличивает FPS и стабильность в играх за счет приоритета игровых процессов.",
             "safety": "Безопасно, встроенная функция Windows."},
            {"type": "gpu_scheduling", "title": "Аппаратное ускорение GPU",
             "description": "Включает аппаратно-ускоренное планирование GPU, позволяя видеокарте самостоятельно управлять своей памятью.",
             "impact": "Снижает нагрузку на CPU, улучшает производительность графики в современных играх.",
             "safety": "Безопасно на совместимом оборудовании (Windows 10 2004 и новее)."},
            {"type": "core_isolation", "title": "Отключить изоляцию ядра",
             "description": "Деактивирует функцию изоляции ядра (целостность памяти), которая защищает систему от вредоносных атак на уровне памяти.",
             "impact": "Незначительно повышает производительность за счет снижения накладных расходов.",
             "safety": "Снижает уровень защиты от некоторых типов атак, используйте с осторожностью."},
            {"type": "hpet", "title": "Отключить HPET",
             "description": "Отключает High Precision Event Timer, таймер высокой точности, который может вызывать микрозадержки. После применения требуется перезагрузка. Лучше применять если вы используете устройство только для игр",
             "impact": "Уменьшает задержки в некоторых играх и приложениях, требующих высокой точности времени.",
             "safety": "Безопасно, но может повлиять на некоторые приложения, зависящие от таймера."},
            {"type": "sticky_keys", "title": "Отключить залипание клавиш",
             "description": "Отключает функцию залипания клавиш, которая активируется при многократном нажатии Shift.",
             "impact": "Устраняет раздражающие всплывающие уведомления во время игр или работы.",
             "safety": "Безопасно, влияет только на удобство использования."},
            {"type": "firewall", "title": "Отключить брандмауэр",
             "description": "Полностью отключает встроенный брандмауэр Windows для всех сетевых профилей.",
             "impact": "Упрощает доступ к сети, может устранить блокировки программ.",
             "safety": "Снижает безопасность, не рекомендуется без альтернативного решения."},
            {"type": "scaling", "title": "Масштаб 100%",
             "description": "Устанавливает масштаб интерфейса Windows на 100%, отключая увеличение элементов.",
             "impact": "Возвращает стандартное отображение, устраняет размытость на некоторых экранах.",
             "safety": "Безопасно, влияет только на визуальное восприятие."},
            {"type": "background_apps", "title": "Отключить фоновые приложения",
             "description": "Запрещает приложениям работать в фоновом режиме, включая уведомления и обновления.",
             "impact": "Снижает нагрузку на систему, увеличивает свободные ресурсы.",
             "safety": "Безопасно, но может отключить некоторые полезные функции (например, уведомления)."},
            {"type": "performance", "title": "Максимальное быстродействие",
             "description": "Настраивает визуальные эффекты Windows для обеспечения максимальной производительности, отключая анимации и тени. Для детальной настройки под себя перейди в раздел Кастомизация",
             "impact": "Ускоряет работу системы, особенно на слабых ПК, за счет упрощения интерфейса.",
             "safety": "Безопасно, влияет только на внешний вид."},
            {"type": "defender", "title": "Отключить Защитник",
             "description": "Деактивирует встроенный антивирус Windows Defender, включая защиту в реальном времени.",
             "impact": "Снижает нагрузку на систему, освобождает ресурсы.",
             "safety": "Снижает безопасность, используйте только при наличии другого антивируса."},
            {"type": "spectre_meltdown", "title": "Отключить Spectre/Meltdown",
             "description": "Отключает патчи против уязвимостей Spectre и Meltdown, которые могут замедлять систему.",
             "impact": "Повышает производительность, особенно на старых процессорах.",
             "safety": "Снижает защиту от специфических атак, требует оценки рисков."},
            {"type": "trim", "title": "Отключить TRIM (не рекомендую, пробуйте сами)",
             "description": "Отключает команду TRIM для SSD, которая оптимизирует удаление данных.",
             "impact": "Может повлиять на производительность SSD в долгосрочной перспективе.",
             "safety": "Осторожно, не рекомендуется для большинства пользователей SSD."}
        ]

        for mod in modifiers:
            widget = ModifierWidget(mod["type"], mod["title"], mod["description"], mod["impact"], mod["safety"])
            self.misc_layout.addWidget(widget)

        self.misc_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def create_restore_point_widget(self):
        # Создаем виджет для точки восстановления
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        widget.setStyleSheet("""
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

        main_layout = QVBoxLayout(widget)
        header_layout = QHBoxLayout()

        title_label = QLabel("Создать точку восстановления")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #cccccc;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        details_widget = QWidget()
        details_widget.setStyleSheet("background-color: transparent")
        details_layout = QVBoxLayout(details_widget)

        info_widget = QWidget()
        info_widget.setStyleSheet("margin: 0,10,0,0; border: 1px solid #1e1e1e;")
        info_layout = QVBoxLayout(info_widget)

        desc_label = QLabel(
            '<span style="color:#4D90D5; font-size: 12px;">Описание</span>: Открывает встроенный интерфейс Windows для создания точки восстановления системы.')
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(desc_label)

        impact_label = QLabel(
            '<span style="color:#FFA500; font-size: 12px;">Эффект</span>: Позволяет сохранить текущее состояние системы для последующего восстановления.')
        impact_label.setWordWrap(True)
        impact_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(impact_label)

        safety_label = QLabel(
            '<span style="color:#32CD32; font-size: 12px;">Безопасность</span>: Крайне рекомендуется создавать перед внесением серьезных изменений в систему..')
        safety_label.setWordWrap(True)
        safety_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold; border: none;")
        info_layout.addWidget(safety_label)

        details_layout.addWidget(info_widget)

        create_button = QPushButton("Создать")
        create_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                background-color: #1e8449;
                border: 1px solid #1e8449;
            }
            QPushButton:hover {
                background-color: #196f3e;
            }
            QPushButton:pressed {
                background-color: #219A52;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        create_button.clicked.connect(self.create_restore_point)
        details_layout.addWidget(create_button)

        details_widget.setVisible(False)
        main_layout.addWidget(details_widget)

        widget.setCursor(Qt.PointingHandCursor)
        widget.mousePressEvent = lambda event: details_widget.setVisible(not details_widget.isVisible())

        return widget

    def create_restore_point(self):
        try:
            # Вызов встроенного интерфейса Windows для создания точки восстановления
            subprocess.run('SystemPropertiesProtection', shell=True, check=True)
        except Exception as e:
            # Можно добавить обработку ошибок, например, уведомление пользователя
            print(f"Ошибка при вызове создания точки восстановления: {str(e)}")
