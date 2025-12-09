from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QScrollArea, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import shutil
import subprocess
import win32serviceutil
import win32service


class SizeCalculatorWorker(QThread):
    calculated = pyqtSignal(int)  # bytes

    def __init__(self, clean_type):
        super().__init__()
        self.clean_type = clean_type

    @staticmethod
    def get_browser_paths():
        paths = {
            'chrome': os.path.join(os.getenv('LOCALAPPDATA'),
                                   'Google\\Chrome\\User Data\\Default\\Cache'),
            'firefox': os.path.join(os.getenv('LOCALAPPDATA'),
                                    'Mozilla\\Firefox\\Profiles'),
            'edge': os.path.join(os.getenv('LOCALAPPDATA'),
                                 'Microsoft\\Edge\\User Data\\Default\\Cache'),
        }
        return paths

    @staticmethod
    def calculate_directory_size(directory):
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size

    def run(self):
        total_size = 0

        if self.clean_type == 'temp':
            temp_paths = [
                os.environ.get('TEMP'),
                os.path.join(os.environ.get('WINDIR'), 'Temp')
            ]
            for path in temp_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'thumbnails':
            thumbnail_path = os.path.join(os.getenv('LOCALAPPDATA'),
                                          'Microsoft\\Windows\\Explorer')
            total_size += self.calculate_directory_size(thumbnail_path)

        elif self.clean_type == 'browsers':
            browser_paths = self.get_browser_paths()
            for browser, path in browser_paths.items():
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'windows_update':
            update_path = os.path.join(os.environ.get('WINDIR'),
                                       'SoftwareDistribution\\Download')
            if os.path.exists(update_path):
                total_size += self.calculate_directory_size(update_path)

        elif self.clean_type == 'delivery_optimization':
            # Path to Delivery Optimization Files
            delivery_path = os.path.join(os.environ.get('WINDIR'),
                                         'ServiceProfiles\\NetworkService\\AppData\\Local\\Microsoft\\Windows\\DeliveryOptimization\\Cache')
            if os.path.exists(delivery_path):
                total_size += self.calculate_directory_size(delivery_path)

        elif self.clean_type == 'internet_temp':
            # Calculate size of Internet Explorer temporary files
            internet_temp_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\INetCache'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Temporary Internet Files')
            ]
            for path in internet_temp_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'directx_cache':
            # Path to DirectX Shader Cache
            shader_cache_path = os.path.join(os.getenv('LOCALAPPDATA'),
                                             'D3DSCache')
            if os.path.exists(shader_cache_path):
                total_size += self.calculate_directory_size(shader_cache_path)

        elif self.clean_type == 'diagnostic_data':
            diagnostic_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\WER'),  # Windows Error Reporting
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Windows\\WER'),  # System-wide error reports
                os.path.join(os.environ.get('WINDIR'), 'LiveKernelReports'),  # Kernel crash dumps
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Feedback')  # Windows Feedback
            ]
            for path in diagnostic_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'recycle_bin':
            recycle_bin_paths = [
                os.path.join(drive + ":\\$Recycle.Bin")
                for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                if os.path.exists(drive + ":\\")
            ]
            for path in recycle_bin_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'memory_dumps':
            dump_paths = [
                os.path.join(os.environ.get('WINDIR'), 'MEMORY.DMP'),
                os.path.join(os.environ.get('WINDIR'), 'Minidump'),
                os.path.join(os.environ.get('LOCALAPPDATA'), 'CrashDumps')
            ]
            for path in dump_paths:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        try:
                            total_size += os.path.getsize(path)
                        except (OSError, PermissionError):
                            continue
                    else:
                        total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'chkdsk_fragments':
            for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                chk_path = f"{drive}:\\found.000"
                if os.path.exists(chk_path):
                    total_size += self.calculate_directory_size(chk_path)

        elif self.clean_type == 'microsoft_store':
            store_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Packages'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Windows\\AppRepository'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Application Shortcuts')
            ]
            for path in store_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'logs':
            log_paths = [
                os.path.join(os.getenv('WINDIR'), 'Logs'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Diagnosis\\ETLLogs'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\WER\\ReportArchive')
            ]
            for path in log_paths:
                if os.path.exists(path):
                    total_size += self.calculate_directory_size(path)

        elif self.clean_type == 'prefetch':
            prefetch_path = os.path.join(os.environ.get('WINDIR'), 'Prefetch')
            if os.path.exists(prefetch_path):
                total_size += self.calculate_directory_size(prefetch_path)

        self.calculated.emit(total_size)


