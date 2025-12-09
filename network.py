from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QGroupBox, QFormLayout, QSpinBox, QMessageBox, QTabWidget)
import wmi
import winreg


class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("NetworkPage")

        self.wmi_service = wmi.WMI()
        self.network_adapters = {}
        self.current_adapter = None

        self.init_ui()
        self.load_network_adapters()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Adapter selection area
        adapter_group = QGroupBox("Выбор сетевого адаптера")
        adapter_group.setStyleSheet("""
                    QGroupBox {
                        background-color: #121212;
                        border: 1px solid #34495e;
                        border-radius: 5px;
                        padding: 3px;
                        margin-top: 2ex;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 3px 0 3px;
                        color: white;
                    }
                """)
        adapter_layout = QVBoxLayout()

        # Combo box for adapter selection
        self.adapter_combo = QComboBox()
        self.adapter_combo.setMinimumWidth(300)
        self.adapter_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #121212;
                        color: white;
                        margin: 5px;
                        border: 1px solid #2c3e50;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QComboBox::drop-down {
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 15px;
                        border-left-width: 1px;
                        border-left-color: #2c3e50;
                        border-left-style: solid;
                        border-top-right-radius: 3px;
                        border-bottom-right-radius: 3px;
                    }
                    QComboBox::down-arrow {
                        image: url(down_arrow.png);
                    }
                """)
        self.adapter_combo.currentIndexChanged.connect(self.on_adapter_selected)

        adapter_layout.addWidget(self.adapter_combo)
        adapter_group.setLayout(adapter_layout)

        # Refresh button for adapters
        refresh_btn = QPushButton("Обновить список адаптеров")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.load_network_adapters)

        # Settings area
        self.settings_tab = QTabWidget()
        self.settings_tab.setStyleSheet("""
                    QTabWidget::pane {
                        border: 1px solid #2c3e50;
                        background: #121212;
                        border-radius: 5px;
                    }
                    QTabBar::tab {
                        background: #121212;
                        color: white;
                        padding: 5px;
                        border: 1px solid #34495e;
                        border-top-left-radius: 4px;
                        border-top-right-radius: 4px;
                    }
                    QTabBar::tab:selected, QTabBar::tab:hover {
                        background: #34495e;
                    }
                """)

        # Create tabs for different setting categories
        self.tcp_ip_tab = QWidget()
        self.ie_tab = QWidget()
        self.host_resolution_tab = QWidget()
        self.qos_tab = QWidget()
        self.gaming_tab = QWidget()
        self.retransmissions_tab = QWidget()
        self.memory_tab = QWidget()
        self.ports_tab = QWidget()

        self.setup_tcp_ip_tab()
        self.setup_ie_tab()
        self.setup_host_resolution_tab()
        self.setup_qos_tab()
        self.setup_gaming_tab()
        self.setup_retransmissions_tab()
        self.setup_memory_tab()
        self.setup_ports_tab()

        self.settings_tab.addTab(self.tcp_ip_tab, "TCP/IP Settings")
        self.settings_tab.addTab(self.ie_tab, "Internet Explorer")
        self.settings_tab.addTab(self.host_resolution_tab, "Host Resolution")
        self.settings_tab.addTab(self.qos_tab, "QoS Settings")
        self.settings_tab.addTab(self.gaming_tab, "Gaming Tweaks")
        self.settings_tab.addTab(self.retransmissions_tab, "Retransmissions")
        self.settings_tab.addTab(self.memory_tab, "Network Memory")
        self.settings_tab.addTab(self.ports_tab, "Port Allocation")

        # Button area
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Применить настройки")
        self.apply_btn.setStyleSheet("""
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
            }
        """)
        self.apply_btn.clicked.connect(self.apply_settings)
        self.reset_btn = QPushButton("Сбросить к стандартным")
        self.reset_btn.setStyleSheet("""
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
            }
        """)
        self.reset_btn.clicked.connect(self.reset_settings)

        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.apply_btn)

        # Add all components to main layout
        main_layout.addWidget(adapter_group)
        main_layout.addWidget(refresh_btn)
        main_layout.addWidget(self.settings_tab)
        main_layout.addLayout(button_layout)

        # Initially disable settings until adapter is selected
        self.settings_tab.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)

        # Set the overall style for the widget
        self.setStyleSheet("""
                    QWidget {
                        background-color: #121212;
                        color: white;
                        font-size: 12px;
                    }
                    QLabel {
                        color: white;
                    }
                    QSpinBox, QComboBox {
                        background-color: #34495e;
                        color: white;
                        border: 1px solid #2c3e50;
                        padding: 2px;
                        border-radius: 3px;
                    }
                """)

    def setup_tcp_ip_tab(self):
        layout = QFormLayout(self.tcp_ip_tab)

        # TCP Window Auto-Tuning
        tcp_tuning_label = QLabel("TCP Window Auto-Tuning:")
        tcp_tuning_label.setToolTip(
            """
Описание: Эта настройка позволяет автоматической настройке размера окна TCP в зависимости от условий сети. 
Это помогает оптимизировать производительность сети, автоматически изменяя размер окна для максимальной 
пропускной способности и уменьшения задержек. 
Дефолтное значение: normal
Рекомендуемое значение: normal (или disabled для очень медленных сетей)
            """)
        self.tcp_tuning_combo = QComboBox()
        self.tcp_tuning_combo.addItems(["disabled", "highly restricted", "restricted", "normal", "experimental"])
        layout.addRow(tcp_tuning_label, self.tcp_tuning_combo)

        # Windows Scaling heuristics
        win_scaling_label = QLabel("Windows Scaling heuristics:")
        win_scaling_label.setToolTip(
            """
Описание: Это алгоритмы масштабирования окна TCP, которые помогают эффективно использовать сетевые ресурсы и 
предотвращать перегрузки. Включение этой функции позволяет системе автоматически регулировать размеры окон для 
поддержания стабильного и быстрого соединения.
Дефолтное значение: enabled
Рекомендуемое значение: disabled (для повышения пропускной способности)
            """)
        self.win_scaling_combo = QComboBox()
        self.win_scaling_combo.addItems(["disabled", "enabled"])
        layout.addRow(win_scaling_label, self.win_scaling_combo)

        # Congestion Control Provider
        congestion_label = QLabel("Congestion Control Provider:")
        congestion_label.setToolTip(
            """
