from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QScrollArea, QListWidget, QLineEdit
from PyQt6.QtCore import Qt
import config

class Dashboard(QWidget):
    def __init__(self, stats_data, whitelist_ref, parent=None):
        super().__init__(parent)
        self.stats = stats_data
        self.whitelist_ref = whitelist_ref
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Focus Pet 3.0 - Dashboard & Ayarlar")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #121212; color: white; font-family: 'Segoe UI', Arial;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 🚀 Başlık
        header = QLabel("Focus Pet Kontrol Merkezi")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00; margin-bottom: 10px;")
        main_layout.addWidget(header)

        # 📊 İstatistik Kartları
        stats_hbox = QHBoxLayout()
        
        def create_stat_card(label, value, color, attr_name):
            card = QFrame()
            card.setStyleSheet(f"background: #1e1e1e; border-radius: 10px; border: 1px solid {color};")
            l = QVBoxLayout(card)
            t = QLabel(label)
            t.setStyleSheet("font-size: 12px; color: #888; border: none;")
            v = QLabel(str(value))
            v.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color}; border: none;")
            setattr(self, attr_name, v) # Dinamik güncelleme için sakla
            l.addWidget(t)
            l.addWidget(v)
            return card

        stats_hbox.addWidget(create_stat_card("Odaklanma", f"{int(self.stats['focused_min'])} dk", "#2ecc71", "val_focused"))
        stats_hbox.addWidget(create_stat_card("Dağılma", f"{int(self.stats['distracted_min'])} dk", "#e74c3c", "val_distracted"))
        stats_hbox.addWidget(create_stat_card("Toplam XP", int(self.stats['xp']), "#f1c40f", "val_xp"))
        main_layout.addLayout(stats_hbox)

        # ⚙️ Whitelist Yönetimi
        main_layout.addSpacing(20)
        wl_label = QLabel("🎯 Akıllı Whitelist (İzin Verilenler)")
        wl_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ccc;")
        main_layout.addWidget(wl_label)

        self.wl_list = QListWidget()
        self.wl_list.setStyleSheet("background: #1e1e1e; border-radius: 5px; padding: 5px; border: 1px solid #333;")
        for item in config.DEFAULT_WHITELIST:
            self.wl_list.addItem(f"• {item} (Sistem)")
        for item in self.whitelist_ref:
            self.wl_list.addItem(item)
        main_layout.addWidget(self.wl_list)

        # Yeni Ekleme
        add_hbox = QHBoxLayout()
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("Yeni kelime ekle (örn: udemy, proje_adı)")
        self.add_input.setStyleSheet("background: #222; border: 1px solid #444; padding: 8px; border-radius: 5px; color: white;")
        add_btn = QPushButton("EKLE")
        add_btn.setStyleSheet("background: #27ae60; font-weight: bold; padding: 8px 15px; border-radius: 5px;")
        add_btn.clicked.connect(self.add_item)
        add_hbox.addWidget(self.add_input)
        add_hbox.addWidget(add_btn)
        main_layout.addLayout(add_hbox)

        self.setLayout(main_layout)

    def update_display(self):
        # Stats verilerini UI'a yansıt
        if hasattr(self, 'val_focused'):
            self.val_focused.setText(f"{int(self.stats['focused_min'])} dk")
            self.val_distracted.setText(f"{int(self.stats['distracted_min'])} dk")
            self.val_xp.setText(str(int(self.stats['xp'])))

    def add_item(self):
        text = self.add_input.text().strip()
        if text:
            self.whitelist_ref.add(text)
            self.wl_list.addItem(text)
            self.add_input.clear()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