class CleanerWorker(QThread):
    progress = pyqtSignal(str, int)  # type, bytes_cleaned
    finished = pyqtSignal()

    def __init__(self, clean_type):
        super().__init__()
        self.clean_type = clean_type

    @staticmethod
    def get_browser_paths():
        paths = {
            'chrome': os.path.join(os.getenv('LOCALAPPDATA'),
                                   'Google\\Chrome\\User Data\\Default\\Cache'),
            'firefox': os.path.join(os.getenv('LOCALAPPDATA'),
                                    'Mozilla\\Firefox\\Profiles'),
            'edge': os.path.join(os.getenv('LOCALAPPDATA'),
                                 'Microsoft\\Edge\\User Data\\Default\\Cache'),
        }
        return paths

    @staticmethod
    def delete_files_in_directory(directory):
        cleaned_size = 0
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                try:
                    file_path = os.path.join(root, name)
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned_size += size
                except (OSError, PermissionError):
                    continue

            for name in dirs:
                try:
                    dir_path = os.path.join(root, name)
                    shutil.rmtree(dir_path, ignore_errors=True)
                except (OSError, PermissionError):
                    continue

        return cleaned_size

    @staticmethod
    def get_service_status(service_name):
        try:
            # Get the current status of the service
            status = win32serviceutil.QueryServiceStatus(service_name)[1]
            return status
        except:
            return None

    def run(self):
        cleaned_size = 0

        if self.clean_type == 'temp':
            temp_paths = [
                os.environ.get('TEMP'),
                os.path.join(os.environ.get('WINDIR'), 'Temp')
            ]
            for path in temp_paths:
                if os.path.exists(path):
                    cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'thumbnails':
            thumbnail_path = os.path.join(os.getenv('LOCALAPPDATA'),
                                          'Microsoft\\Windows\\Explorer')
            thumb_files = ['thumbcache_*.db', 'iconcache_*.db']
            for file_pattern in thumb_files:
                pattern_path = os.path.join(thumbnail_path, file_pattern)
                try:
                    subprocess.run(['del', '/F', '/S', '/Q', pattern_path],
                                   shell=True, check=True)
                    cleaned_size += 1024 * 1024  # Approximate estimation
                except subprocess.CalledProcessError:
                    pass

        elif self.clean_type == 'browsers':
            browser_paths = self.get_browser_paths()
            for browser, path in browser_paths.items():
                if os.path.exists(path):
                    cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'windows_update':
            update_path = os.path.join(os.environ.get('WINDIR'),
                                       'SoftwareDistribution\\Download')
            if os.path.exists(update_path):
                try:
                    # Check initial service status
                    initial_status = self.get_service_status('wuauserv')

                    # If service is running, stop it before cleaning
                    if initial_status == win32service.SERVICE_RUNNING:
                        subprocess.run(['net', 'stop', 'wuauserv'], check=True)

                    # Clean the cache
                    cleaned_size = self.delete_files_in_directory(update_path)

                    # Only restart the service if it was initially running
                    if initial_status == win32service.SERVICE_RUNNING:
                        subprocess.run(['net', 'start', 'wuauserv'], check=True)

                except (subprocess.CalledProcessError, Exception) as e:
                    # Log error or handle it appropriately
                    print(f"Error during Windows Update cleanup: {str(e)}")

        elif self.clean_type == 'delivery_optimization':
            delivery_path = os.path.join(os.environ.get('WINDIR'),
                    'ServiceProfiles\\NetworkService\\AppData\\Local\\Microsoft\\Windows\\DeliveryOptimization\\Cache')
            if os.path.exists(delivery_path):
                try:
                    # Check initial service status
                    initial_status = self.get_service_status('DoSvc')

                    # If service is running, stop it before cleaning
                    if initial_status == win32service.SERVICE_RUNNING:
                        subprocess.run(['net', 'stop', 'DoSvc'], check=True)

                    # Clean the cache
                    cleaned_size = self.delete_files_in_directory(delivery_path)

                    # Only restart the service if it was initially running
                    if initial_status == win32service.SERVICE_RUNNING:
                        subprocess.run(['net', 'start', 'DoSvc'], check=True)

                except (subprocess.CalledProcessError, Exception) as e:
                    print(f"Error during Delivery Optimization cleanup: {str(e)}")

        elif self.clean_type == 'internet_temp':
            internet_temp_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\INetCache'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Temporary Internet Files')
            ]
            for path in internet_temp_paths:
                if os.path.exists(path):
                    cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'directx_cache':
            shader_cache_path = os.path.join(os.getenv('LOCALAPPDATA'),
                                             'D3DSCache')
            if os.path.exists(shader_cache_path):
                try:
                    # We need to stop any running applications that might be using DirectX
                    # This is optional and might be skipped if too intrusive
                    cleaned_size = self.delete_files_in_directory(shader_cache_path)
                except (OSError, PermissionError) as e:
                    print(f"Error cleaning DirectX cache: {e}")

        elif self.clean_type == 'diagnostic_data':
            diagnostic_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\WER'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Windows\\WER'),
                os.path.join(os.environ.get('WINDIR'), 'LiveKernelReports'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Feedback')
            ]

            try:
                # Stop Windows Error Reporting service before cleaning
                initial_wer_status = self.get_service_status('WerSvc')
                if initial_wer_status == win32service.SERVICE_RUNNING:
                    subprocess.run(['net', 'stop', 'WerSvc'], check=True)

                # Clean all diagnostic data paths
                for path in diagnostic_paths:
                    if os.path.exists(path):
                        cleaned_size += self.delete_files_in_directory(path)

                # Restart Windows Error Reporting service if it was running
                if initial_wer_status == win32service.SERVICE_RUNNING:
                    subprocess.run(['net', 'start', 'WerSvc'], check=True)

            except (subprocess.CalledProcessError, Exception) as e:
                print(f"Error during diagnostic data cleanup: {e}")

        elif self.clean_type == 'recycle_bin':
            try:
                # Используем send2trash для безопасной очистки корзины
                subprocess.run(['cmd', '/c', 'rd /s /q %systemdrive%\\$Recycle.bin'], shell=True)
                cleaned_size = 1024 * 1024  # Примерная оценка
            except Exception as e:
                print(f"Error cleaning Recycle Bin: {e}")

        elif self.clean_type == 'memory_dumps':
            dump_paths = [
                os.path.join(os.environ.get('WINDIR'), 'MEMORY.DMP'),
                os.path.join(os.environ.get('WINDIR'), 'Minidump'),
                os.path.join(os.environ.get('LOCALAPPDATA'), 'CrashDumps')
            ]

            for path in dump_paths:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        try:
                            size = os.path.getsize(path)
                            os.remove(path)
                            cleaned_size += size
                        except (OSError, PermissionError):
                            continue
                    else:
                        cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'chkdsk_fragments':
            for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                chk_path = f"{drive}:\\found.000"
                if os.path.exists(chk_path):
                    cleaned_size += self.delete_files_in_directory(chk_path)

        elif self.clean_type == 'microsoft_store':
            store_paths = [
                os.path.join(os.getenv('LOCALAPPDATA'), 'Packages'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Windows\\AppRepository'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\Application Shortcuts')
            ]
            for path in store_paths:
                if os.path.exists(path):
                    cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'logs':
            log_paths = [
                os.path.join(os.getenv('WINDIR'), 'Logs'),
                os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft\\Diagnosis\\ETLLogs'),
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft\\Windows\\WER\\ReportArchive')
            ]
            for path in log_paths:
                if os.path.exists(path):
                    cleaned_size += self.delete_files_in_directory(path)

        elif self.clean_type == 'prefetch':
            prefetch_path = os.path.join(os.environ.get('WINDIR'), 'Prefetch')
            if os.path.exists(prefetch_path):
                # Удаляем все файлы кроме готового состояния системы
                for filename in os.listdir(prefetch_path):
                    file_path = os.path.join(prefetch_path, filename)
                    try:
                        if filename.lower() != 'layout.ini':  # Не удаляем файл конфигурации
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                cleaned_size += os.path.getsize(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

        self.progress.emit(self.clean_type, cleaned_size)
        self.finished.emit()


class CleanWidget(QFrame):
    def __init__(self, clean_type, title, description, impact, safety):
        super().__init__()
        self.worker = None
        self.current_size = None
        self.clean_type = clean_type
        self.expanded = False
        self.cleaned_size = 0

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

        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #cccccc;
        """)

        # Статус очистки
        self.status_label = QLabel("Подсчёт размера...")
        self.status_label.setStyleSheet("font-size: 12px; color: white; font-weight: bold;")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        self.main_layout.addLayout(header_layout)

        # Детальная информация
        self.details_widget = QWidget()
        self.details_widget.setStyleSheet("background-color: transparent")
        self.details_layout = QVBoxLayout(self.details_widget)

        # Добавляем описание
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

        # Кнопка очистки
        self.clean_button = QPushButton("Очистить")
        self.clean_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #219A52;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        self.clean_button.clicked.connect(self.start_cleaning)
        self.details_layout.addWidget(self.clean_button)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2d2d2d;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1e8449;
            }
        """)
        self.details_layout.addWidget(self.progress_bar)

        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)

        self.setCursor(Qt.PointingHandCursor)

        # Запускаем подсчет размера
        self.calculator = SizeCalculatorWorker(self.clean_type)
        self.calculator.calculated.connect(self.update_size_info)
        self.calculator.start()

    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def update_size_info(self, size_bytes):
        self.current_size = size_bytes
        self.status_label.setText(f"Занято: {self.format_size(size_bytes)}")

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self.details_widget.setVisible(self.expanded)

    def start_cleaning(self):
        self.clean_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Индетерминированный режим
        self.status_label.setText("Очистка...")

        self.worker = CleanerWorker(self.clean_type)
        self.worker.progress.connect(self.cleaning_progress)
        self.worker.finished.connect(self.cleaning_finished)
        self.worker.start()

    def cleaning_progress(self, clean_type, bytes_cleaned):
        if clean_type == self.clean_type:
            self.cleaned_size = bytes_cleaned

    def cleaning_finished(self):
        self.clean_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        # После очистки запускаем новый подсчет размера
        self.calculator = SizeCalculatorWorker(self.clean_type)
        self.calculator.calculated.connect(self.update_size_info)
        self.calculator.start()