Описание: Управление перегрузками – это механизм, который помогает регулировать трафик в сети, чтобы избежать потерь 
пакетов и перегрузок. В Windows доступны несколько алгоритмов, таких как Compound TCP (ctcp) и CUBIC.
Дефолтное значение: ctcp
Рекомендуемое значение: ctcp (или cubic для высокоскоростных сетей)
            """)
        self.congestion_combo = QComboBox()
        self.congestion_combo.addItems(["default", "ctcp", "dctcp", "cubic", "newreno"])
        layout.addRow(congestion_label, self.congestion_combo)

        # RSS
        rss_label = QLabel("Receive-Side Scaling (RSS):")
        rss_label.setToolTip(
            """
Описание: RSS позволяет распределять обработку входящего сетевого трафика между несколькими процессорами, что уменьшает 
нагрузку на один процессор и улучшает общую производительность сети.
Дефолтное значение: enabled
Рекомендуемое значение: enabled
            """)
        self.rss_combo = QComboBox()
        self.rss_combo.addItems(["disabled", "enabled"])
        layout.addRow(rss_label, self.rss_combo)

        # RSC
        rsc_label = QLabel("R.Segment Coalescing (RSC):")
        rsc_label.setToolTip(
            """
Описание: RSC объединяет несколько сегментов TCP в один большой сегмент перед передачей на сетевой стек. Это помогает 
уменьшить количество прерываний и снижает нагрузку на CPU.
Дефолтное значение: enabled
Рекомендуемое значение: enabled
            """)
        self.rsc_combo = QComboBox()
        self.rsc_combo.addItems(["disabled", "enabled"])
        layout.addRow(rsc_label, self.rsc_combo)

        # TTL
        ttl_label = QLabel("Time to Live (TTL):")
        ttl_label.setToolTip(
            """
Описание: TTL определяет максимальное количество хопов (прыжков), через которые пакет может пройти, прежде чем будет 
уничтожен. Это помогает предотвратить зацикливание пакетов в сети.
Дефолтное значение: 128
Рекомендуемое значение: 64
            """)
        self.ttl_spin = QSpinBox()
        self.ttl_spin.setRange(32, 255)
        self.ttl_spin.setValue(64)
        layout.addRow(ttl_label, self.ttl_spin)

        # ECN
        ecn_label = QLabel("ECN Capability:")
        ecn_label.setToolTip(
            """
Описание: Explicit Congestion Notification (ECN) – это технология, которая позволяет сетевым устройствам уведомлять друг
друга о перегрузках без необходимости сбрасывать пакеты. Это может улучшить производительность в перегруженных сетях.
Дефолтное значение: disabled
Рекомендуемое значение: disabled    
            """)
        self.ecn_combo = QComboBox()
        self.ecn_combo.addItems(["default", "disabled", "enabled"])
        layout.addRow(ecn_label, self.ecn_combo)

        # Checksum Offloading
        checksum_label = QLabel("Checksum Offloading:")
        checksum_label.setToolTip(
            """
Описание: Эта функция позволяет сетевому адаптеру выполнять контрольную сумму пакетов, что разгружает процессор 
и улучшает производительность сети.
Дефолтное значение: enabled
Рекомендуемое значение: disabled
        """)
        self.checksum_combo = QComboBox()
        self.checksum_combo.addItems(["disabled", "enabled"])
        layout.addRow(checksum_label, self.checksum_combo)

        # TCP Chimney Offload
        chimney_label = QLabel("TCP Chimney Offload:")
        chimney_label.setToolTip(
            """
Описание: Эта настройка позволяет передавать обработку TCP/IP соединений на сетевой адаптер, что может уменьшить 
нагрузку на процессор.
Дефолтное значение: disabled
Рекомендуемое значение: disabled
            """)
        self.chimney_combo = QComboBox()
        self.chimney_combo.addItems(["disabled", "enabled"])
        layout.addRow(chimney_label, self.chimney_combo)

        # LSO
        lso_label = QLabel("Large Send Offload (LSO):")
        lso_label.setToolTip(
            """
Описание: LSO позволяет отправлять большие сегменты данных на сетевой адаптер, который затем разбивает их на мелкие 
пакеты. Это снижает нагрузку на процессор и повышает производительность сети.
Дефолтное значение: enabled
Рекомендуемое значение: disabled
            """)
        self.lso_combo = QComboBox()
        self.lso_combo.addItems(["disabled", "enabled"])
        layout.addRow(lso_label, self.lso_combo)

        # TCP 1323 Timestamps
        tcp1323_label = QLabel("TCP 1323 Timestamps:")
        tcp1323_label.setToolTip(
            """
Описание: Включение меток времени TCP позволяет улучшить управление передачей данных и уменьшить задержки в сетях с 
высокой пропускной способностью.
Дефолтное значение: enabled
Рекомендуемое значение: disabled
            """)
        self.tcp1323_combo = QComboBox()
        self.tcp1323_combo.addItems(["disabled", "enabled"])
        layout.addRow(tcp1323_label, self.tcp1323_combo)

    def setup_ie_tab(self):
        layout = QFormLayout(self.ie_tab)

        # MaxConnectionsPer1_0Server
        max_conn_1_0_label = QLabel("MaxConnectionsPer1_0Server:")
        max_conn_1_0_label.setToolTip(
            """
Описание: Эта настройка определяет максимальное количество одновременных соединений с сервером HTTP/1.0, что 
может повлиять на скорость загрузки страниц.
Дефолтное значение: 4
Рекомендуемое значение: 10
            """)
        self.max_conn_1_0_spin = QSpinBox()
        self.max_conn_1_0_spin.setRange(1, 128)
        self.max_conn_1_0_spin.setValue(10)
        layout.addRow(max_conn_1_0_label, self.max_conn_1_0_spin)

        # MaxConnectionsPerServer
        max_conn_label = QLabel("MaxConnectionsPerServer:")
        max_conn_label.setToolTip(
            """
