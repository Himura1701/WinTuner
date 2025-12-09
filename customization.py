from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QScrollArea, QFrame, QHBoxLayout, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import winreg


def get_registry_value(key_path, value_name, default_value=None):
    try:
        # Пробуем открыть существующий ключ
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except WindowsError:
            winreg.CloseKey(key)
            return default_value
    except WindowsError:
        try:
            # Если ключ не существует, создаем его
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE | winreg.KEY_READ)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD if isinstance(default_value, int) else winreg.REG_SZ, default_value)
            winreg.CloseKey(key)
            return default_value
        except Exception as e:
            print(f"Error creating registry key: {e}")
            return default_value


class CustomizationWorker(QThread):
    progress = pyqtSignal(str, bool)
    finished = pyqtSignal()

    def __init__(self, setting_type, enable):
        super().__init__()
        self.setting_type = setting_type
        self.enable = enable

    def set_registry_value(self, key_path, value_name, value_data, value_type=winreg.REG_DWORD):
        try:
            # Создаем или открываем ключ с полными правами
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0,
                                     winreg.KEY_WRITE | winreg.KEY_READ)

            # Конвертируем строку в число для REG_DWORD
            if value_type == winreg.REG_DWORD and isinstance(value_data, str):
                value_data = int(value_data)

            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error setting registry value: {e}")
            return False

    def run(self):
        success = False

        registry_settings = {
            "window_animation": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
                "value": "0" if self.enable else "1",
                "type": winreg.REG_SZ
            },
            "context_menu": {
                "path": r"Control Panel\Desktop",
                "name": "MenuShowDelay",
                "value": "0" if self.enable else "400",
                "type": winreg.REG_SZ
            },
            "window_shadows": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ListviewShadow",
                "value": 0 if self.enable else 1
            },
            "menu_animation": {
                "path": r"Control Panel\Desktop",
                "name": "MenuAnimation",
                "value": 0 if self.enable else 1
            },
            "smooth_scroll": {
                "path": r"Control Panel\Desktop",
                "name": "SmoothScroll",
                "value": 0 if self.enable else 1
            },
            "taskbar_animation": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarAnimations",
                "value": 0 if self.enable else 1
            },
            "task_switch": {
                "path": r"Control Panel\Desktop",
                "name": "TaskSwitchEnabled",
                "value": 0 if self.enable else 1
            },
            "thumbnail_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "DisableThumbnailCache",
                "value": 1 if self.enable else 0
            },
            "right_click": {
                "path": r"Control Panel\Desktop",
                "name": "MenuShowDelay",
                "value": "0" if self.enable else "400",
                "type": winreg.REG_SZ
            },
            "smartscreen": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "SmartScreenEnabled",
                "value": "Off" if self.enable else "On",
                "type": winreg.REG_SZ
            },
            "start_menu_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "StartMenuDelay",
                "value": 0 if self.enable else 400
            },
            "app_close_delay": {
                "path": r"Control Panel\Desktop",
                "name": "HungAppTimeout",
                "value": "1000" if self.enable else "5000",
                "type": winreg.REG_SZ
            },
            "ui_hover_delay": {
                "path": r"Control Panel\Desktop",
                "name": "MouseHoverTime",
                "value": "0" if self.enable else "400",
                "type": winreg.REG_SZ
            },
            "tooltip_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ToolTipAnimationDelay",
                "value": 0 if self.enable else 500
            },
            "alt_tab_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "AltTabSettings",
                "value": 1 if self.enable else 0
            },
            "desktop_icons": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "IconSpacing",
                "value": "-1000" if self.enable else "-1125",
                "type": winreg.REG_SZ
            },
            "icon_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "Max Cached Icons",
                "value": "0" if self.enable else "2000",
                "type": winreg.REG_SZ
            },
            "window_fade": {
                "path": r"Control Panel\Desktop",
                "name": "UserPreferencesMask",
                "value": b"\x90\x12\x03\x80\x10\x00\x00\x00" if self.enable else b"\x9E\x1E\x07\x80\x12\x00\x00\x00",
                "type": winreg.REG_BINARY
            },
            "start_scroll": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "StartMenuAnimation",
                "value": 0 if self.enable else 1
            },
            "taskbar_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarGroupDelay",
                "value": 0 if self.enable else 500
            },
            "explorer_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "AlwaysUnloadDLL",
                "value": 1 if self.enable else 0
            },
            "minimize_animation": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
                "value": "0" if self.enable else "1",
                "type": winreg.REG_SZ
            },
            "menu_fade": {
                "path": r"Control Panel\Desktop",
                "name": "SelMenuFade",
                "value": 0 if self.enable else 1
            },
            "taskbar_hover": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarHoverTime",
                "value": 0 if self.enable else 400
            },
            "sync_all_settings": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync",
                "name": "SyncEnabled",
                "value": 0 if self.enable else 1
            },
            "sync_theme": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Personalization",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "sync_browser": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\BrowserSettings",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "sync_passwords": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Credentials",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "sync_language": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Language",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "sync_accessibility": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Accessibility",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "sync_other": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Windows",
                "name": "Enabled",
                "value": 0 if self.enable else 1
            },
            "disable_start_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SystemPaneSuggestionsEnabled",
                "value": 0 if self.enable else 1
            },
            "disable_recent_items": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "Start_TrackDocs",
                "value": 0 if self.enable else 1
            },
            "disable_explorer_ads": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ShowSyncProviderNotifications",
                "value": 0 if self.enable else 1
            },
            "disable_onedrive_startup": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                "name": "OneDrive",
                "value": b"\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" if self.enable else b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                "type": winreg.REG_BINARY
            },
            "disable_onedrive": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\OneDrive",
                "name": "DisableFileSyncNGSC",
                "value": 1 if self.enable else 0
            },
            "cortana_speech_recognition": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings\OnlineSpeechPrivacy",
                "name": "HasAccepted",
                "value": 0 if self.enable else 1
            },

            "cortana_location": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "AllowSearchToUseLocation",
                "value": 0 if self.enable else 1
            },

            "cortana_web_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "BingSearchEnabled",
                "value": 0 if self.enable else 1
            },

            "cortana_web_results": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "DisableWebSearch",
                "value": 1 if self.enable else 0
            },

            "cortana_speech_update": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings",
                "name": "ModelDownloadAllowed",
                "value": 0 if self.enable else 1
            },

            "cortana_cloud_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "CloudSearchEnabled",
                "value": 0 if self.enable else 1
            },

            "cortana_lockscreen": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "AllowCortanaAboveLock",
                "value": 0 if self.enable else 1
            },

            "cortana_taskbar_highlight": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "SearchboxTaskbarMode",
                "value": 0 if self.enable else 1
            },

            "cortana_reset": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "CortanaEnabled",
                "value": 0 if self.enable else 1
            },

            "cortana_personalization": {
                "path": r"SOFTWARE\Microsoft\Personalization\Settings",
                "name": "AcceptedPrivacyPolicy",
                "value": 0 if self.enable else 1
            },
            "taskbar_contacts": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People",
                "name": "PeopleBand",
                "value": 0 if self.enable else 1
            },

            "taskbar_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "SearchboxTaskbarMode",
                "value": 0 if self.enable else 1
            },

            "taskbar_meet_now": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                "name": "HideSCAMeetNow",
                "value": 1 if self.enable else 0
            },

            "taskbar_news": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Feeds",
                "name": "ShellFeedsTaskbarViewMode",
                "value": 2 if self.enable else 0
            },

            "taskbar_bing_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "BingSearchEnabled",
                "value": 0 if self.enable else 1
            },
            'lock_screen_spotlight': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'RotatingLockScreenEnabled',
                'value': 0 if self.enable else 1
            },
            'lock_screen_fun_facts': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'RotatingLockScreenOverlayEnabled',
                'value': 0 if self.enable else 1
            },
            'lock_screen_notifications': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings',
                'name': 'NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK',
                'value': 0 if self.enable else 1
            },
            'disable_feedback': {
                'path': r'SOFTWARE\Microsoft\Siuf\Rules',
                'name': 'NumberOfSIUFInPeriod',
                'value': 0 if self.enable else 1
            },
            'disable_remote_assistance': {
                'path': r'System\CurrentControlSet\Control\Remote Assistance',
                'name': 'fAllowToGetHelp',
                'value': 0 if self.enable else 1
            },
            'disable_remote_desktop': {
                'path': r'System\CurrentControlSet\Control\Terminal Server',
                'name': 'fDenyTSConnections',
                'value': 1 if self.enable else 0
            },
            'disable_kms': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows NT\CurrentVersion\Software Protection Platform',
                'name': 'NoGenTicket',
                'value': 1 if self.enable else 0
            },
            'disable_maps_update': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\Maps',
                'name': 'AutoDownloadAndUpdateMapData',
                'value': 0 if self.enable else 1
            },
            'disable_maps_traffic': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\Maps',
                'name': 'AllowUntriggeredNetworkTrafficOnSettingsPage',
                'value': 0 if self.enable else 1
            },
            'disable_pc_health': {
                'path': r'SOFTWARE\Microsoft\PCHealthCheck',
                'name': 'installations_disabled',
                'value': 1 if self.enable else 0
            },
            'disable_ncsi': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\NetworkConnectivityStatusIndicator',
                'name': 'NoActiveProbe',
                'value': 1 if self.enable else 0
            },
            'disable_store_auto_install': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\CloudContent',
                'name': 'DisableWindowsConsumerFeatures',
                'value': 1 if self.enable else 0
            },
            'disable_windows_tips': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'SoftLandingEnabled',
                'value': 0 if self.enable else 1
            },
            'disable_wmp_diagnostics': {
                'path': r'SOFTWARE\Microsoft\MediaPlayer\Preferences',
                'name': 'UsageTracking',
                'value': 0 if self.enable else 1
            },
            'windows_copilot': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced',
                'name': 'CoPilotEnabled',
                'value': 0 if self.enable else 1
            },
            'windows_copilot_feedback': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy',
                'name': 'TailoredExperiencesWithDiagnosticDataEnabled',
                'value': 0 if self.enable else 1
            }
        }

        if self.setting_type in registry_settings:
            setting = registry_settings[self.setting_type]
            success = self.set_registry_value(
                setting["path"],
                setting["name"],
                setting["value"],
                setting.get("type", winreg.REG_DWORD)
            )

        self.progress.emit(self.setting_type, success)
        self.finished.emit()


