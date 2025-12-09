from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QHBoxLayout, QTabWidget)
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
            "app_telemetry": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                "name": "AllowTelemetry",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "diagnostic_data": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy",
                "name": "TailoredExperiencesWithDiagnosticDataEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "diagnostic_logs": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack",
                "name": "EnableDiagnostics",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "one_settings": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\OneSettings",
                "name": "DisableOneSettingsDownloads",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "account_info": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userAccountInformation",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "diagnostic_info": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "location": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "camera": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "microphone": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "notifications": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\notifications",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "motion": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\activity",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "contacts": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\contacts",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "calendar": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appointments",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "phone_calls": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\phoneCall",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "call_history": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\phoneCallHistory",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "email": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\email",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "tasks": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userDataTasks",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "messages": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\chat",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "radios": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\radios",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "unpaired_devices": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetoothSync",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "documents": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\documentsLibrary",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "pictures": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\picturesLibrary",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "videos": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\videosLibrary",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "file_system": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\broadFileSystemAccess",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "wireless": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\wifiDirect",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "eye_tracking": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\gazeInput",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "app_launch_tracking": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "Start_TrackProgs",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "voice_activation": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\speechRecognition",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "voice_activation_lock": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps",
                "name": "AgentActivationEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "headset_button": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\headsetButton",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "background_apps": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                "name": "GlobalUserDisabled",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "handwriting_sharing": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\TextInput",
                "name": "AllowLinguisticDataCollection",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "handwriting_error_reporting": {
                "path": r"SOFTWARE\Microsoft\Input\Settings",
                "name": "EnableHwkErrorReports",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "advertising_id": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                "name": "Enabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "inventory_collector": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                "name": "DisableInventory",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "login_camera": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                "name": "DisableLogonCameraImage",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "ink_transfer": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\TextInput",
                "name": "DisableInkingDataTransmission",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "timeline_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-353698Enabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "bluetooth_ads": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                "name": "DisableBluetoothAdvertising",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "start_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SystemPaneSuggestionsEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "customer_experience": {
                "path": r"SOFTWARE\Microsoft\SQMClient\Windows",
                "name": "CEIPEnable",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "sms_backup": {
                "path": r"SOFTWARE\Microsoft\Messaging",
                "name": "CloudServiceSyncEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "error_reporting": {
                "path": r"SOFTWARE\Microsoft\Windows\Windows Error Reporting",
                "name": "Disabled",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "biometric": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\WinBio",
                "name": "DisableBiometrics",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "windows_tips": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SoftLandingEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "settings_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-338393Enabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "device_setup": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\UserProfileEngagement",
                "name": "ScoobeSystemSettingEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "app_notifications": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications",
                "name": "ToastEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "browser_language": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\LanguagePackManagement",
                "name": "PreventLanguageChange",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "text_suggestions": {
                "path": r"SOFTWARE\Microsoft\Input\Settings",
                "name": "EnableTextSuggestions",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "store_addresses": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Store",
                "name": "DisableStoreAddressTransmission",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "clipboard_history_user": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Clipboard",
                "name": "EnableClipboardHistory",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "activity_history": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ActivityDataLayer",
                "name": "EnableActivityFeed",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "activity_history_storage": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ActivityDataLayer",
                "name": "AllowLocalStorageOfActivities",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "activity_history_sync": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ActivityDataLayer",
                "name": "UploadUserActivities",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "clipboard_history_system": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\System",
                "name": "AllowClipboardHistory",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "clipboard_sync": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\System",
                "name": "AllowCrossDeviceClipboard",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "password_reveal": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\CredUI",
                "name": "DisablePasswordReveal",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "user_activity_recording": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\System",
                "name": "PublishUserActivities",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "telemetry_settings": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                "name": "AllowTelemetry",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "drm_internet": {
                "path": r"SOFTWARE\Policies\Microsoft\WMDRM",
                "name": "DisableOnline",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "location_service": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                "name": "Value",
                "value": "Deny" if self.enable else "Allow",
                "type": winreg.REG_SZ
            },
            "location_script": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3",
                "name": "2002",
                "value": 3 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "location_sensors": {
                "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}",
                "name": "SensorPermissionState",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "location_windows_service": {
                "path": r"SYSTEM\CurrentControlSet\Services\lfsvc\Service\Configuration",
                "name": "Status",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "spynet_membership": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Spynet",
                "name": "SpyNetReporting",
                "value": 0 if self.enable else 2,
                "type": winreg.REG_DWORD
            },
            "spynet_samples": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Spynet",
                "name": "SubmitSamplesConsent",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "infection_reporting": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Reporting",
                "name": "DisableGenericReports",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "mobile_connection": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\MobileDeviceManager",
                "name": "DisableEnrollment",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "edge_tracking": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "PersonalizationReportingEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_payment_check": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillCreditCardEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_personalized_ads": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "PersonalizationAdsEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_autofill_addresses": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillAddressEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_feedback": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "UserFeedbackAllowed",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_cards_autofill": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillCreditCardEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_form_fill": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_local_providers": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "LocalProvidersEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_search_suggestions": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SearchSuggestEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_shopping_assistant": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "ShoppingAssistantEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_sidebar": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "HubsSidebarEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_msaccount_button": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "MSASignInRestriction",
                "value": 1 if self.enable else 0,
                "type": winreg.REG_DWORD
            },
            "edge_spell_check": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SpellcheckEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_navigation_error": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AlternateErrorPagesEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_similar_sites": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "DNREnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_preload": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "NetworkPredictionOptions",
                "value": 2 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_password_save": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "PasswordManagerEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_site_safety": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SafeBrowsingProtectionLevel",
                "value": 0 if self.enable else 2,
                "type": winreg.REG_DWORD
            },
            "edge_ie_redirect": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "RedirectSitesFromInternetExplorerRedirectMode",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_smartscreen": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SmartScreenEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
            },
            "edge_typo_check": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "TyposquattingCheckerEnabled",
                "value": 0 if self.enable else 1,
                "type": winreg.REG_DWORD
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
            "app_telemetry": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                "name": "AllowTelemetry",
                "default": "1",
                "enabled_value": "0"
            },
            "diagnostic_data": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy",
                "name": "TailoredExperiencesWithDiagnosticDataEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "diagnostic_logs": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack",
                "name": "EnableDiagnostics",
                "default": "1",
                "enabled_value": "0"
            },
            "one_settings": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\OneSettings",
                "name": "DisableOneSettingsDownloads",
                "default": "0",
                "enabled_value": "1"
            },
            "account_info": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userAccountInformation",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "diagnostic_info": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "location": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "camera": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "microphone": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "notifications": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\notifications",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "motion": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\activity",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "contacts": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\contacts",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "calendar": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appointments",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "phone_calls": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\phoneCall",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "call_history": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\phoneCallHistory",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "email": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\email",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "tasks": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userDataTasks",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "messages": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\chat",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "radios": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\radios",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "unpaired_devices": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\bluetoothSync",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "documents": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\documentsLibrary",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "pictures": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\picturesLibrary",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "videos": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\videosLibrary",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "file_system": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\broadFileSystemAccess",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "wireless": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\wifiDirect",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "eye_tracking": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\gazeInput",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "app_launch_tracking": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "Start_TrackProgs",
                "default": "1",
                "enabled_value": "0"
            },
            "voice_activation": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\speechRecognition",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "voice_activation_lock": {
                "path": r"SOFTWARE\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps",
                "name": "AgentActivationEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "headset_button": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\headsetButton",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "background_apps": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                "name": "GlobalUserDisabled",
                "default": "0",
                "enabled_value": "1"
            },
            "handwriting_sharing": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\TextInput",
                "name": "AllowLinguisticDataCollection",
                "default": "1",
                "enabled_value": "0"
            },
            "handwriting_error_reporting": {
                "path": r"SOFTWARE\Microsoft\Input\Settings",
                "name": "EnableHwkErrorReports",
                "default": "1",
                "enabled_value": "0"
            },
            "advertising_id": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                "name": "Enabled",
                "default": "1",
                "enabled_value": "0"
            },
            "inventory_collector": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                "name": "DisableInventory",
                "default": "0",
                "enabled_value": "1"
            },
            "login_camera": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                "name": "DisableLogonCameraImage",
                "default": "0",
                "enabled_value": "1"
            },
            "ink_transfer": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\TextInput",
                "name": "DisableInkingDataTransmission",
                "default": "0",
                "enabled_value": "1"
            },
            "timeline_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-353698Enabled",
                "default": "1",
                "enabled_value": "0"
            },
            "bluetooth_ads": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                "name": "DisableBluetoothAdvertising",
                "default": "0",
                "enabled_value": "1"
            },
            "start_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SystemPaneSuggestionsEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "customer_experience": {
                "path": r"SOFTWARE\Microsoft\SQMClient\Windows",
                "name": "CEIPEnable",
                "default": "1",
                "enabled_value": "0"
            },
            "sms_backup": {
                "path": r"SOFTWARE\Microsoft\Messaging",
                "name": "CloudServiceSyncEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "error_reporting": {
                "path": r"SOFTWARE\Microsoft\Windows\Windows Error Reporting",
                "name": "Disabled",
                "default": "0",
                "enabled_value": "1"
            },
            "biometric": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\WinBio",
                "name": "DisableBiometrics",
                "default": "0",
                "enabled_value": "1"
            },
            "windows_tips": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SoftLandingEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "settings_suggestions": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-338393Enabled",
                "default": "1",
                "enabled_value": "0"
            },
            "device_setup": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\UserProfileEngagement",
                "name": "ScoobeSystemSettingEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "app_notifications": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications",
                "name": "ToastEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "browser_language": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\LanguagePackManagement",
                "name": "PreventLanguageChange",
                "default": "0",
                "enabled_value": "1"
            },
            "text_suggestions": {
                "path": r"SOFTWARE\Microsoft\Input\Settings",
                "name": "EnableTextSuggestions",
                "default": "1",
                "enabled_value": "0"
            },
            "store_addresses": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Store",
                "name": "DisableStoreAddressTransmission",
                "default": "0",
                "enabled_value": "1"
            },
            "password_reveal": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\CredUI",
                "name": "DisablePasswordReveal",
                "default": "0",
                "enabled_value": "1"
            },
            "user_activity_recording": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\System",
                "name": "PublishUserActivities",
                "default": "1",
                "enabled_value": "0"
            },
            "telemetry_settings": {
                "path": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                "name": "AllowTelemetry",
                "default": "1",
                "enabled_value": "0"
            },
            "drm_internet": {
                "path": r"SOFTWARE\Policies\Microsoft\WMDRM",
                "name": "DisableOnline",
                "default": "0",
                "enabled_value": "1"
            },
            "location_service": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                "name": "Value",
                "default": "Allow",
                "enabled_value": "Deny"
            },
            "location_script": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3",
                "name": "2002",
                "default": "0",
                "enabled_value": "3"
            },
            "location_sensors": {
                "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}",
                "name": "SensorPermissionState",
                "default": "1",
                "enabled_value": "0"
            },
            "location_windows_service": {
                "path": r"SYSTEM\CurrentControlSet\Services\lfsvc\Service\Configuration",
                "name": "Status",
                "default": "1",
                "enabled_value": "0"
            },
            "spynet_membership": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Spynet",
                "name": "SpyNetReporting",
                "default": "2",
                "enabled_value": "0"
            },
            "spynet_samples": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Spynet",
                "name": "SubmitSamplesConsent",
                "default": "1",
                "enabled_value": "0"
            },
            "infection_reporting": {
                "path": r"SOFTWARE\Microsoft\Windows Defender\Reporting",
                "name": "DisableGenericReports",
                "default": "0",
                "enabled_value": "1"
            },
            "mobile_connection": {
                "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\MobileDeviceManager",
                "name": "DisableEnrollment",
                "default": "0",
                "enabled_value": "1"
            },
            "edge_tracking": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "TrackingPrevention",
                "default": "0",
                "enabled_value": "1"
            },
            "edge_payment_check": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillCreditCardEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_personalized_ads": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "PersonalizedAdsEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_autofill_addresses": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillAddressEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_feedback": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "UserFeedbackAllowed",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_cards_autofill": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillCreditCardEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_form_fill": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AutofillEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_local_providers": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "LocalProvidersEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_search_suggestions": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SearchSuggestEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_shopping_assistant": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "ShoppingAssistantEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_sidebar": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "HubsSidebarEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_msaccount_button": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "MSASignInRestriction",
                "default": "0",
                "enabled_value": "1"
            },
            "edge_spell_check": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SpellcheckEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_navigation_error": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "AlternateErrorPagesEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_similar_sites": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "DNREnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_preload": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "NetworkPredictionOptions",
                "default": "1",
                "enabled_value": "2"
            },
            "edge_password_save": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "PasswordManagerEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_site_safety": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SafeBrowsingProtectionLevel",
                "default": "2",
                "enabled_value": "0"
            },
            "edge_ie_redirect": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "RedirectSitesFromInternetExplorerRedirectMode",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_smartscreen": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "SmartScreenEnabled",
                "default": "1",
                "enabled_value": "0"
            },
            "edge_typo_protection": {
                "path": r"SOFTWARE\Policies\Microsoft\Edge",
                "name": "TyposquattingCheckerEnabled",
                "default": "1",
                "enabled_value": "0"
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


class PrivacyPage(QWidget):
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

        diagnostic_tab = self.create_tab("Диагностические данные")
        confidentiality_tab = self.create_tab("Конфиденциальность приложений и данных")
        history_clipboard = self.create_tab("История активности и клипборд")
        satefy_settings_tab = self.create_tab("Параметры безопасности")
        microsoft_tab = self.create_tab("Microsoft Edge")
        location_tab = self.create_tab("Местоположение")
        msdefender_spynet_tab = self.create_tab("MS Defender и MS SpyNet")
        mobile_tab = self.create_tab("Мобильные устройства")

        tab_widget.addTab(diagnostic_tab, "Диагностические данные")
        tab_widget.addTab(confidentiality_tab, "Конфиденциальность приложений и данных")
        tab_widget.addTab(history_clipboard, "История активности и клипборд")
        tab_widget.addTab(satefy_settings_tab, "Параметры безопасности")
        tab_widget.addTab(microsoft_tab, "Microsoft Edge")
        tab_widget.addTab(location_tab, "Местоположение")
        tab_widget.addTab(msdefender_spynet_tab, "MS Defender и MS SpyNet")
        tab_widget.addTab(mobile_tab, "Мобильные устройства")

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
                'type': 'app_telemetry',
                'title': 'Отключить телеметрию приложения',
                'description': 'Отключает сбор данных о работе приложений и отправку их в Microsoft',
                'impact': 'Повышение приватности, небольшое снижение нагрузки на систему',
                'safety': 'Безопасно. Не влияет на работу системы'
            },
            {
                'type': 'diagnostic_data',
                'title': 'Отключить использование диагностических данных',
                'description': 'Отключает использование диагностических данных для унификации пользовательского опыта',
                'impact': 'Повышение приватности, отключение персонализированных рекомендаций',
                'safety': 'Безопасно. Может снизить удобство использования некоторых функций Windows'
            },
            {
                'type': 'diagnostic_logs',
                'title': 'Отключение сбора журналов диагностики',
                'description': 'Отключает сбор и отправку журналов диагностики в Microsoft',
                'impact': 'Повышение приватности, экономия места на диске',
                'safety': 'Безопасно. Может затруднить диагностику проблем'
            },
            {
                'type': 'one_settings',
                'title': 'Отключение загрузки параметров OneSettings',
                'description': 'Отключает автоматическую загрузку параметров конфигурации OneSettings',
                'impact': 'Снижение сетевой активности, повышение приватности',
                'safety': 'Безопасно. Может потребоваться ручная настройка некоторых параметров'
            },
            {
                'type': 'account_info',
                'title': 'Отключить доступ приложения к информации учетной записи пользователя',
                'description': 'Запрещает приложениям доступ к данным учетной записи пользователя',
                'impact': 'Повышение приватности, некоторые приложения могут потребовать ручной ввод данных',
                'safety': 'Безопасно. Можно включить для отдельных приложений при необходимости'
            },
            {
                'type': 'diagnostic_info',
                'title': 'Отключить доступ приложения к диагностической информации',
                'description': 'Запрещает приложениям доступ к диагностической информации системы',
                'impact': 'Повышение приватности, может затруднить диагностику проблем',
                'safety': 'Безопасно. Можно временно включить при необходимости'
            },
            {
                'type': 'location',
                'title': 'Отключить доступ приложения к местоположению устройства',
                'description': 'Запрещает приложениям доступ к данным о местоположении',
                'impact': 'Повышение приватности, отключение функций на основе местоположения',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'camera',
                'title': 'Отключить доступ к камере',
                'description': 'Запрещает приложениям доступ к камере устройства',
                'impact': 'Повышение приватности, отключение функций видеосвязи',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'microphone',
                'title': 'Отключить доступ к микрофону',
                'description': 'Запрещает приложениям доступ к микрофону устройства',
                'impact': 'Повышение приватности, отключение функций голосовой связи',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'notifications',
                'title': 'Отключить уведомления',
                'description': 'Запрещает приложениям отправку уведомлений на рабочий стол',
                'impact': 'Повышение приватности, уменьшение отвлекающих уведомлений',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'motion',
                'title': 'Отключить доступ к активности пользователя',
                'description': 'Запрещает приложениям доступ к данным о движениях пользователя',
                'impact': 'Повышение приватности, отключение функций управления жестами',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'contacts',
                'title': 'Отключить доступ к контактам',
                'description': 'Запрещает приложениям доступ к списку контактов пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации контактов',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'calendar',
                'title': 'Отключить доступ к календарю',
                'description': 'Запрещает приложениям доступ к календарю пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации календаря',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'phone_calls',
                'title': 'Отключить доступ к звонкам',
                'description': 'Запрещает приложениям доступ к данным о звонках пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации звонков',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'call_history',
                'title': 'Отключить доступ к истории звонков',
                'description': 'Запрещает приложениям доступ к истории звонков пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации звонков',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'email',
                'title': 'Отключить доступ к почте',
                'description': 'Запрещает приложениям доступ к почтовому ящику пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации почты',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'tasks',
                'title': 'Отключить доступ к задачам',
                'description': 'Запрещает приложениям доступ к задачам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации задач',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'messages',
                'title': 'Отключить доступ к сообщениям',
                'description': 'Запрещает приложениям доступ к сообщениям пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации сообщений',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'radios',
                'title': 'Отключить доступ к радио',
                'description': 'Запрещает приложениям доступ к радиоустройствам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации радио',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'unpaired_devices',
                'title': 'Отключить доступ к устройствам',
                'description': 'Запрещает приложениям доступ к устройствам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации устройств',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'documents',
                'title': 'Отключить доступ к документам',
                'description': 'Запрещает приложениям доступ к документам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации документов',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'pictures',
                'title': 'Отключить доступ к изображениям',
                'description': 'Запрещает приложениям доступ к изображениям пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации изображений',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'videos',
                'title': 'Отключить доступ к видео',
                'description': 'Запрещает приложениям доступ к видеофайлам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации видео',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'file_system',
                'title': 'Отключить доступ к файловой системе',
                'description': 'Запрещает приложениям доступ к файловой системе пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации файлов',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'wireless',
                'title': 'Отключить доступ к беспроводным устройствам',
                'description': 'Запрещает приложениям доступ к беспроводным устройствам пользователя',
                'impact': 'Повышение приватности, отключение функций синхронизации беспроводных устройств',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'eye_tracking',
                'title': 'Отключить доступ к системе отслеживания взгляда',
                'description': 'Запрещает приложениям доступ к системе отслеживания взгляда пользователя',
                'impact': 'Повышение приватности, отключение функций управления взглядом',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'app_launch_tracking',
                'title': 'Отключить отслеживание запуска приложений',
                'description': 'Отключает отслеживание запуска приложений для улучшения рекомендаций',
                'impact': 'Повышение приватности, отключение персонализированных рекомендаций',
                'safety': 'Безопасно. Можно включить для улучшения рекомендаций'
            },
            {
                'type': 'voice_activation',
                'title': 'Отключить активацию голосом',
                'description': 'Отключает активацию голосовых команд для улучшения приватности',
                'impact': 'Повышение приватности, отключение функций голосового управления',
                'safety': 'Безопасно. Можно включить для улучшения управления'
            },
            {
                'type': 'voice_activation_lock',
                'title': 'Отключить активацию голосом для всех приложений',
                'description': 'Отключает активацию голосовых команд для всех приложений',
                'impact': 'Повышение приватности, отключение функций голосового управления',
                'safety': 'Безопасно. Можно включить для улучшения управления'
            },
            {
                'type': 'headset_button',
                'title': 'Отключить доступ к кнопке на наушниках',
                'description': 'Запрещает приложениям доступ к кнопке на наушниках пользователя',
                'impact': 'Повышение приватности, отключение функций управления наушниками',
                'safety': 'Безопасно. Можно включить для отдельных приложений'
            },
            {
                'type': 'background_apps',
                'title': 'Отключить фоновые приложения',
                'description': 'Отключает запуск фоновых приложений для экономии ресурсов',
                'impact': 'Экономия ресурсов, повышение производительности',
                'safety': 'Безопасно. Можно включить для улучшения работы некоторых приложений'
            },
            {
                'type': 'handwriting_sharing',
                'title': 'Запретить совместное использование данных рукописного ввода',
                'description': 'Отключает отправку данных рукописного ввода в Microsoft',
                'impact': 'Повышение приватности, отключение улучшений распознавания рукописного ввода',
                'safety': 'Безопасно. Не влияет на основную функциональность рукописного ввода'
            },
            {
                'type': 'handwriting_error_reporting',
                'title': 'Отключить отчет об ошибках при рукописном вводе текста',
                'description': 'Отключает отправку отчетов об ошибках рукописного ввода',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'advertising_id',
                'title': 'Отключить и сбросить идентификатор рекламы',
                'description': 'Отключает отслеживание для персонализированной рекламы',
                'impact': 'Повышение приватности, менее релевантная реклама',
                'safety': 'Безопасно'
            },
            {
                'type': 'inventory_collector',
                'title': 'Отключить сборщика данных инвентаризации',
                'description': 'Отключает сбор данных об установленном ПО и оборудовании',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'login_camera',
                'title': 'Отключить камеру в экране входа в систему',
                'description': 'Отключает использование камеры на экране входа',
                'impact': 'Повышение безопасности и приватности',
                'safety': 'Безопасно. Не влияет на работу камеры после входа в систему'
            },
            {
                'type': 'ink_transfer',
                'title': 'Отключить передачу рукописного текста',
                'description': 'Отключает передачу данных рукописного ввода',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'timeline_suggestions',
                'title': 'Отключить показ предложений в хронике',
                'description': 'Отключает показ рекомендаций в timeline Windows',
                'impact': 'Меньше отвлекающих элементов',
                'safety': 'Безопасно'
            },
            {
                'type': 'bluetooth_ads',
                'title': 'Отключить рекламу через Bluetooth',
                'description': 'Отключает рекламные сообщения через Bluetooth',
                'impact': 'Повышение приватности, меньше рекламы',
                'safety': 'Безопасно'
            },
            {
                'type': 'start_suggestions',
                'title': 'Отключить предложения в Start',
                'description': 'Отключает рекомендации в меню Пуск',
                'impact': 'Чистое меню Пуск без рекламы',
                'safety': 'Безопасно'
            },
            {
                'type': 'customer_experience',
                'title': 'Отключение программы улучшения качества обслуживания клиентов Windows',
                'description': 'Отключает отправку данных об использовании Windows',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'sms_backup',
                'title': 'Отключить резервное копирование SMS-сообщений в облако',
                'description': 'Отключает автоматическое резервное копирование SMS в облако',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно. SMS останутся только на устройстве'
            },
            {
                'type': 'error_reporting',
                'title': 'Отключение сообщения об ошибках Windows',
                'description': 'Отключает автоматическую отправку отчетов об ошибках',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно. Может затруднить диагностику проблем'
            },
            {
                'type': 'biometric',
                'title': 'Отключить биометрические характеристики',
                'description': 'Отключает использование биометрических данных',
                'impact': 'Повышение безопасности',
                'safety': 'Безопасно. Потребуется использовать альтернативные методы входа'
            },
            {
                'type': 'windows_tips',
                'title': 'Отключить советы, подсказки и рекомендации при использовании Windows',
                'description': 'Отключает все подсказки и рекомендации Windows',
                'impact': 'Меньше отвлекающих элементов',
                'safety': 'Безопасно'
            },
            {
                'type': 'settings_suggestions',
                'title': 'Отключение показа предлагаемого содержимого в приложении "Настройки"',
                'description': 'Отключает рекомендации в приложении Настройки',
                'impact': 'Чистый интерфейс без рекламы',
                'safety': 'Безопасно'
            },
            {
                'type': 'device_setup',
                'title': 'Отключить возможность предложить завершить настройку устройства',
                'description': 'Отключает предложения о дополнительной настройке',
                'impact': 'Меньше уведомлений',
                'safety': 'Безопасно'
            },
            {
                'type': 'app_notifications',
                'title': 'Отключить уведомления приложений',
                'description': 'Отключает все уведомления от приложений',
                'impact': 'Меньше отвлекающих факторов',
                'safety': 'Безопасно. Можно настроить для отдельных приложений'
            },
            {
                'type': 'browser_language',
                'title': 'Запретить доступ к языковым настройкам браузера',
                'description': 'Запрещает приложениям менять языковые настройки',
                'impact': 'Повышение безопасности',
                'safety': 'Безопасно'
            },
            {
                'type': 'text_suggestions',
                'title': 'Отключить текстовые предложения при наборе текста',
                'description': 'Отключает подсказки при вводе текста',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'store_addresses',
                'title': 'Отключить передачу интернет-адресов в Windows Store',
                'description': 'Отключает отправку посещенных адресов в Store',
                'impact': 'Повышение приватности',
                'safety': 'Безопасно'
            },
            {
                'type': 'clipboard_history_user',
                'title': 'Отключить хранение истории буфера обмена для текущих пользователей',
                'description': 'Отключает сохранение истории буфера обмена для текущего пользователя Windows',
                'impact': 'Повышение приватности, уменьшение использования памяти',
                'safety': 'Безопасно. Будет доступно только последнее скопированное содержимое'
            },
            {
                'type': 'activity_history',
                'title': 'Отключить записи активности пользователя',
                'description': 'Отключает запись действий пользователя в системе Windows',
                'impact': 'Повышение приватности, отсутствие истории действий',
                'safety': 'Безопасно. Может затруднить восстановление предыдущих действий'
            },
            {
                'type': 'activity_history_storage',
                'title': 'Отключить сохранение истории активности пользователей',
                'description': 'Отключает сохранение истории действий пользователя на локальном компьютере',
                'impact': 'Повышение приватности, экономия места на диске',
                'safety': 'Безопасно. История действий не будет сохраняться'
            },
            {
                'type': 'activity_history_sync',
                'title': 'Отключить отправку действий пользователей в Microsoft',
                'description': 'Отключает синхронизацию истории действий с серверами Microsoft',
                'impact': 'Повышение приватности, снижение сетевого трафика',
                'safety': 'Безопасно. Отключает облачную синхронизацию действий'
            },
            {
                'type': 'clipboard_history_system',
                'title': 'Отключить хранение истории буфера обмена для целых компьютеров',
                'description': 'Полностью отключает функцию истории буфера обмена на уровне системы',
                'impact': 'Максимальная приватность буфера обмена, экономия ресурсов',
                'safety': 'Безопасно. Отключает все функции истории буфера обмена'
            },
            {
                'type': 'clipboard_sync',
                'title': 'Отключить перенос буфера обмена на другие устройства через облако',
                'description': 'Отключает синхронизацию буфера обмена между устройствами через облако Microsoft',
                'impact': 'Повышение приватности, отключение облачной синхронизации',
                'safety': 'Безопасно. Буфер обмена будет работать только локально'
            },
            {
                'type': 'password_reveal',
                'title': 'Отключить кнопку раскрытия пароля',
                'description': 'Отключает кнопку, позволяющую показать введенный пароль в полях ввода',
                'impact': 'Повышение безопасности при вводе паролей',
                'safety': 'Безопасно. Усложняет проверку правильности ввода пароля'
            },
            {
                'type': 'user_activity_recording',
                'title': 'Отключение записи действий пользователя',
                'description': 'Отключает запись и хранение истории действий пользователя в системе',
                'impact': 'Повышение приватности, уменьшение размера системных логов',
                'safety': 'Безопасно. Может затруднить восстановление истории действий'
            },
            {
                'type': 'telemetry_settings',
                'title': 'Отключить телеметрию',
                'description': 'Полностью отключает сбор и отправку телеметрических данных в Microsoft',
                'impact': 'Максимальное повышение приватности, снижение сетевой активности',
                'safety': 'Безопасно. Может затруднить получение автоматических исправлений'
            },
            {
                'type': 'drm_internet',
                'title': 'Отключить Windows Media DRM доступ к интернету',
                'description': 'Отключает возможность Windows Media DRM подключаться к интернету',
                'impact': 'Повышение приватности, контроль сетевого доступа',
                'safety': 'Безопасно. Может ограничить воспроизведение защищенного контента'
            },
            {
                'type': 'location_service',
                'title': 'Отключить функцию местоположения',
                'description': 'Полностью отключает службу определения местоположения Windows',
                'impact': 'Приложения не смогут получать данные о местоположении',
                'safety': 'Безопасно. Может ограничить функциональность карт и погоды'
            },
            {
                'type': 'location_script',
                'title': 'Отключить функции скрипта для определения местонахождения',
                'description': 'Запрещает скриптам определять ваше местоположение',
                'impact': 'Повышение приватности при работе в браузере',
                'safety': 'Безопасно. Может потребоваться ручной ввод местоположения'
            },
            {
                'type': 'location_sensors',
                'title': 'Отключить датчики позиционирования',
                'description': 'Отключает все датчики, используемые для определения местоположения',
                'impact': 'Полное отключение функций геолокации',
                'safety': 'Безопасно. Влияет на работу приложений с геолокацией'
            },
            {
                'type': 'location_windows_service',
                'title': 'Отключить службы Windows для определения местонахождения',
                'description': 'Отключает системные службы геолокации Windows',
                'impact': 'Системные службы не смогут отслеживать местоположение',
                'safety': 'Безопасно. Может потребоваться перезагрузка'
            },
            {
                'type': 'spynet_membership',
                'title': 'Отключить членство Microsoft SpyNet',
                'description': 'Отключает участие в сети Microsoft SpyNet',
                'impact': 'Прекращение отправки данных в сеть SpyNet',
                'safety': 'Безопасно. Может снизить эффективность обнаружения угроз'
            },
            {
                'type': 'spynet_samples',
                'title': 'Отключить отправку проб данных',
                'description': 'Отключает отправку образцов файлов в Microsoft',
                'impact': 'Повышение приватности, файлы не отправляются для анализа',
                'safety': 'Безопасно. Может снизить точность определения угроз'
            },
            {
                'type': 'infection_reporting',
                'title': 'Не отсылать информацию о заражении',
                'description': 'Отключает автоматическую отправку отчетов о вирусах',
                'impact': 'Microsoft не получает данные о заражениях',
                'safety': 'Безопасно. Требует ручной отправки отчетов при необходимости'
            },
            {
                'type': 'mobile_connection',
                'title': 'Отключение подключения к мобильным устройствам',
                'description': 'Отключает возможность подключения мобильных устройств к ПК',
                'impact': 'Повышение безопасности, ограничение доступа мобильных устройств',
                'safety': 'Безопасно. Потребуется ручное разрешение подключений'
            },
            {
                'type': 'edge_tracking',
                'title': 'Отключить отслеживание пользователей в Интернете',
                'description': 'Отключает сбор данных о поведении пользователя при просмотре веб-страниц',
                'impact': 'Повышение приватности при использовании браузера',
                'safety': 'Безопасно. Может снизить персонализацию контента'
            },
            {
                'type': 'edge_payment_check',
                'title': 'Отключить проверку сохраненных способов оплаты',
                'description': 'Отключает проверку и использование сохраненных способов оплаты веб-сайтами',
                'impact': 'Повышение безопасности платежных данных',
                'safety': 'Безопасно. Потребуется ручной ввод платежных данных'
            },
            {
                'type': 'edge_personalized_ads',
                'title': 'Отключить персонализацию рекламы и контента',
                'description': 'Отключает персонализацию рекламы, поиска, новостей и других услуг',
                'impact': 'Повышение приватности, менее релевантная реклама',
                'safety': 'Безопасно. Не влияет на функциональность'
            },
            {
                'type': 'edge_autofill_addresses',
                'title': 'Отключить автозаполнение адресов',
                'description': 'Отключает автоматическое заполнение веб-адресов в адресной строке',
                'impact': 'Повышение приватности при навигации',
                'safety': 'Безопасно. Потребуется ручной ввод адресов'
            },
            {
                'type': 'edge_feedback',
                'title': 'Отключить обратную связь',
                'description': 'Отключает сбор обратной связи с пользователем на панели инструментов',
                'impact': 'Отключение отправки отзывов в Microsoft',
                'safety': 'Безопасно. Не влияет на работу браузера'
            },
            {
                'type': 'edge_cards_autofill',
                'title': 'Отключить автозаполнение карт',
                'description': 'Отключение автоматического хранения и заполнения данных кредитных карт',
                'impact': 'Повышение безопасности платежных данных',
                'safety': 'Безопасно. Потребуется ручной ввод данных карт'
            },
            {
                'type': 'edge_form_fill',
                'title': 'Отключить автозаполнение форм',
                'description': 'Отключить предложения заполнения формуляров в Microsoft Edge',
                'impact': 'Повышение приватности при работе с формами',
                'safety': 'Безопасно. Потребуется ручной ввод данных'
            },
            {
                'type': 'edge_local_providers',
                'title': 'Отключить локальных провайдеров',
                'description': 'Отключить предложения от местных поставщиков',
                'impact': 'Отключение локальных рекомендаций',
                'safety': 'Безопасно. Не влияет на основные функции'
            },
            {
                'type': 'edge_search_suggestions',
                'title': 'Отключить поисковые предложения',
                'description': 'Отключить предложения вариантов поисковых запросов и веб-адресов',
                'impact': 'Повышение приватности при поиске',
                'safety': 'Безопасно. Может замедлить поиск'
            },
            {
                'type': 'edge_shopping_assistant',
                'title': 'Отключить помощник по покупкам',
                'description': 'Отключение помощника по покупкам в Microsoft Edge',
                'impact': 'Отключение рекомендаций по покупкам',
                'safety': 'Безопасно. Не влияет на покупки'
            },
            {
                'type': 'edge_sidebar',
                'title': 'Отключить боковую панель',
                'description': 'Отключение боковой панели в Microsoft Edge',
                'impact': 'Упрощение интерфейса браузера',
                'safety': 'Безопасно. Можно включить вручную'
            },
            {
                'type': 'edge_msaccount_button',
                'title': 'Отключить кнопку входа в учетную запись',
                'description': 'Отключение кнопки входа в учетную запись Майкрософт',
                'impact': 'Упрощение интерфейса, повышение приватности',
                'safety': 'Безопасно. Вход возможен через настройки'
            },
            {
                'type': 'edge_spell_check',
                'title': 'Отключить проверку орфографии',
                'description': 'Отключите расширенную проверку орфографии',
                'impact': 'Отключение отправки текста на серверы Microsoft',
                'safety': 'Безопасно. Базовая проверка работает локально'
            },
            {
                'type': 'edge_navigation_error',
                'title': 'Отключить веб-сервис навигации',
                'description': 'Отключить использование веб-сервиса для устранения ошибок навигации',
                'impact': 'Повышение приватности при ошибках навигации',
                'safety': 'Безопасно. Стандартные ошибки остаются'
            },
            {
                'type': 'edge_similar_sites',
                'title': 'Отключить похожие сайты',
                'description': 'Отключить предложение подобных сайтов при ошибках',
                'impact': 'Отключение рекомендаций похожих сайтов',
                'safety': 'Безопасно. Не влияет на навигацию'
            },
            {
                'type': 'edge_preload',
                'title': 'Отключить предзагрузку',
                'description': 'Отключить предварительную загрузку страниц',
                'impact': 'Снижение использования трафика',
                'safety': 'Безопасно. Может замедлить навигацию'
            },
            {
                'type': 'edge_password_save',
                'title': 'Отключить сохранение паролей',
                'description': 'Отключение сохранения паролей для веб-сайтов',
                'impact': 'Повышение безопасности учетных данных',
                'safety': 'Безопасно. Требует ручной ввод паролей'
            },
            {
                'type': 'edge_site_safety',
                'title': 'Отключить проверку безопасности',
                'description': 'Отключение служб безопасности сайта',
                'impact': 'Повышение приватности при просмотре',
                'safety': 'Может снизить защиту от вредоносных сайтов'
            },
            {
                'type': 'edge_ie_redirect',
                'title': 'Отключить перенаправление IE',
                'description': 'Отключение автоматического перенаправления из Internet Explorer',
                'impact': 'Отключение автоматического перехода в Edge',
                'safety': 'Безопасно. Не влияет на работу браузера'
            },
            {
                'type': 'edge_smartscreen',
                'title': 'Отключить SmartScreen',
                'description': 'Отключает фильтр SmartScreen',
                'impact': 'Отсутствие проверки безопасности сайтов',
                'safety': 'Требует осторожности при посещении неизвестных сайтов'
            },
            {
                'type': 'edge_typo_protection',
                'title': 'Отключить проверку опечаток',
                'description': 'Отключает проверку опечаток в адресах сайтов',
                'impact': 'Отсутствие защиты от опечаток в URL',
                'safety': 'Требует внимательности при вводе адресов'
            }
        ]

        if tab_name == "Диагностические данные":
            return [s for s in all_settings if s['type'] in [
                'app_telemetry', 'diagnostic_data', 'diagnostic_logs', 'one_settings'
            ]]
        elif tab_name == "Конфиденциальность приложений и данных":
            return [s for s in all_settings if s['type'] in [
                'account_info', 'diagnostic_info', 'location', 'camera', 'microphone', 'notifications', 'motion',
                'contacts', 'calendar', 'phone_calls', 'call_history', 'email', 'tasks', 'messages', 'radios',
                'unpaired_devices', 'documents', 'pictures', 'videos', 'file_system', 'wireless', 'eye_tracking',
                'app_launch_tracking', 'voice_activation', 'voice_activation_lock', 'headset_button',
                'background_apps', 'handwriting_sharing', 'handwriting_error_reporting', 'advertising_id',
                'inventory_collector', 'login_camera', 'ink_transfer', 'timeline_suggestions', 'bluetooth_ads',
                'start_suggestions', 'customer_experience', 'sms_backup', 'error_reporting', 'biometric',
                'windows_tips', 'settings_suggestions', 'device_setup', 'app_notifications', 'browser_language',
                'text_suggestions', 'store_addresses'
            ]]
        elif tab_name == "История активности и клипборд":
            return [s for s in all_settings if s['type'] in [
                'clipboard_history_user', 'activity_history', 'activity_history_storage',
                'activity_history_sync', 'clipboard_history_system', 'clipboard_sync'
            ]]
        elif tab_name == "Параметры безопасности":
            return [s for s in all_settings if s['type'] in [
                'password_reveal', 'user_activity_recording', 'telemetry_settings', 'drm_internet'
            ]]
        elif tab_name == "Microsoft Edge":
            return [s for s in all_settings if s['type'] in [
                'edge_tracking', 'edge_payment_check', 'edge_personalized_ads', 'edge_autofill_addresses',
                'edge_feedback', 'edge_cards_autofill', 'edge_form_fill', 'edge_local_providers',
                'edge_search_suggestions', 'edge_shopping_assistant', 'edge_sidebar', 'edge_msaccount_button',
                'edge_spell_check', 'edge_navigation_error', 'edge_similar_sites', 'edge_preload',
                'edge_password_save', 'edge_site_safety', 'edge_ie_redirect', 'edge_smartscreen',
                'edge_typo_protection'
            ]]
        elif tab_name == "Местоположение":
            return [s for s in all_settings if s['type'] in [
                'location_service', 'location_script', 'location_sensors', 'location_windows_service'
            ]]
        elif tab_name == "MS Defender и MS SpyNet":
            return [s for s in all_settings if s['type'] in [
                'spynet_membership', 'spynet_samples', 'infection_reporting'
            ]]
        elif tab_name == "Мобильные устройства":
            return [s for s in all_settings if s['type'] in [
                'mobile_connection'
            ]]
        else:
            return []