Описание: Эта настройка определяет максимальное количество одновременных соединений с сервером HTTP/1.1, что также 
может повлиять на скорость загрузки страниц.
Дефолтное значение: 2
Рекомендуемое значение: 10
            """)
        self.max_conn_spin = QSpinBox()
        self.max_conn_spin.setRange(1, 128)
        self.max_conn_spin.setValue(10)
        layout.addRow(max_conn_label, self.max_conn_spin)

    def setup_host_resolution_tab(self):
        layout = QFormLayout(self.host_resolution_tab)

        # LocalPriority
        local_priority_label = QLabel("LocalPriority:")
        local_priority_label.setToolTip(
            """
Описание: Приоритет локальных имен хостов при их разрешении. Чем ниже значение, тем выше приоритет.
Дефолтное значение: 499
Рекомендуемое значение: 4
            """)
        self.local_priority_spin = QSpinBox()
        self.local_priority_spin.setRange(0, 50)
        self.local_priority_spin.setValue(4)
        layout.addRow(local_priority_label, self.local_priority_spin)

        # Host Priority
        host_priority_label = QLabel("Host Priority:")
        host_priority_label.setToolTip(
            """
Описание: Приоритет разрешения имен хостов, не относящихся к локальной сети.
Дефолтное значение: 500
Рекомендуемое значение: 5
            """)
        self.host_priority_spin = QSpinBox()
        self.host_priority_spin.setRange(0, 50)
        self.host_priority_spin.setValue(5)
        layout.addRow(host_priority_label, self.host_priority_spin)

        # DnsPriority
        dns_priority_label = QLabel("DnsPriority:")
        dns_priority_label.setToolTip(
            """
Описание: Приоритет разрешения DNS-имен.
Дефолтное значение: 2000
Рекомендуемое значение: 6
            """)
        self.dns_priority_spin = QSpinBox()
        self.dns_priority_spin.setRange(0, 50)
        self.dns_priority_spin.setValue(6)
        layout.addRow(dns_priority_label, self.dns_priority_spin)

        # Netbt Priority
        netbt_priority_label = QLabel("Netbt Priority:")
        netbt_priority_label.setToolTip(
            """
Описание: Приоритет разрешения имен NetBIOS.
Дефолтное значение: 2001
Рекомендуемое значение: 7
            """)
        self.netbt_priority_spin = QSpinBox()
        self.netbt_priority_spin.setRange(0, 50)
        self.netbt_priority_spin.setValue(7)
        layout.addRow(netbt_priority_label, self.netbt_priority_spin)

    def setup_qos_tab(self):
        layout = QFormLayout(self.qos_tab)

        # QoS Limit
        qos_limit_label = QLabel("QoS: NonBest Effort Limit:")
        qos_limit_label.setToolTip(
            """
Описание: Ограничение небезопасного трафика для обеспечения приоритета критически важных данных.
Дефолтное значение: 0
Рекомендуемое значение: 0
            """)
        self.qos_limit_spin = QSpinBox()
        self.qos_limit_spin.setRange(0, 100)
        self.qos_limit_spin.setValue(20)
        layout.addRow(qos_limit_label, self.qos_limit_spin)

        # QoS NLA
        qos_nla_label = QLabel("QoS: Do not use NLA:")
        qos_nla_label.setToolTip(
            """
Описание: Использование оптимальных настроек QoS без Network Location Awareness (NLA).
Дефолтное значение: 0
Рекомендуемое значение: 1
            """)
        self.qos_nla_combo = QComboBox()
        self.qos_nla_combo.addItems(["0", "1"])
        layout.addRow(qos_nla_label, self.qos_nla_combo)

        # Bandwidth Reservation
        bandwidth_reservation_label = QLabel("Ограничить резервируемую пропускную способность (Система):")
        bandwidth_reservation_label.setToolTip(
            """
Описание: Определяет процент пропускной способности подключения, резервируемый системой для приоритетных задач. 
По умолчанию, Windows резервирует до 80% пропускной способности, но это значение можно изменить с помощью данной 
настройки. Это помогает обеспечить критически важным приложениям и службам достаточную пропускную способность.
Дефолтное значение: не задано
Рекомендуемое значение: включено & 0%
            """)
        self.bandwidth_reservation_combo = QComboBox()
        self.bandwidth_reservation_combo.addItems(["не задано", "включено", "отключено"])
        self.bandwidth_reservation_combo.currentTextChanged.connect(self.on_bandwidth_reservation_changed)
        layout.addRow(bandwidth_reservation_label, self.bandwidth_reservation_combo)

        # Bandwidth Limit
        self.bandwidth_limit_label = QLabel("Ограничение пропускной способности (Система):")
        self.bandwidth_limit_label.setToolTip(
            """
Описание: Лимит совокупной пропускной способности, резервируемой всеми программами, запущенными на компьютере. 
Это значение позволяет управлять и контролировать максимальное использование полосы пропускания для 
различных приложений и служб.
Дефолтное значение: 80
Рекомендуемое значение: 0
            """)
        self.bandwidth_limit_spin = QSpinBox()
        self.bandwidth_limit_spin.setRange(0, 100)
        self.bandwidth_limit_spin.setValue(0)
        self.bandwidth_limit_spin.setSuffix("%")
        layout.addRow(self.bandwidth_limit_label, self.bandwidth_limit_spin)

        # Initially hide the bandwidth limit controls
        self.bandwidth_limit_label.hide()
        self.bandwidth_limit_spin.hide()

    def on_bandwidth_reservation_changed(self, value):
        """Handle bandwidth reservation combo box changes"""
        show_limit = value == "включено"
        self.bandwidth_limit_label.setVisible(show_limit)
        self.bandwidth_limit_spin.setVisible(show_limit)

    def setup_gaming_tab(self):
        layout = QFormLayout(self.gaming_tab)

        # Network Throttling
        throttling_label = QLabel("Network Throttling Index:")
        throttling_label.setToolTip(
            """
Описание: Эта настройка контролирует регулировку сети для обеспечения стабильной производительности. Более высокие значения могут уменьшить задержки в сетевых играх.
Дефолтное значение: 10
Рекомендуемое значение: ffffffff (для отключения)
            """)
        self.throttling_combo = QComboBox()
        self.throttling_combo.addItems(["ffffffff", "10", "30", "70"])
        layout.addRow(throttling_label, self.throttling_combo)

        # System Responsiveness
        responsiveness_label = QLabel("System Responsiveness:")
        responsiveness_label.setToolTip(
            """