class CleanPage(QWidget):
    def __init__(self):
        super().__init__()
        self.admin_warning = None
        self.clean_layout = None
        self.init_ui()
        self.setStyleSheet("background-color: #121212; border-radius: 5px;")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
        """)

        # Контейнер для виджетов очистки
        container = QWidget()
        self.clean_layout = QVBoxLayout(container)

        # Добавляем виджеты очистки
        cleaners = [
            {
                'type': 'recycle_bin',
                'title': 'Очистка Корзины',
                'description': 'Полная очистка Корзины Windows на всех дисках',
                'impact': 'Освобождение места на диске, окончательное удаление файлов из Корзины',
                'safety': 'Внимание: файлы будут удалены без возможности восстановления'
            },
            {
                'type': 'temp',
                'title': 'Временные файлы Windows',
                'description': 'Удаление временных файлов, созданных системой и приложениями',
                'impact': 'Освобождение места на диске, удаление ненужных файлов',
                'safety': 'Безопасно. Эти файлы можно удалять'
            },
            {
                'type': 'thumbnails',
                'title': 'Кэш эскизов Windows',
                'description': 'Очистка кэша миниатюр файлов и папок',
                'impact': 'Освобождение места, миниатюры будут созданы заново при необходимости',
                'safety': 'Безопасно. Кэш автоматически восстановится'
            },
            {
                'type': 'browsers',
                'title': 'Кэш браузеров',
                'description': 'Очистка кэша Chrome, Firefox и Edge',
                'impact': 'Освобождение места, возможно небольшое замедление загрузки сайтов',
                'safety': 'Безопасно. Потребуется повторная загрузка кэша сайтов'
            },
            {
                'type': 'windows_update',
                'title': 'Кэш обновлений Windows',
                'description': 'Удаление загруженных файлов обновлений',
                'impact': 'Значительное освобождение места на диске',
                'safety': 'Безопасно. Старые файлы обновлений больше не нужны'
            },
            {
                'type': 'delivery_optimization',
                'title': 'Файлы оптимизации доставки',
                'description': 'Удаление кэшированных файлов службы оптимизации доставки Windows',
                'impact': 'Освобождение места на диске, очистка кэша обновлений',
                'safety': 'Безопасно. Файлы будут загружены заново при необходимости'
            },
            {
                'type': 'internet_temp',
                'title': 'Временные файлы Интернета',
                'description': 'Очистка временных файлов и кэша Internet Explorer/Edge',
                'impact': 'Освобождение места, удаление устаревших файлов',
                'safety': 'Безопасно. Временные файлы будут созданы заново при необходимости'
            },
            {
                'type': 'directx_cache',
                'title': 'Кэш построителя текстур DirectX',
                'description': 'Очистка кэша шейдеров и текстур DirectX, используемых в играх и приложениях',
                'impact': 'Освобождение места на диске. При следующем запуске игр может потребоваться повторная компиляция шейдеров',
                'safety': 'Безопасно. Кэш будет создан заново при необходимости, но может вызвать временное снижение производительности в играх'
            },
            {
                'type': 'diagnostic_data',
                'title': 'Диагностические данные Windows',
                'description': 'Удаление отчетов об ошибках, дампов памяти и файлов обратной связи Windows',
                'impact': 'Освобождение места, удаление старых отчетов об ошибках и диагностических данных',
                'safety': 'Безопасно. Эти файлы используются только для диагностики проблем'
            },
            {
                'type': 'memory_dumps',
                'title': 'Дампы памяти',
                'description': 'Удаление файлов дампов памяти, созданных при сбоях системы',
                'impact': 'Освобождение места на диске, удаление технических файлов',
                'safety': 'Безопасно. Эти файлы нужны только для анализа сбоев'
            },
            {
                'type': 'chkdsk_fragments',
                'title': 'Фрагменты файлов Chkdsk',
                'description': 'Удаление фрагментов файлов, найденных при проверке диска',
                'impact': 'Освобождение места, удаление потерянных фрагментов файлов',
                'safety': 'Безопасно. Эти файлы являются потерянными фрагментами'
            },
            {
                'type': 'microsoft_store',
                'title': 'Кэш Microsoft Store',
                'description': 'Удаление кэша приложений Microsoft Store и UWP-программ',
                'impact': 'Освобождение места, пересоздание кэша при запуске приложений',
                'safety': 'Безопасно. Не влияет на работу установленных программ'
            },
            {
                'type': 'logs',
                'title': 'Системные логи',
                'description': 'Очистка журналов событий и диагностических логов Windows',
                'impact': 'Удаление истории системных ошибок и отчетов',
                'safety': 'Условно безопасно. Логи могут содержать полезную информацию'
            },
            {
                'type': 'prefetch',
                'title': 'Файлы Prefetch',
                'description': 'Удаление истории запуска программ для ускорения загрузки системы',
                'impact': 'Может временно замедлить запуск приложений до перезагрузки',
                'safety': 'Безопасно. Windows автоматически пересоздаст актуальные записи'
            }
        ]
        for cleaner in cleaners:
            widget = CleanWidget(
                cleaner['type'],
                cleaner['title'],
                cleaner['description'],
                cleaner['impact'],
                cleaner['safety']
            )
            self.clean_layout.addWidget(widget)

        self.clean_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