class CustomizationWidget(QFrame):
    def __init__(self, setting_type, title, description, impact, safety):
        super().__init__()
        self.worker = None
        self.setting_type = setting_type
        self.expanded = False
        self.is_enabled = False

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

        self.status_label = QLabel("Выключено")
        self.status_label.setStyleSheet("font-size: 12px; color: #FF6B6B; font-weight: bold;")

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
        desc_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: bold;
            border: none;
        """)
        info_layout.addWidget(desc_label)

        impact_label = QLabel(f'<span style="color:#FFA500; font-size: 12px;">Эффект</span>: {impact}')
        impact_label.setWordWrap(True)
        impact_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: bold;
            border: none;
        """)
        info_layout.addWidget(impact_label)

        safety_label = QLabel(f'<span style="color:#32CD32; font-size: 12px;">Безопасность</span>: {safety}')
        safety_label.setWordWrap(True)
        safety_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: bold;
            border: none;
        """)
        info_layout.addWidget(safety_label)

        self.details_layout.addWidget(info_widget)

        self.toggle_button = QPushButton("Включить")
        self.toggle_button.setStyleSheet("""
        QPushButton {
            color: white;
            font-weight: bold;
            background-color: #1e8449;
            border: 1px solid #1e8449;
            padding: 5px;
            border-radius: 5px;
        }
        QPushButton[state="off"] {
            background-color: #f04438;
            border: 1px solid #f04438;
        }
        QPushButton:hover {
            background-color: #196f3e;
        }
        QPushButton[state="off"]:hover {
            background-color: #d63b2f;
        }
        QPushButton:pressed {
            background-color: #219A52;
        }
        QPushButton[state="off"]:pressed {
            background-color: #b33129;
        }
        QPushButton:disabled {
            background-color: #666666;
        }
        """)
        self.toggle_button.clicked.connect(self.toggle_setting)
        self.details_layout.addWidget(self.toggle_button)

        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)

        self.setCursor(Qt.PointingHandCursor)

        # Check initial state
        self.check_current_state()

    def update_button_style(self):
        if self.is_enabled:
            self.toggle_button.setProperty("state", "off")
            self.toggle_button.setText("Выключить")
        else:
            self.toggle_button.setProperty("state", None)
            self.toggle_button.setText("Включить")
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)

    def check_current_state(self):
        """Check the current state of the setting in the registry"""
        registry_settings = {
            "window_animation": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
                "default": "1",
                "enabled_value": "0"
            },
            "context_menu": {
                "path": r"Control Panel\Desktop",
                "name": "MenuShowDelay",
                "default": "400",
                "enabled_value": "0"
            },
            "transparency": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "UseOLEDTaskbarTransparency",
                "default": 1,
                "enabled_value": 0
            },
            "window_shadows": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ListviewShadow",
                "default": 1,
                "enabled_value": 0
            },
            "menu_animation": {
                "path": r"Control Panel\Desktop",
                "name": "MenuAnimation",
                "default": "1",
                "enabled_value": "0"
            },
            "smooth_scroll": {
                "path": r"Control Panel\Desktop",
                "name": "SmoothScroll",
                "default": "1",
                "enabled_value": "0"
            },
            "taskbar_animation": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarAnimations",
                "default": 1,
                "enabled_value": 0
            },
            "task_switch": {
                "path": r"Control Panel\Desktop",
                "name": "TaskSwitchEnabled",
                "default": "0",
                "enabled_value": "1"
            },
            "thumbnail_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "DisableThumbnailCache",
                "default": 0,
                "enabled_value": 1
            },
            "right_click": {
                "path": r"Control Panel\Desktop",
                "name": "MenuShowDelay",
                "default": "400",
                "enabled_value": "0"
            },
            "smartscreen": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "SmartScreenEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "start_menu_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "Start_ShowDelay",
                "default": 1,
                "enabled_value": 0
            },
            "app_close_delay": {
                "path": r"Control Panel\Desktop",
                "name": "HungAppTimeout",
                "default": "5000",
                "enabled_value": "1000"
            },
            "ui_hover_delay": {
                "path": r"Control Panel\Desktop",
                "name": "MouseHoverTime",
                "default": "400",
                "enabled_value": "0"
            },
            "tooltip_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TooltipAnimationDuration",
                "default": 500,
                "enabled_value": 0
            },
            "alt_tab_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "AltTabSettings",
                "default": 0,
                "enabled_value": 1
            },
            "desktop_icons": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "IconSpacing",
                "default": "-1125",
                "enabled_value": "-1000"
            },
            "icon_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "Max Cached Icons",
                "default": "2000",
                "enabled_value": "0"
            },
            "window_fade": {
                "path": r"Control Panel\Desktop",
                "name": "UserPreferencesMask",
                "default": b"\x9E\x1E\x07\x80\x12\x00\x00\x00",
                "enabled_value": b"\x90\x12\x03\x80\x10\x00\x00\x00"
            },
            "start_scroll": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "StartMenuAnimations",
                "default": 1,
                "enabled_value": 0
            },
            "taskbar_delay": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarGroupSize",
                "default": 2,
                "enabled_value": 0
            },
            "minimize_animation": {
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
                "default": "1",
                "enabled_value": "0"
            },
            "menu_fade": {
                "path": r"Control Panel\Desktop",
                "name": "SelMenuFade",
                "default": 1,
                "enabled_value": 0
            },
            "taskbar_hover": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarHoverTime",
                "default": 400,
                "enabled_value": 0
            },
            "sync_all_settings": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync",
                "name": "SyncEnabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_theme": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Personalization",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_browser": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\BrowserSettings",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_passwords": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Credentials",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_language": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Language",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_accessibility": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Accessibility",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "sync_other": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Windows",
                "name": "Enabled",
                "default": 1,
                "enabled_value": 0
            },
            "explorer_cache": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer",
                "name": "AlwaysUnloadDLL",
                "default": 0,
                "enabled_value": 1
            },
            "disable_start_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SystemPaneSuggestionsEnabled",
                "default": 1,
                "enabled_value": 0
            },
            "disable_recent_items": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "Start_TrackDocs",
                "default": 1,
                "enabled_value": 0
            },
            "disable_explorer_ads": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "ShowSyncProviderNotifications",
                "default": 1,
                "enabled_value": 0
            },
            "disable_onedrive_startup": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
                "name": "OneDrive",
                "default": b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                "enabled_value": b"\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            },
            "disable_onedrive": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\OneDrive",
                "name": "DisableFileSyncNGSC",
                "default": 0,
                "enabled_value": 1
            },
            "cortana_speech_recognition": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings\OnlineSpeechPrivacy",
                "name": "HasAccepted",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_location": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "AllowSearchToUseLocation",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_web_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "BingSearchEnabled",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_web_results": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "DisableWebSearch",
                "default": 0,
                "enabled_value": 1
            },
            "cortana_speech_update": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings",
                "name": "ModelDownloadAllowed",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_cloud_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "CloudSearchEnabled",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_lockscreen": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "AllowCortanaAboveLock",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_taskbar_highlight": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "SearchboxTaskbarMode",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_reset": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "CortanaEnabled",
                "default": 1,
                "enabled_value": 0
            },
            "cortana_personalization": {
                "path": r"SOFTWARE\Microsoft\Personalization\Settings",
                "name": "AcceptedPrivacyPolicy",
                "default": 1,
                "enabled_value": 0
            },
            "taskbar_contacts": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People",
                "name": "PeopleBand",
                "default": 1,
                "enabled_value": 0
            },
            "taskbar_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "SearchboxTaskbarMode",
                "default": 1,
                "enabled_value": 0
            },
            "taskbar_meet_now": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                "name": "HideSCAMeetNow",
                "default": 0,
                "enabled_value": 1
            },
            "taskbar_news": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Feeds",
                "name": "ShellFeedsTaskbarViewMode",
                "default": 0,
                "enabled_value": 2
            },
            "taskbar_bing_search": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                "name": "BingSearchEnabled",
                "default": 1,
                "enabled_value": 0
            },
            'lock_screen_spotlight': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'RotatingLockScreenEnabled',
                'default': 1,
                'enabled_value': 0
            },
            'lock_screen_fun_facts': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'RotatingLockScreenOverlayEnabled',
                'default': 1,
                'enabled_value': 0
            },
            'lock_screen_notifications': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings',
                'name': 'NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK',
                'default': 1,
                'enabled_value': 0
            },
            'disable_feedback': {
                'path': r'SOFTWARE\Microsoft\Siuf\Rules',
                'name': 'NumberOfSIUFInPeriod',
                'default': 1,
                'enabled_value': 0
            },
            'disable_remote_assistance': {
                'path': r'System\CurrentControlSet\Control\Remote Assistance',
                'name': 'fAllowToGetHelp',
                'default': 1,
                'enabled_value': 0
            },
            'disable_remote_desktop': {
                'path': r'System\CurrentControlSet\Control\Terminal Server',
                'name': 'fDenyTSConnections',
                'default': 0,
                'enabled_value': 1
            },
            'disable_kms': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows NT\CurrentVersion\Software Protection Platform',
                'name': 'NoGenTicket',
                'default': 0,
                'enabled_value': 1
            },
            'disable_maps_update': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\Maps',
                'name': 'AutoDownloadAndUpdateMapData',
                'default': 1,
                'enabled_value': 0
            },
            'disable_maps_traffic': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\Maps',
                'name': 'AllowUntriggeredNetworkTrafficOnSettingsPage',
                'default': 1,
                'enabled_value': 0
            },
            'disable_pc_health': {
                'path': r'SOFTWARE\Microsoft\PCHealthCheck',
                'name': 'installations_disabled',
                'default': 0,
                'enabled_value': 1
            },
            'disable_ncsi': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\NetworkConnectivityStatusIndicator',
                'name': 'NoActiveProbe',
                'default': 0,
                'enabled_value': 1
            },
            'disable_store_auto_install': {
                'path': r'SOFTWARE\Policies\Microsoft\Windows\CloudContent',
                'name': 'DisableWindowsConsumerFeatures',
                'default': 0,
                'enabled_value': 1
            },
            'disable_windows_tips': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager',
                'name': 'SoftLandingEnabled',
                'default': 1,
                'enabled_value': 0
            },
            'disable_wmp_diagnostics': {
                'path': r'SOFTWARE\Microsoft\MediaPlayer\Preferences',
                'name': 'UsageTracking',
                'default': 1,
                'enabled_value': 0
            },
            'windows_copilot': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced',
                'name': 'CoPilotEnabled',
                'default': 1,
                'enabled_value': 0
            },
            'windows_copilot_feedback': {
                'path': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy',
                'name': 'TailoredExperiencesWithDiagnosticDataEnabled',
                'default': 1,
                'enabled_value': 0
            }
        }

        if self.setting_type in registry_settings:
            setting = registry_settings[self.setting_type]
            value = get_registry_value(setting["path"], setting["name"], setting["default"])
            self.is_enabled = str(value) == str(setting["enabled_value"])
        else:
            # Для неизвестных типов настроек по умолчанию считаем, что они выключены
            self.is_enabled = False

        # Update UI to reflect current state
        if self.is_enabled:
            self.status_label.setText("Включено")
            self.status_label.setStyleSheet("font-size: 12px; color: #90EE90; font-weight: bold;")
        else:
            self.status_label.setText("Выключено")
            self.status_label.setStyleSheet("font-size: 12px; color: #FF6B6B; font-weight: bold;")

        self.update_button_style()

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.details_widget.setVisible(self.expanded)

    def toggle_setting(self):
        self.toggle_button.setEnabled(False)
        self.is_enabled = not self.is_enabled

        self.worker = CustomizationWorker(self.setting_type, self.is_enabled)
        self.worker.progress.connect(self.setting_progress)
        self.worker.finished.connect(self.setting_finished)
        self.worker.start()

    def setting_progress(self, setting_type, success):
        if setting_type == self.setting_type and success:
            if self.is_enabled:
                self.status_label.setText("Включено")
                self.status_label.setStyleSheet("font-size: 12px; color: #90EE90; font-weight: bold;")
            else:
                self.status_label.setText("Выключено")
                self.status_label.setStyleSheet("font-size: 12px; color: #FF6B6B; font-weight: bold;")

            self.update_button_style()

    def setting_finished(self):
        self.toggle_button.setEnabled(True)


class CustomizationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.admin_warning = None
        self.init_ui()
        self.setStyleSheet("background-color: #121212; border-radius: 5px;")

    def init_ui(self):
        layout = QVBoxLayout(self)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
                        QTabWidget::pane {
                            border: 1px solid #555555;
                            background: #1e1e1e;
                            border-radius: 5px;
                        }
                        QTabBar::tab {
                            background: #121212;;
                            color: #cccccc;
                            font-weight: bold;
                            font-size: 10px;
                            padding: 8px;
                            margin-left: 1px;
                            border: 1px solid #34495e;
                            border-bottom-color: #1e1e1e;
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px;
                        }
                        QTabBar::tab:selected, QTabBar::tab:hover {
                            background: #1e1e1e;
                        }
                        QTabBar::tab:selected {
                            background: #34495e;
                            border-color: #34495e;
                            border-bottom-color: #1e1e1e;
                        }
                    """)

        interface_tab = self.create_tab("Интерфейс")
        explorer_tab = self.create_tab("Проводник Windows")
        cortana_tab = self.create_tab("Cortana")
        windows_synhronization_tab = self.create_tab("Синхронизация настроек Windows")
        windows_ai_tab = self.create_tab("Windows AI")
        lock_screen_tab = self.create_tab("Экран блокировки")
        task_panel_tab = self.create_tab("Панель задач")
        another_tab = self.create_tab("Другие настройки")

        tab_widget.addTab(interface_tab, "Интерфейс")
        tab_widget.addTab(explorer_tab, "Проводник Windows")
        tab_widget.addTab(cortana_tab, "Cortana")
        tab_widget.addTab(windows_synhronization_tab, "Синхронизация настроек Windows")
        tab_widget.addTab(windows_ai_tab, "Windows AI")
        tab_widget.addTab(lock_screen_tab, "Экран блокировки")
        tab_widget.addTab(task_panel_tab, "Панель задач")
        tab_widget.addTab(another_tab, "Другие настройки")

        layout.addWidget(tab_widget)

    def create_tab(self, tab_name):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        customization_settings = self.get_settings_for_tab(tab_name)

        for setting in customization_settings:
            widget = CustomizationWidget(
                setting['type'],
                setting['title'],
                setting['description'],
                setting['impact'],
                setting['safety']
            )
            container_layout.addWidget(widget)

        container_layout.addStretch()
        scroll.setWidget(container)
        tab_layout.addWidget(scroll)

        return tab

    def get_settings_for_tab(self, tab_name):
        all_settings = [
            {
                'type': 'window_animation',
                'title': 'Отключение анимации окон',
                'description': 'Отключает анимацию при открытии и закрытии окон',
                'impact': 'Ускорение отклика системы при работе с окнами',
                'safety': 'Безопасно. Влияет только на визуальные эффекты'
            },
            {
                'type': 'context_menu',
                'title': 'Ускорение появления контекстного меню',
                'description': 'Уменьшает задержку перед появлением контекстного меню',
                'impact': 'Мгновенное появление меню при клике правой кнопкой мыши',
                'safety': 'Безопасно. Не влияет на функциональность'
            },
            {
                'type': 'window_shadows',
                'title': 'Отключение теней у окон и меню',
                'description': 'Убирает эффект тени вокруг окон и контекстных меню',
                'impact': 'Повышение производительности на слабых системах',
                'safety': 'Безопасно. Чисто визуальное изменение'
            },
            {
                'type': 'menu_animation',
                'title': 'Отключение эффектов появления/исчезновения меню',
                'description': 'Убирает анимацию при открытии и закрытии меню',
                'impact': 'Ускорение работы с меню приложений',
                'safety': 'Безопасно. Только визуальный эффект'
            },
            {
                'type': 'smooth_scroll',
                'title': 'Отключение эффекта плавной прокрутки',
                'description': 'Отключает сглаживание при прокрутке страниц',
                'impact': 'Более быстрый отклик при скроллинге',
                'safety': 'Безопасно. Влияет только на анимацию прокрутки'
            },
            {
                'type': 'taskbar_animation',
                'title': 'Отключение анимации панели задач',
                'description': 'Убирает анимацию элементов панели задач',
                'impact': 'Мгновенный отклик панели задач',
                'safety': 'Безопасно. Только визуальное изменение'
            },
            {
                'type': 'task_switch',
                'title': 'Ускорение отклика окон при переключении задач',
                'description': 'Оптимизирует время отклика при Alt+Tab',
                'impact': 'Более быстрое переключение между окнами',
                'safety': 'Безопасно. Не влияет на стабильность'
            },
            {
                'type': 'thumbnail_cache',
                'title': 'Отключение кеширования миниатюр',
                'description': 'Отключает сохранение миниатюр файлов',
                'impact': 'Экономия места на диске и памяти',
                'safety': 'Безопасно. Миниатюры будут создаваться заново'
            },
            {
                'type': 'right_click',
                'title': 'Ускорение реакции системы на клик правой кнопкой',
                'description': 'Минимизирует задержку контекстного меню',
                'impact': 'Мгновенное появление меню',
                'safety': 'Безопасно. Оптимизация интерфейса'
            },
            {
                'type': 'smartscreen',
                'title': 'Отключение SmartScreen',
                'description': 'Отключает проверку файлов системой SmartScreen',
                'impact': 'Ускорение открытия файлов и программ',
                'safety': 'Требует осторожности. Снижает безопасность'
            },
            {
                'type': 'start_menu_delay',
                'title': 'Отключение задержки при загрузке меню "Пуск"',
                'description': 'Убирает искусственную задержку меню',
                'impact': 'Мгновенное открытие меню "Пуск"',
                'safety': 'Безопасно. Оптимизация интерфейса'
            },
            {
                'type': 'app_close_delay',
                'title': 'Отключение задержки при закрытии программ',
                'description': 'Ускоряет процесс закрытия приложений',
                'impact': 'Более быстрое закрытие программ',
                'safety': 'Безопасно при стабильной системе'
            },
            {
                'type': 'ui_hover_delay',
                'title': 'Отключение задержки при наведении курсора',
                'description': 'Убирает задержку при наведении на элементы',
                'impact': 'Мгновенная реакция интерфейса',
                'safety': 'Безопасно. Оптимизация отклика'
            },
            {
                'type': 'tooltip_delay',
                'title': 'Уменьшение задержки всплывающих подсказок',
                'description': 'Ускоряет появление и исчезновение подсказок',
                'impact': 'Более быстрый показ подсказок',
                'safety': 'Безопасно. Настройка интерфейса'
            },
            {
                'type': 'alt_tab_delay',
                'title': 'Ускорение переключения между окнами',
                'description': 'Оптимизирует время отклика Alt+Tab',
                'impact': 'Мгновенное переключение окон',
                'safety': 'Безопасно. Оптимизация системы'
            },
            {
                'type': 'desktop_icons',
                'title': 'Ускорение отклика значков на рабочем столе',
                'description': 'Оптимизирует работу со значками',
                'impact': 'Более быстрый отклик рабочего стола',
                'safety': 'Безопасно. Оптимизация интерфейса'
            },
            {
                'type': 'icon_cache',
                'title': 'Отключение обновления кеша значков',
                'description': 'Отключает автообновление кеша иконок',
                'impact': 'Ускорение работы проводника',
                'safety': 'Безопасно. Можно обновить вручную'
            },
            {
                'type': 'window_fade',
                'title': 'Отключение эффекта исчезновения окон',
                'description': 'Убирает анимацию закрытия окон',
                'impact': 'Мгновенное закрытие окон',
                'safety': 'Безопасно. Визуальный эффект'
            },
            {
                'type': 'start_scroll',
                'title': 'Отключение эффекта прокрутки в меню "Пуск"',
                'description': 'Убирает анимацию прокрутки в меню',
                'impact': 'Более быстрая навигация по меню',
                'safety': 'Безопасно. Оптимизация меню'
            },
            {
                'type': 'taskbar_delay',
                'title': 'Уменьшение задержки запуска из панели задач',
                'description': 'Ускоряет запуск приложений',
                'impact': 'Более быстрый старт программ',
                'safety': 'Безопасно. Оптимизация запуска'
            },
            {
                'type': 'minimize_animation',
                'title': 'Отключение анимации сворачивания',
                'description': 'Убирает анимацию минимизации окон',
                'impact': 'Мгновенное сворачивание окон',
                'safety': 'Безопасно. Визуальный эффект'
            },
            {
                'type': 'menu_fade',
                'title': 'Отключение эффекта затухания меню',
                'description': 'Убирает анимацию появления/исчезновения',
                'impact': 'Мгновенная работа с меню',
                'safety': 'Безопасно. Визуальный эффект'
            },
            {
                'type': 'taskbar_hover',
                'title': 'Отключение задержки панели задач',
                'description': 'Убирает задержку при наведении',
                'impact': 'Мгновенный отклик панели задач',
                'safety': 'Безопасно. Оптимизация интерфейса'
            },
            {
                'type': 'explorer_cache',
                'title': 'Отключение буфера Проводника',
                'description': 'Отключает временное хранение файлов',
                'impact': 'Экономия памяти, быстрая работа',
                'safety': 'Безопасно. Системная оптимизация'
            },
            {
                'type': 'sync_all_settings',
                'title': 'Отключить синхронизацию всех настроек',
                'description': 'Полностью отключает синхронизацию настроек Windows между устройствами',
                'impact': 'Прекращение синхронизации всех настроек Windows между устройствами',
                'safety': 'Безопасно. Можно включить обратно в любой момент'
            },
            {
                'type': 'sync_theme',
                'title': 'Отключить синхронизацию настроек темы',
                'description': 'Отключает синхронизацию настроек оформления и персонализации',
                'impact': 'Темы и персонализация останутся локальными для каждого устройства',
                'safety': 'Безопасно. Влияет только на визуальные настройки'
            },
            {
                'type': 'sync_browser',
                'title': 'Отключить синхронизацию настроек веб-браузера',
                'description': 'Отключает синхронизацию настроек браузера Edge между устройствами',
                'impact': 'Настройки браузера будут независимы на каждом устройстве',
                'safety': 'Безопасно. Не влияет на сохранённые данные'
            },
            {
                'type': 'sync_passwords',
                'title': 'Отключить синхронизацию паролей',
                'description': 'Отключает синхронизацию сохранённых паролей Windows',
                'impact': 'Пароли не будут синхронизироваться между устройствами',
                'safety': 'Безопасно. Рекомендуется для повышения безопасности'
            },
            {
                'type': 'sync_language',
                'title': 'Отключить синхронизацию языковых настроек',
                'description': 'Отключает синхронизацию языковых параметров и словарей',
                'impact': 'Языковые настройки останутся локальными для устройства',
                'safety': 'Безопасно. Влияет только на языковые параметры'
            },
            {
                'type': 'sync_accessibility',
                'title': 'Отключить синхронизацию настроек упрощённого доступа',
                'description': 'Отключает синхронизацию параметров специальных возможностей',
                'impact': 'Настройки доступности не будут синхронизироваться',
                'safety': 'Безопасно. Влияет только на параметры доступности'
            },
            {
                'type': 'sync_other',
                'title': 'Отключить синхронизацию дополнительных настроек Windows',
                'description': 'Отключает синхронизацию прочих настроек Windows',
                'impact': 'Остальные настройки Windows останутся локальными',
                'safety': 'Безопасно. Можно настроить индивидуально'
            },
            {
                'type': 'disable_start_suggestions',
                'title': 'Отключить рекомендуемые приложения в меню Пуск',
                'description': 'Убирает рекомендации приложений из меню "Пуск"',
                'impact': 'Очистка меню "Пуск" от рекламных предложений',
                'safety': 'Безопасно. Влияет только на рекомендации'
            },
            {
                'type': 'disable_recent_items',
                'title': 'Отключить недавно открытые элементы',
                'description': 'Не показывать недавно открытые элементы в меню "Пуск" и панели задач',
                'impact': 'Повышение приватности, очистка списков переходов',
                'safety': 'Безопасно. Можно включить обратно в любой момент'
            },
            {
                'type': 'disable_explorer_ads',
                'title': 'Отключить рекламу в проводнике Windows / OneDrive',
                'description': 'Убирает рекламные уведомления в проводнике Windows',
                'impact': 'Отсутствие рекламных баннеров и уведомлений',
                'safety': 'Безопасно. Не влияет на функциональность'
            },
            {
                'type': 'disable_onedrive_startup',
                'title': 'Отключить сетевой доступ OneDrive до входа',
                'description': 'Отключает автозапуск OneDrive при старте системы',
                'impact': 'OneDrive не будет запускаться автоматически',
                'safety': 'Безопасно. Можно запустить вручную'
            },
            {
                'type': 'disable_onedrive',
                'title': 'Отключение Microsoft OneDrive',
                'description': 'Полностью отключает интеграцию OneDrive с системой',
                'impact': 'Прекращение синхронизации файлов с OneDrive',
                'safety': 'Безопасно. Требуется ручное включение'
            },
            {
                'type': 'cortana_speech_recognition',
                'title': 'Отключить онлайн распознавание речи',
                'description': 'Отключает функцию онлайн распознавания речи в системе',
                'impact': 'Повышение приватности, система не будет отправлять голосовые данные',
                'safety': 'Безопасно. Локальное распознавание речи продолжит работать'
            },
            {
                'type': 'cortana_location',
                'title': 'Запретить Cortana и поиску использовать данные местоположения',
                'description': 'Отключает доступ Cortana к данным о местоположении устройства',
                'impact': 'Повышение приватности, отсутствие локализованных результатов',
                'safety': 'Безопасно. Не влияет на основные функции поиска'
            },
            {
                'type': 'cortana_web_search',
                'title': 'Отключить Веб-поиск в локальном поиске',
                'description': 'Отключает интеграцию веб-результатов в локальном поиске Windows',
                'impact': 'Ускорение поиска, только локальные результаты',
                'safety': 'Безопасно. Улучшает приватность'
            },
            {
                'type': 'cortana_web_results',
                'title': 'Запретить отображение результатов поиска из Интернета',
                'description': 'Полностью отключает показ результатов из интернета в поиске Windows',
                'impact': 'Только локальные результаты поиска',
                'safety': 'Безопасно. Повышает скорость поиска'
            },
            {
                'type': 'cortana_speech_update',
                'title': 'Отключить загрузку модулей распознавания и синтеза речи',
                'description': 'Предотвращает автоматическое обновление голосовых модулей',
                'impact': 'Экономия трафика, отсутствие автообновлений речевых функций',
                'safety': 'Безопасно. Можно обновить вручную при необходимости'
            },
            {
                'type': 'cortana_cloud_search',
                'title': 'Отключить поиск в облаке',
                'description': 'Отключает использование облачных сервисов при поиске',
                'impact': 'Повышение приватности и скорости поиска',
                'safety': 'Безопасно. Работает только локальный поиск'
            },
            {
                'type': 'cortana_lockscreen',
                'title': 'Отключение Кортаны над экраном блокировки',
                'description': 'Убирает доступ к Cortana с экрана блокировки',
                'impact': 'Повышение безопасности системы',
                'safety': 'Безопасно. Рекомендуется для защиты'
            },
            {
                'type': 'cortana_taskbar_highlight',
                'title': 'Отключение подсветки поиска на панели задач',
                'description': 'Убирает визуальное выделение поиска на панели задач',
                'impact': 'Менее навязчивый интерфейс',
                'safety': 'Безопасно. Только визуальное изменение'
            },
            {
                'type': 'cortana_reset',
                'title': 'Отключить и сбросить настройки Cortana',
                'description': 'Полностью отключает Cortana и сбрасывает все её настройки',
                'impact': 'Полное отключение функций Cortana',
                'safety': 'Безопасно. Можно включить заново при необходимости'
            },
            {
                'type': 'cortana_personalization',
                'title': 'Отключить ввод персонализации и знакомство с пользователем',
                'description': 'Отключает сбор данных для персонализации Cortana',
                'impact': 'Повышение приватности, отсутствие персонализации',
                'safety': 'Безопасно. Рекомендуется для защиты личных данных'
            },
            {
                'type': 'taskbar_contacts',
                'title': 'Удалить значок контактов в панели задач',
                'description': 'Убирает значок People (Контакты) из панели задач Windows',
                'impact': 'Освобождение места на панели задач, отключение быстрого доступа к контактам',
                'safety': 'Безопасно. Не влияет на сами контакты и их данные'
            },
            {
                'type': 'taskbar_search',
                'title': 'Отключить окно поиска в панели задач',
                'description': 'Убирает поисковое поле из панели задач Windows',
                'impact': 'Больше свободного места на панели задач, поиск доступен через Win+S',
                'safety': 'Безопасно. Функция поиска остаётся доступной'
            },
            {
                'type': 'taskbar_meet_now',
                'title': 'Отключить "Встреча сейчас" в баре задач',
                'description': 'Убирает кнопку быстрого создания встреч из панели задач',
                'impact': 'Очистка панели задач от неиспользуемых элементов',
                'safety': 'Безопасно. Функция доступна через другие способы'
            },
            {
                'type': 'taskbar_news',
                'title': 'Отключение новостей и интересов в баре задач',
                'description': 'Отключает виджет новостей и погоды в панели задач',
                'impact': 'Уменьшение потребления ресурсов, отключение автоматических обновлений новостей',
                'safety': 'Безопасно. Не влияет на работу системы'
            },
            {
                'type': 'taskbar_bing_search',
                'title': 'Отключить интернет-поиск (Bing) для локального поиска',
                'description': 'Отключает интеграцию с Bing в локальном поиске Windows',
                'impact': 'Ускорение поиска, повышение приватности',
                'safety': 'Безопасно. Останется только локальный поиск'
            },
            {
                'type': 'lock_screen_spotlight',
                'title': 'Отключить функцию "Windows: интересное"',
                'description': 'Отключает показ красивых фотографий и изображений на экране блокировки',
                'impact': 'Статическое изображение на экране блокировки, экономия трафика',
                'safety': 'Безопасно. Влияет только на визуальное оформление'
            },
            {
                'type': 'lock_screen_fun_facts',
                'title': 'Отключить забавные факты и советы',
                'description': 'Убирает отображение советов, рекомендаций и интересных фактов на экране блокировки',
                'impact': 'Чистый экран блокировки без дополнительной информации',
                'safety': 'Безопасно. Только информационный контент'
            },
            {
                'type': 'lock_screen_notifications',
                'title': 'Отключить уведомления на экране блокировки',
                'description': 'Отключает показ уведомлений от приложений на экране блокировки',
                'impact': 'Повышение приватности, отсутствие уведомлений до разблокировки',
                'safety': 'Безопасно. Рекомендуется для защиты личных данных'
            },
            {
                'type': 'disable_feedback',
                'title': 'Отключение напоминаний об отзывах',
                'description': 'Отключает запросы на предоставление отзывов о Windows',
                'impact': 'Отсутствие всплывающих окон с просьбой оставить отзыв',
                'safety': 'Безопасно. Не влияет на работу системы'
            },
            {
                'type': 'disable_remote_assistance',
                'title': 'Отключение удаленного помощника',
                'description': 'Отключает возможность подключения удаленного помощника к компьютеру',
                'impact': 'Повышение безопасности, блокировка удаленного доступа помощника',
                'safety': 'Безопасно. Рекомендуется для защиты'
            },
            {
                'type': 'disable_remote_desktop',
                'title': 'Отключение удаленных подключений',
                'description': 'Запрещает удаленные подключения к этому компьютеру',
                'impact': 'Повышение безопасности системы, блокировка удаленного доступа',
                'safety': 'Безопасно. Рекомендуется для защиты'
            },
            {
                'type': 'disable_kms',
                'title': 'Отключение онлайн-активации KMS',
                'description': 'Деактивирует онлайн-активацию через службу управления ключами',
                'impact': 'Отключение автоматической активации Windows через KMS',
                'safety': 'Безопасно. Не влияет на текущую активацию'
            },
            {
                'type': 'disable_maps_update',
                'title': 'Отключить обновление карт',
                'description': 'Отключает автоматическую загрузку и обновление карт',
                'impact': 'Экономия трафика, отключение фоновых обновлений карт',
                'safety': 'Безопасно. Карты можно обновить вручную'
            },
            {
                'type': 'disable_maps_traffic',
                'title': 'Отключить сетевой трафик карт',
                'description': 'Отключает нежелательный сетевой трафик на странице настроек офлайн-карты',
                'impact': 'Экономия трафика, повышение приватности',
                'safety': 'Безопасно. Не влияет на работу системы'
            },
            {
                'type': 'disable_pc_health',
                'title': 'Отключить проверку работоспособности ПК',
                'description': 'Отключает установку и работу службы проверки работоспособности ПК',
                'impact': 'Отключение автоматической диагностики системы',
                'safety': 'Безопасно. Можно проверять систему вручную'
            },
            {
                'type': 'disable_ncsi',
                'title': 'Отключить индикатор состояния сети',
                'description': 'Отключает индикатор состояния сетевого подключения Windows (NCSI)',
                'impact': 'Отключение проверок интернет-соединения Windows',
                'safety': 'Безопасно. Не влияет на работу сети'
            },
            {
                'type': 'disable_store_auto_install',
                'title': 'Отключить автоустановку приложений',
                'description': 'Отключает автоматическую установку рекомендуемых приложений из Windows Store',
                'impact': 'Предотвращение автоматической установки приложений',
                'safety': 'Безопасно. Контроль над установкой приложений'
            },
            {
                'type': 'disable_windows_tips',
                'title': 'Отключить советы Windows',
                'description': 'Отключает советы, подсказки и рекомендации при использовании Windows',
                'impact': 'Отсутствие всплывающих подсказок системы',
                'safety': 'Безопасно. Только информационный контент'
            },
            {
                'type': 'disable_wmp_diagnostics',
                'title': 'Отключить диагностику Windows Media',
                'description': 'Отключает отправку диагностических данных проигрывателя Windows Media',
                'impact': 'Повышение приватности при использовании медиаплеера',
                'safety': 'Безопасно. Не влияет на функциональность'
            },
            {
                'type': 'windows_copilot',
                'title': 'Деактивация программы Windows Copilot',
                'description': 'Отключает функционал Windows Copilot и его автозапуск',
                'impact': 'Предотвращает работу AI-ассистента Windows и его фоновых процессов',
                'safety': 'Безопасно. Можно включить обратно при необходимости'
            },
            {
                'type': 'windows_copilot_feedback',
                'title': 'Отключение отзывов Windows Copilot',
                'description': 'Отключает сбор и отправку данных об использовании Windows Copilot',
                'impact': 'Повышение приватности, прекращение отправки отзывов о работе AI',
                'safety': 'Безопасно. Улучшает конфиденциальность'
            }

        ]

        if tab_name == "Интерфейс":
            return [s for s in all_settings if s['type'] in [
                'window_animation', 'context_menu', 'window_shadows', 'menu_animation',
                'smooth_scroll', 'taskbar_animation', 'task_switch', 'right_click',
                'start_menu_delay', 'app_close_delay','ui_hover_delay', 'tooltip_delay', 'alt_tab_delay',
                'window_fade', 'start_scroll', 'taskbar_delay', 'minimize_animation',
                'menu_fade', 'taskbar_hover', 'thumbnail_cache', 'desktop_icons', 'icon_cache', 'smartscreen'
            ]]
        elif tab_name == "Проводник Windows":
            return [s for s in all_settings if s['type'] in [
                'explorer_cache', 'disable_explorer_ads', 'disable_onedrive', 'disable_onedrive_startup',
                'disable_start_suggestions', 'disable_recent_items'
            ]]
        elif tab_name == "Cortana":
            return [s for s in all_settings if s['type'] in [
                'cortana_speech_recognition', 'cortana_location', 'cortana_web_search',
                'cortana_web_results', 'cortana_speech_update', 'cortana_cloud_search',
                'cortana_lockscreen', 'cortana_taskbar_highlight', 'cortana_reset',
                'cortana_personalization'
            ]]
        elif tab_name == "Синхронизация настроек Windows":
            return [s for s in all_settings if s['type'] in [
                'sync_all_settings', 'sync_theme', 'sync_browser', 'sync_passwords', 'sync_language',
                'sync_accessibility', 'sync_other'
            ]]
        elif tab_name == "Windows AI":
            return [s for s in all_settings if s['type'] in [
                'windows_copilot', 'windows_copilot_feedback'
            ]]
        elif tab_name == "Экран блокировки":
            return [s for s in all_settings if s['type'] in [
                'lock_screen_spotlight', 'lock_screen_fun_facts', 'lock_screen_notifications'
            ]]
        elif tab_name == "Панель задач":
            return [s for s in all_settings if s['type'] in [
                'taskbar_contacts', 'taskbar_search', 'taskbar_meet_now',
                'taskbar_news', 'taskbar_bing_search'
            ]]
        elif tab_name == "Другие настройки":
            return [s for s in all_settings if s['type'] in [
                'disable_feedback', 'disable_remote_assistance', 'disable_remote_desktop',
                'disable_kms', 'disable_maps_update', 'disable_maps_traffic',
                'disable_pc_health', 'disable_ncsi', 'disable_store_auto_install',
                'disable_windows_tips', 'disable_wmp_diagnostics'
            ]]
        else:
            return []