Описание: Определяет время отклика системы на пользовательские действия и сетевые запросы.
Дефолтное значение: 20
Рекомендуемое значение: 0 (для повышения производительности игр)
            """)
        self.responsiveness_combo = QComboBox()
        self.responsiveness_combo.addItems(["0", "10", "20", "30", "100"])
        layout.addRow(responsiveness_label, self.responsiveness_combo)

        # TcpAck Frequency
        tcp_ack_label = QLabel("TcpAck Frequency:")
        tcp_ack_label.setToolTip(
            """
Описание: Устанавливает частоту отправки подтверждений TCP. Более высокое значение может улучшить 
производительность сетевых приложений и игр.
Дефолтное значение: 2
Рекомендуемое значение: 1
            """)
        self.tcp_ack_spin = QSpinBox()
        self.tcp_ack_spin.setRange(0, 255)
        self.tcp_ack_spin.setValue(1)
        layout.addRow(tcp_ack_label, self.tcp_ack_spin)

        # TCPNo Delay
        tcp_nodelay_label = QLabel("TCPNo Delay:")
        tcp_nodelay_label.setToolTip(
            """
Описание: Отключение задержки TCP для повышения производительности сетевых соединений.
Дефолтное значение: 0
Рекомендуемое значение: 1
            """)
        self.tcp_nodelay_combo = QComboBox()
        self.tcp_nodelay_combo.addItems(["0", "1"])
        layout.addRow(tcp_nodelay_label, self.tcp_nodelay_combo)

        # TcpDelAck Ticks
        tcp_delack_label = QLabel("TcpDelAck Ticks:")
        tcp_delack_label.setToolTip(
            """
Описание: Интервал задержки подтверждений TCP. Меньшие значения могут улучшить отклик сети.
Дефолтное значение: 2
Рекомендуемое значение: 0
            """)
        self.tcp_delack_spin = QSpinBox()
        self.tcp_delack_spin.setRange(0, 6)
        self.tcp_delack_spin.setValue(0)
        layout.addRow(tcp_delack_label, self.tcp_delack_spin)

    def setup_retransmissions_tab(self):
        layout = QFormLayout(self.retransmissions_tab)

        # Max SYN Retransmissions
        max_syn_label = QLabel("Max SYN Retransmissions:")
        max_syn_label.setToolTip(
            """
Описание: Максимальное количество попыток повторной передачи SYN-пакетов для установления соединения.
Дефолтное значение: 2
Рекомендуемое значение: 2
            """)
        self.max_syn_combo = QComboBox()
        self.max_syn_combo.addItems(["2", "3", "4", "5", "6", "7", "8"])
        layout.addRow(max_syn_label, self.max_syn_combo)

        # Non Sack Rtt Resiliency
        non_sack_label = QLabel("Non Sack Rtt Resiliency:")
        non_sack_label.setToolTip(
            """
Описание: Эта настройка позволяет улучшить устойчивость сети к потерям пакетов в случае, если сеть не поддерживает 
Selective Acknowledgments (SACK). Это помогает уменьшить негативное влияние задержек на производительность сети.
Дефолтное значение: disabled
Рекомендуемое значение: disabled
            """)
        self.non_sack_combo = QComboBox()
        self.non_sack_combo.addItems(["disabled", "enabled"])
        layout.addRow(non_sack_label, self.non_sack_combo)

        # Min RTO
        min_rto_label = QLabel("Min RTO:")
        min_rto_label.setToolTip(
            """
Описание: Минимальное время ожидания перед повторной передачей пакета данных в случае его потери. Это значение 
помогает минимизировать задержки и обеспечивает более быструю повторную передачу.
Дефолтное значение: 300 мс
Рекомендуемое значение: 300 мс
            """)
        self.min_rto_spin = QSpinBox()
        self.min_rto_spin.setRange(100, 3000)
        self.min_rto_spin.setValue(300)
        self.min_rto_spin.setSingleStep(10)
        layout.addRow(min_rto_label, self.min_rto_spin)

        # Initial RTO
        initial_rto_label = QLabel("Initial RTO:")
        initial_rto_label.setToolTip(
            """
Описание: Начальное время ожидания перед первой попыткой повторной передачи пакета данных. Это значение задает 
начальный тайм-аут, который затем может увеличиваться при последующих попытках.
Дефолтное значение: 3000 мс
Рекомендуемое значение: 1000 или 2000 мс
            """)
        self.initial_rto_spin = QSpinBox()
        self.initial_rto_spin.setRange(100, 3000)
        self.initial_rto_spin.setValue(3000)
        self.initial_rto_spin.setSingleStep(100)
        layout.addRow(initial_rto_label, self.initial_rto_spin)

    def setup_memory_tab(self):
        layout = QFormLayout(self.memory_tab)

        # Large SystemCache
        large_cache_label = QLabel("Large SystemCache:")
        large_cache_label.setToolTip(
            """
Описание: Эта настройка определяет использование большого системного кеша для улучшения производительности 
файловой системы и сети. Включение этой опции может увеличить общую производительность системы за счет 
выделения большего количества памяти для кеширования.
Дефолтное значение: 0 (отключено)
Рекомендуемое значение: 0 (отключено)
            """)
        self.large_cache_combo = QComboBox()
        self.large_cache_combo.addItems(["0", "1"])
        layout.addRow(large_cache_label, self.large_cache_combo)

        # Size
        size_label = QLabel("Size:")
        size_label.setToolTip(
            """
Описание: Размер выделенной памяти для сети. Это определяет объем памяти, который система выделяет для сетевого 
трафика. Большие значения могут улучшить производительность сети в высоконагруженных средах.
Дефолтное значение: 1 (small)
Рекомендуемое значение: 3 (large)
            """)
        self.size_combo = QComboBox()
        self.size_combo.addItems(["small", "medium", "large"])
        layout.addRow(size_label, self.size_combo)

    def setup_ports_tab(self):
        layout = QFormLayout(self.ports_tab)

        # MaxUserPort
        max_user_port_label = QLabel("MaxUserPort:")
        max_user_port_label.setToolTip(
            """
