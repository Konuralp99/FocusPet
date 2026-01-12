from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QScrollArea, QListWidget, QLineEdit, QTabWidget, QProgressBar
from PyQt6.QtCore import Qt
import config

class Dashboard(QWidget):
    def __init__(self, stats_data, whitelist_ref, parent=None):
        super().__init__(parent)
        self.stats = stats_data
        self.whitelist_ref = whitelist_ref
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Focus Pet 4.0 - AI Assistant Dashboard")
        self.setFixedSize(650, 600)
        self.setStyleSheet("background-color: #121212; color: white; font-family: 'Segoe UI', Arial;")
        
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; background: #121212; }
            QTabBar::tab { background: #1a1a1a; color: #888; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #333; color: #00ff00; border-bottom: 2px solid #00ff00; }
        """)
        
        # --- SEKME 1: ÖZET & GÖREVLER ---
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)

        # 📊 İstatistik Kartları
        stats_hbox = QHBoxLayout()
        def create_stat_card(label, value, color, attr_name):
            card = QFrame()
            card.setStyleSheet(f"background: #1e1e1e; border-radius: 10px; border: 1px solid {color};")
            l = QVBoxLayout(card)
            t = QLabel(label); t.setStyleSheet("font-size: 11px; color: #888; border: none;")
            v = QLabel(str(value)); v.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; border: none;")
            setattr(self, attr_name, v)
            l.addWidget(t); l.addWidget(v)
            return card

        stats_hbox.addWidget(create_stat_card("Odak", f"{int(self.stats['focused_min'])}dk", "#2ecc71", "val_focused"))
        stats_hbox.addWidget(create_stat_card("Enerji", f"%{int(self.stats.get('energy', 100))}", "#e67e22", "val_energy"))
        stats_hbox.addWidget(create_stat_card("XP", int(self.stats['xp']), "#f1c40f", "val_xp"))
        summary_layout.addLayout(stats_hbox)

        # 🎯 Günlük Görevler (v4.0 Yeni)
        summary_layout.addSpacing(15)
        summary_layout.addWidget(QLabel("🎯 GÜNLÜK GÖREVLER (XP ÖDÜLLÜ)", styleSheet="font-weight: bold; color: #888;"))
        self.quest_container = QVBoxLayout()
        summary_layout.addLayout(self.quest_container)
        
        # ⚙️ Whitelist Bölümü (Özetin altına)
        summary_layout.addStretch()
        summary_layout.addWidget(QLabel("⚙️ WHITELIST YÖNETİMİ", styleSheet="font-weight: bold; color: #888;"))
        self.wl_list = QListWidget()
        self.wl_list.setFixedHeight(120)
        self.wl_list.setStyleSheet("background: #1a1a1a; border: 1px solid #333; border-radius: 5px;")
        for item in self.whitelist_ref: self.wl_list.addItem(item)
        summary_layout.addWidget(self.wl_list)
        
        add_hbox = QHBoxLayout()
        self.add_input = QLineEdit(); self.add_input.setPlaceholderText("Yeni kelime...")
        self.add_input.setStyleSheet("background: #222; border: 1px solid #444; padding: 5px; border-radius: 4px; color: white;")
        add_btn = QPushButton("EKLE"); add_btn.clicked.connect(self.add_item)
        add_btn.setStyleSheet("background: #27ae60; font-weight: bold; padding: 5px 15px; border-radius: 4px;")
        add_hbox.addWidget(self.add_input); add_hbox.addWidget(add_btn)
        summary_layout.addLayout(add_hbox)
        
        # SİLME Butonu (v4.0.1 Yeni)
        remove_btn = QPushButton("SEÇİLENİ LİSTEDEN SİL")
        remove_btn.clicked.connect(self.remove_item)
        remove_btn.setStyleSheet("""
            background: #c0392b; color: white; font-weight: bold; 
            padding: 8px; border-radius: 4px; margin-top: 5px;
        """)
        summary_layout.addWidget(remove_btn)

        # --- SEKME 2: ANALİTİK (HİSTORY) ---
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.addWidget(QLabel("📈 UYGULAMA KULLANIM ANALİZİ", styleSheet="font-weight: bold; color: #888;"))
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background: #1a1a1a; border: none; font-size: 13px; color: #ddd;")
        analysis_layout.addWidget(self.history_list)
        
        self.tabs.addTab(summary_tab, "🏠 Özet & Görevler")
        self.tabs.addTab(analysis_tab, "📈 Analitik")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.update_display()

    def update_display(self):
        # Stats güncelleme
        if hasattr(self, 'val_focused'):
            self.val_focused.setText(f"{int(self.stats['focused_min'])}dk")
            self.val_energy.setText(f"%{int(self.stats.get('energy', 100))}")
            self.val_xp.setText(str(int(self.stats['xp'])))

        # Görevleri temizle ve yeniden oluştur (Hızlı ama kaba çözüm, geliştirilebilir)
        while self.quest_container.count():
            item = self.quest_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for q in self.stats.get("daily_quests", []):
            q_frame = QFrame()
            q_frame.setStyleSheet(f"background: #1a1a1a; border: 1px solid {'#27ae60' if q['done'] else '#333'}; border-radius: 5px; padding: 5px;")
            ql = QHBoxLayout(q_frame)
            icon = "✅" if q["done"] else "⏳"
            ql.addWidget(QLabel(f"{icon} {q['title']}"))
            prog = QProgressBar()
            prog.setMaximum(int(q["goal"]))
            prog.setValue(int(q["progress"]))
            prog.setFixedHeight(10); prog.setTextVisible(False)
            prog.setStyleSheet("QProgressBar::chunk { background: #27ae60; }")
            ql.addWidget(prog)
            self.quest_container.addWidget(q_frame)

        # History güncelleme
        self.history_list.clear()
        for item in reversed(self.stats.get("history", [])):
            color = "#2ecc71" if item["state"] == "focused" else ("#e74c3c" if item["state"] == "distracted" else "#888")
            status_text = "Odak" if item["state"] == "focused" else ("Dağıldı" if item["state"] == "distracted" else "Uzakta")
            self.history_list.addItem(f"[{item['time']}] {item['app'][:20]} - {int(item['duration']*60)}sn ({status_text})")
            self.history_list.item(self.history_list.count()-1).setForeground(Qt.GlobalColor.white if item["state"]=="focused" else Qt.GlobalColor.gray)

    def add_item(self):
        text = self.add_input.text().strip().lower()
        if text and text not in self.whitelist_ref:
            self.whitelist_ref.add(text)
            self.wl_list.addItem(text)
            self.add_input.clear()

    def remove_item(self):
        selected_items = self.wl_list.selectedItems()
        if not selected_items: return
        
        for item in selected_items:
            text = item.text()
            if text in self.whitelist_ref:
                self.whitelist_ref.remove(text)
            self.wl_list.takeItem(self.wl_list.row(item))

    def closeEvent(self, event):
        event.ignore()
        self.hide()