Описание: Эта настройка определяет максимальное количество динамических портов, которые могут быть 
выделены пользователю. Увеличение этого значения может улучшить производительность сетевых приложений, 
требующих большого количества соединений.
Дефолтное значение: 5000
Рекомендуемое значение: 65534
            """)
        self.max_user_port_spin = QSpinBox()
        self.max_user_port_spin.setRange(1024, 65535)
        self.max_user_port_spin.setValue(65535)
        layout.addRow(max_user_port_label, self.max_user_port_spin)

        # Tcp TimedWait Delay
        tcp_timedwait_label = QLabel("Tcp TimedWait Delay:")
        tcp_timedwait_label.setToolTip(
            """
Описание: Эта настройка определяет время, в течение которого TCP-соединение остается в состоянии ожидания перед его 
окончательным завершением. Уменьшение этого значения может ускорить повторное использование портов для новых соединений.
Дефолтное значение: 240 секунд
Рекомендуемое значение: 60-30 секунд
            """)
        self.tcp_timedwait_spin = QSpinBox()
        self.tcp_timedwait_spin.setRange(30, 300)
        self.tcp_timedwait_spin.setValue(120)
        layout.addRow(tcp_timedwait_label, self.tcp_timedwait_spin)

    def get_adapter_registry_key(self, adapter_guid):
        """Get the correct registry key path for a network adapter"""
        base_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as base_key:
                # Iterate through subkeys (0000, 0001, etc.)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(base_key, i)
                        with winreg.OpenKey(base_key, subkey_name) as subkey:
                            try:
                                # Check if this is our adapter by comparing NetCfgInstanceId with GUID
                                value, _ = winreg.QueryValueEx(subkey, "NetCfgInstanceId")
                                if value.lower() == adapter_guid.lower():
                                    return f"{base_path}\\{subkey_name}"
                            except:
                                pass
                        i += 1
                    except WindowsError:
                        break
        except:
            pass

        return None

    def load_network_adapters(self):
        self.adapter_combo.clear()
        self.network_adapters = {}

        try:
            # Get all network adapters without filtering
            network_adapters = self.wmi_service.Win32_NetworkAdapter(
                PhysicalAdapter=True  # Only physical adapters
            )

            for adapter in network_adapters:
                try:
                    # Get adapter configuration
                    adapter_configs = self.wmi_service.Win32_NetworkAdapterConfiguration(
                        Index=adapter.Index
                    )

                    if adapter_configs:
                        config = adapter_configs[0]

                        # Get GUID from adapter
                        adapter_guid = None
                        try:
                            adapter_guid = adapter.GUID
                        except:
                            try:
                                adapter_guid = config.SettingID
                            except:
                                continue

                        if adapter_guid:
                            # Create more informative adapter name
                            status = "Enabled" if adapter.NetEnabled else "Disabled"
                            ip_info = ""
                            if hasattr(config, 'IPAddress') and config.IPAddress:
                                ip_info = f" - {config.IPAddress[0]}"

                            adapter_name = f"{adapter.NetConnectionID or adapter.Name} ({status}{ip_info})"
                            self.adapter_combo.addItem(adapter_name)

                            # Store adapter info
                            self.network_adapters[adapter_name] = {
                                'adapter': adapter,
                                'guid': adapter_guid
                            }
                except Exception as adapter_error:
                    print(f"Error processing adapter: {str(adapter_error)}")
                    continue

            if self.adapter_combo.count() > 0:
                self.adapter_combo.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось загрузить список сетевых адаптеров: {str(e)}\n"
                                "Попробуйте запустить программу от имени администратора.")

    def on_adapter_selected(self, index):
        if index >= 0:
            adapter_name = self.adapter_combo.currentText()
            adapter_info = self.network_adapters.get(adapter_name)

            if adapter_info:
                self.current_adapter = adapter_info['adapter']
                self.current_adapter_guid = adapter_info['guid']
                self.settings_tab.setEnabled(True)
                self.apply_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.load_current_settings()
            else:
                self.current_adapter = None
                self.current_adapter_guid = None
                self.settings_tab.setEnabled(False)
                self.apply_btn.setEnabled(False)
                self.reset_btn.setEnabled(False)

    def load_current_settings(self):
        """Load current network settings from the registry for the selected adapter"""
        if not self.current_adapter:
            return

        try:
            # Get adapter registry key path if GUID is available
            adapter_registry_key = None
            if hasattr(self, 'current_adapter_guid') and self.current_adapter_guid:
                adapter_registry_key = self.get_adapter_registry_key(self.current_adapter_guid)

            # Load TCP/IP settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                                winreg.KEY_READ) as key:

                try:
                    value, _ = winreg.QueryValueEx(key, "GlobalMaxTcpWindowSize")
                    # Map value to corresponding auto-tuning setting (this is simplified)
                    if value < 8192:
                        self.tcp_tuning_combo.setCurrentText("disabled")
                    elif value < 65535:
                        self.tcp_tuning_combo.setCurrentText("highly restricted")
                    else:
                        self.tcp_tuning_combo.setCurrentText("normal")
                except:
                    self.tcp_tuning_combo.setCurrentText("normal")

                try:
                    value, _ = winreg.QueryValueEx(key, "Tcp1323Opts")
                    self.win_scaling_combo.setCurrentText("enabled" if (value & 1) else "disabled")
                    self.tcp1323_combo.setCurrentText("enabled" if (value & 2) else "disabled")
                except:
                    self.win_scaling_combo.setCurrentText("enabled")
                    self.tcp1323_combo.setCurrentText("enabled")

                try:
                    value, _ = winreg.QueryValueEx(key, "DefaultTTL")
                    self.ttl_spin.setValue(value)
                except:
                    self.ttl_spin.setValue(64)

                try:
                    value, _ = winreg.QueryValueEx(key, "ECN")
                    if value == 0:
                        self.ecn_combo.setCurrentText("disabled")
                    elif value == 1:
                        self.ecn_combo.setCurrentText("enabled")
                    else:
                        self.ecn_combo.setCurrentText("default")
                except:
                    self.ecn_combo.setCurrentText("default")

            # Load congestion provider
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Nsi\{eb004a03-9b1a-11d4-9123-0050047759bc}\26", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "CongestionProvider")
                    if value == 0:
                        self.congestion_combo.setCurrentText("default")
                    elif value == 1:
                        self.congestion_combo.setCurrentText("ctcp")
                    elif value == 2:
                        self.congestion_combo.setCurrentText("dctcp")
                    elif value == 3:
                        self.congestion_combo.setCurrentText("cubic")
                    elif value == 4:
                        self.congestion_combo.setCurrentText("newreno")
                except:
                    self.congestion_combo.setCurrentText("default")

            # Load RSS and RSC settings from adapter properties
            if adapter_registry_key:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_registry_key, 0, winreg.KEY_READ) as key:
                        try:
                            value, _ = winreg.QueryValueEx(key, "*RSS")
                            self.rss_combo.setCurrentText("enabled" if value == 1 else "disabled")
                        except:
                            self.rss_combo.setCurrentText("enabled")

                        try:
                            value, _ = winreg.QueryValueEx(key, "*RSC")
                            self.rsc_combo.setCurrentText("enabled" if value == 1 else "disabled")
                        except:
                            self.rsc_combo.setCurrentText("enabled")

                        try:
                            value, _ = winreg.QueryValueEx(key, "*ChecksumOffload")
                            self.checksum_combo.setCurrentText("enabled" if value == 1 else "disabled")
                        except:
                            self.checksum_combo.setCurrentText("enabled")

                        try:
                            value, _ = winreg.QueryValueEx(key, "*TCPChimneyOffload")
                            self.chimney_combo.setCurrentText("enabled" if value == 1 else "disabled")
                        except:
                            self.chimney_combo.setCurrentText("disabled")

                        try:
                            value, _ = winreg.QueryValueEx(key, "*LSOv2IPv4")
                            self.lso_combo.setCurrentText("enabled" if value == 1 else "disabled")
                        except:
                            self.lso_combo.setCurrentText("enabled")
                except:
                    # Set default values if we couldn't access adapter registry
                    self.rss_combo.setCurrentText("enabled")
                    self.rsc_combo.setCurrentText("enabled")
                    self.checksum_combo.setCurrentText("enabled")
                    self.chimney_combo.setCurrentText("disabled")
                    self.lso_combo.setCurrentText("enabled")

            # Load IE settings
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "MaxConnectionsPer1_0Server")
                    self.max_conn_1_0_spin.setValue(value)
                except:
                    self.max_conn_1_0_spin.setValue(10)

                try:
                    value, _ = winreg.QueryValueEx(key, "MaxConnectionsPerServer")
                    self.max_conn_spin.setValue(value)
                except:
                    self.max_conn_spin.setValue(10)

            # Load Host Resolution Priority settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider",
                                0, winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "LocalPriority")
                    self.local_priority_spin.setValue(value)
                except:
                    self.local_priority_spin.setValue(4)

                try:
                    value, _ = winreg.QueryValueEx(key, "HostsPriority")
                    self.host_priority_spin.setValue(value)
                except:
                    self.host_priority_spin.setValue(5)

                try:
                    value, _ = winreg.QueryValueEx(key, "DnsPriority")
                    self.dns_priority_spin.setValue(value)
                except:
                    self.dns_priority_spin.setValue(6)

                try:
                    value, _ = winreg.QueryValueEx(key, "NetbtPriority")
                    self.netbt_priority_spin.setValue(value)
                except:
                    self.netbt_priority_spin.setValue(7)

            # Load QoS settings
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Psched", 0,
                                    winreg.KEY_READ) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "NonBestEffortLimit")
                        self.qos_limit_spin.setValue(value)
                    except:
                        self.qos_limit_spin.setValue(20)

                    try:
                        value, _ = winreg.QueryValueEx(key, "DontUseNLA")
                        self.qos_nla_combo.setCurrentText(str(value))
                    except:
                        self.qos_nla_combo.setCurrentText("0")

                    try:
                        value, _ = winreg.QueryValueEx(key, "BandwidthReservation")
                        if value == 1:
                            self.bandwidth_reservation_combo.setCurrentText("включено")
                        elif value == 0:
                            self.bandwidth_reservation_combo.setCurrentText("отключено")
                        else:
                            self.bandwidth_reservation_combo.setCurrentText("не задано")

                        limit_value, _ = winreg.QueryValueEx(key, "BandwidthLimit")
                        self.bandwidth_limit_spin.setValue(limit_value)
                    except:
                        self.bandwidth_reservation_combo.setCurrentText("не задано")
                        self.bandwidth_limit_spin.setValue(0)
            except:
                # Set defaults if key doesn't exist
                self.qos_limit_spin.setValue(20)
                self.qos_nla_combo.setCurrentText("0")
                self.bandwidth_reservation_combo.setCurrentText("не задано")
                self.bandwidth_limit_spin.setValue(0)

            # Load Gaming settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "NetworkThrottlingIndex")
                    self.throttling_combo.setCurrentText(str(value) if value in [10, 30, 70] else "ffffffff")
                except:
                    self.throttling_combo.setCurrentText("ffffffff")

                try:
                    value, _ = winreg.QueryValueEx(key, "SystemResponsiveness")
                    self.responsiveness_combo.setCurrentText(str(value))
                except:
                    self.responsiveness_combo.setCurrentText("20")

            # Load Nagle settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "TcpAckFrequency")
                    self.tcp_ack_spin.setValue(value)
                except:
                    self.tcp_ack_spin.setValue(1)

                try:
                    value, _ = winreg.QueryValueEx(key, "TCPNoDelay")
                    self.tcp_nodelay_combo.setCurrentText(str(value))
                except:
                    self.tcp_nodelay_combo.setCurrentText("0")

                try:
                    value, _ = winreg.QueryValueEx(key, "TcpDelAckTicks")
                    self.tcp_delack_spin.setValue(value)
                except:
                    self.tcp_delack_spin.setValue(0)

            # Load Retransmission settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "TcpMaxDataRetransmissions")
                    self.max_syn_combo.setCurrentText(
                        str(value) if str(value) in ["2", "3", "4", "5", "6", "7", "8"] else "2")
                except:
                    self.max_syn_combo.setCurrentText("2")

                try:
                    value, _ = winreg.QueryValueEx(key, "NonSackRttResiliency")
                    self.non_sack_combo.setCurrentText("enabled" if value == 1 else "disabled")
                except:
                    self.non_sack_combo.setCurrentText("disabled")

                try:
                    value, _ = winreg.QueryValueEx(key, "TcpMinRtoMs")
                    self.min_rto_spin.setValue(value)
                except:
                    self.min_rto_spin.setValue(300)

                try:
                    value, _ = winreg.QueryValueEx(key, "TcpInitialRtoMs")
                    self.initial_rto_spin.setValue(value)
                except:
                    self.initial_rto_spin.setValue(3000)

            # Load Memory settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "LargeSystemCache")
                    self.large_cache_combo.setCurrentText(str(value))
                except:
                    self.large_cache_combo.setCurrentText("0")

                try:
                    value, _ = winreg.QueryValueEx(key, "Size")
                    if value < 1:
                        self.size_combo.setCurrentText("small")
                    elif value < 2:
                        self.size_combo.setCurrentText("medium")
                    else:
                        self.size_combo.setCurrentText("large")
                except:
                    self.size_combo.setCurrentText("medium")

            # Load Port settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                                winreg.KEY_READ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "MaxUserPort")
                    self.max_user_port_spin.setValue(value)
                except:
                    self.max_user_port_spin.setValue(65535)

                try:
                    value, _ = winreg.QueryValueEx(key, "TcpTimedWaitDelay")
                    self.tcp_timedwait_spin.setValue(value)
                except:
                    self.tcp_timedwait_spin.setValue(120)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить текущие настройки: {str(e)}")
            self.reset_settings()  # Load defaults if we can't get current settings

    def apply_settings(self):
        """Apply the current settings to the registry"""
        try:
            if not self.current_adapter:
                raise Exception("Не выбран сетевой адаптер")

            # Get adapter GUID
            adapter_guid = self.current_adapter.GUID if hasattr(self.current_adapter, 'GUID') else None

            # Save settings to registry
            self.save_settings_to_registry(adapter_guid)

            QMessageBox.information(self, "Успех",
                                    "Настройки успешно применены. Некоторые изменения могут потребовать перезагрузки.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {str(e)}")

    def reset_settings(self):
        try:
            # Reset all controls to default values
            self.tcp_tuning_combo.setCurrentText("normal")
            self.win_scaling_combo.setCurrentText("enabled")
            self.congestion_combo.setCurrentText("cubic")
            self.rss_combo.setCurrentText("enabled")
            self.rsc_combo.setCurrentText("enabled")
            self.ttl_spin.setValue(64)
            self.ecn_combo.setCurrentText("default")
            self.checksum_combo.setCurrentText("enabled")
            self.chimney_combo.setCurrentText("disabled")
            self.lso_combo.setCurrentText("enabled")
            self.tcp1323_combo.setCurrentText("enabled")

            self.max_conn_1_0_spin.setValue(4)
            self.max_conn_spin.setValue(2)

            self.local_priority_spin.setValue(499)
            self.host_priority_spin.setValue(500)
            self.dns_priority_spin.setValue(2000)
            self.netbt_priority_spin.setValue(2001)

            self.qos_limit_spin.setValue(20)
            self.qos_nla_combo.setCurrentText("0")
            self.bandwidth_reservation_combo.setCurrentText("не задано")
            self.bandwidth_limit_spin.setValue(0)

            self.throttling_combo.setCurrentText("10")
            self.responsiveness_combo.setCurrentText("20")
            self.tcp_ack_spin.setValue(2)
            self.tcp_nodelay_combo.setCurrentText("0")
            self.tcp_delack_spin.setValue(0)

            self.max_syn_combo.setCurrentText("2")
            self.non_sack_combo.setCurrentText("disabled")
            self.min_rto_spin.setValue(300)
            self.initial_rto_spin.setValue(3000)

            self.large_cache_combo.setCurrentText("0")
            self.size_combo.setCurrentText("medium")

            self.max_user_port_spin.setValue(65535)
            self.tcp_timedwait_spin.setValue(120)

            QMessageBox.information(self, "Сброс", "Настройки сброшены к стандартным значениям")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сбросить настройки: {str(e)}")

    def save_settings_to_registry(self, adapter_guid=None):
        """Save the current settings to the Windows registry"""
        try:
            # Get adapter registry key path if GUID is available
            adapter_registry_key = None
            if adapter_guid:
                adapter_registry_key = self.get_adapter_registry_key(adapter_guid)

            # TCP/IP Parameters
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 0,
                                winreg.KEY_WRITE) as key:

                # TCP Window Auto-Tuning (this is simplified)
                if self.tcp_tuning_combo.currentText() == "disabled":
                    winreg.SetValueEx(key, "GlobalMaxTcpWindowSize", 0, winreg.REG_DWORD, 8192)
                elif self.tcp_tuning_combo.currentText() == "highly restricted":
                    winreg.SetValueEx(key, "GlobalMaxTcpWindowSize", 0, winreg.REG_DWORD, 32768)
                elif self.tcp_tuning_combo.currentText() == "restricted":
                    winreg.SetValueEx(key, "GlobalMaxTcpWindowSize", 0, winreg.REG_DWORD, 65535)
                elif self.tcp_tuning_combo.currentText() == "normal":
                    winreg.SetValueEx(key, "GlobalMaxTcpWindowSize", 0, winreg.REG_DWORD, 131072)
                elif self.tcp_tuning_combo.currentText() == "experimental":
                    winreg.SetValueEx(key, "GlobalMaxTcpWindowSize", 0, winreg.REG_DWORD, 262144)

                # Windows Scaling and TCP 1323 Timestamps
                value = 0
                if self.win_scaling_combo.currentText() == "enabled":
                    value |= 1
                if self.tcp1323_combo.currentText() == "enabled":
                    value |= 2
                winreg.SetValueEx(key, "Tcp1323Opts", 0, winreg.REG_DWORD, value)

                # TTL
                winreg.SetValueEx(key, "DefaultTTL", 0, winreg.REG_DWORD, self.ttl_spin.value())

                # ECN
                if self.ecn_combo.currentText() == "disabled":
                    winreg.SetValueEx(key, "ECN", 0, winreg.REG_DWORD, 0)
                elif self.ecn_combo.currentText() == "enabled":
                    winreg.SetValueEx(key, "ECN", 0, winreg.REG_DWORD, 1)
                # For "default", we don't set the value

                # Nagle's algorithm settings
                winreg.SetValueEx(key, "TcpAckFrequency", 0, winreg.REG_DWORD, self.tcp_ack_spin.value())
                winreg.SetValueEx(key, "TCPNoDelay", 0, winreg.REG_DWORD, int(self.tcp_nodelay_combo.currentText()))
                winreg.SetValueEx(key, "TcpDelAckTicks", 0, winreg.REG_DWORD, self.tcp_delack_spin.value())

                # Retransmission settings
                winreg.SetValueEx(key, "TcpMaxDataRetransmissions", 0, winreg.REG_DWORD,
                                  int(self.max_syn_combo.currentText()))
                winreg.SetValueEx(key, "NonSackRttResiliency", 0, winreg.REG_DWORD,
                                  1 if self.non_sack_combo.currentText() == "enabled" else 0)
                winreg.SetValueEx(key, "TcpMinRtoMs", 0, winreg.REG_DWORD, self.min_rto_spin.value())
                winreg.SetValueEx(key, "TcpInitialRtoMs", 0, winreg.REG_DWORD, self.initial_rto_spin.value())

                # Port settings
                winreg.SetValueEx(key, "MaxUserPort", 0, winreg.REG_DWORD, self.max_user_port_spin.value())
                winreg.SetValueEx(key, "TcpTimedWaitDelay", 0, winreg.REG_DWORD, self.tcp_timedwait_spin.value())

            # Congestion provider
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Nsi\{eb004a03-9b1a-11d4-9123-0050047759bc}\26", 0,
                                winreg.KEY_WRITE) as key:
                value = 0  # default
                if self.congestion_combo.currentText() == "ctcp":
                    value = 1
                elif self.congestion_combo.currentText() == "dctcp":
                    value = 2
                elif self.congestion_combo.currentText() == "cubic":
                    value = 3
                elif self.congestion_combo.currentText() == "newreno":
                    value = 4
                winreg.SetValueEx(key, "CongestionProvider", 0, winreg.REG_DWORD, value)

            # Adapter-specific settings
            if adapter_registry_key:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_registry_key, 0, winreg.KEY_WRITE) as key:
                        # RSS
                        winreg.SetValueEx(key, "*RSS", 0, winreg.REG_DWORD,
                                          1 if self.rss_combo.currentText() == "enabled" else 0)

                        # RSC
                        winreg.SetValueEx(key, "*RSC", 0, winreg.REG_DWORD,
                                          1 if self.rsc_combo.currentText() == "enabled" else 0)

                        # Checksum Offloading
                        winreg.SetValueEx(key, "*ChecksumOffload", 0, winreg.REG_DWORD,
                                          1 if self.checksum_combo.currentText() == "enabled" else 0)

                        # TCP Chimney Offload
                        winreg.SetValueEx(key, "*TCPChimneyOffload", 0, winreg.REG_DWORD,
                                          1 if self.chimney_combo.currentText() == "enabled" else 0)

                        # Large Send Offload
                        winreg.SetValueEx(key, "*LSOv2IPv4", 0, winreg.REG_DWORD,
                                          1 if self.lso_combo.currentText() == "enabled" else 0)
                except:
                    QMessageBox.warning(self, "Предупреждение", "Не удалось сохранить некоторые настройки адаптера")

            # IE settings
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0,
                                winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "MaxConnectionsPer1_0Server", 0, winreg.REG_DWORD,
                                  self.max_conn_1_0_spin.value())
                winreg.SetValueEx(key, "MaxConnectionsPerServer", 0, winreg.REG_DWORD, self.max_conn_spin.value())

            # Host Resolution Priority
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider",
                                0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "LocalPriority", 0, winreg.REG_DWORD, self.local_priority_spin.value())
                winreg.SetValueEx(key, "HostsPriority", 0, winreg.REG_DWORD, self.host_priority_spin.value())
                winreg.SetValueEx(key, "DnsPriority", 0, winreg.REG_DWORD, self.dns_priority_spin.value())
                winreg.SetValueEx(key, "NetbtPriority", 0, winreg.REG_DWORD, self.netbt_priority_spin.value())

            # QoS settings
            try:
                with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\Psched") as key:
                    winreg.SetValueEx(key, "NonBestEffortLimit", 0, winreg.REG_DWORD, self.qos_limit_spin.value())
                    winreg.SetValueEx(key, "DontUseNLA", 0, winreg.REG_DWORD, int(self.qos_nla_combo.currentText()))

                    # Save bandwidth reservation settings
                    reservation_value = -1  # не задано
                    if self.bandwidth_reservation_combo.currentText() == "включено":
                        reservation_value = 1
                    elif self.bandwidth_reservation_combo.currentText() == "отключено":
                        reservation_value = 0

                    winreg.SetValueEx(key, "BandwidthReservation", 0, winreg.REG_DWORD, reservation_value)

                    if self.bandwidth_reservation_combo.currentText() == "включено":
                        winreg.SetValueEx(key, "BandwidthLimit", 0, winreg.REG_DWORD, self.bandwidth_limit_spin.value())
            except:
                QMessageBox.warning(self, "Предупреждение", "Не удалось сохранить настройки QoS")

            # Gaming settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0,
                                winreg.KEY_WRITE) as key:
                if self.throttling_combo.currentText() == "ffffffff":
                    winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff)
                else:
                    winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD,
                                      int(self.throttling_combo.currentText()))

                winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD,
                                  int(self.responsiveness_combo.currentText()))

            # Memory settings
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", 0,
                                winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD,
                                  int(self.large_cache_combo.currentText()))

                size_value = 0
                if self.size_combo.currentText() == "small":
                    size_value = 0
                elif self.size_combo.currentText() == "medium":
                    size_value = 1
                elif self.size_combo.currentText() == "large":
                    size_value = 2
                winreg.SetValueEx(key, "Size", 0, winreg.REG_DWORD, size_value)

        except Exception as e:
            raise Exception(f"Ошибка при сохранении в реестр: {str(e)}")