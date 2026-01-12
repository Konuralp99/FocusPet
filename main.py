import sys
import os
import random
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QProgressBar, QHBoxLayout, QFrame, QSystemTrayIcon
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QPixmap, QCursor, QAction, QMovie, QIcon
from monitor import WindowMonitor
from dashboard import Dashboard
import config

class FocusPet(QWidget):
    def __init__(self):
        super().__init__()
        
        # Dosya yolları
        self.happy_path = os.path.join(config.ASSETS_DIR, "happy.gif")
        self.angry_path = os.path.join(config.ASSETS_DIR, "angry.gif")
        self.sleep_path = os.path.join(config.ASSETS_DIR, "sleep.gif")
        self.table_path = os.path.join(config.ASSETS_DIR, "table.png")
        self.plant_path = os.path.join(config.ASSETS_DIR, "plant.png")
        self.coffee_path = os.path.join(config.ASSETS_DIR, "coffee.png")
        
        self.state = "happy"
        self.is_afk = False
        self.current_window_title = ""
        self.stats_data = config.get_default_stats()
        self.dashboard_window = None
        
        self.initUI()
        self.oldPos = self.pos()
        
        # Monitor Thread
        self.monitor = WindowMonitor()
        self.monitor.focus_changed.connect(self.update_status)
        self.monitor.start()
        
        # Tray Icon setup
        self.tray_icon = None
        self.setup_tray()

    def initUI(self):
        # Tool penceresi olarak ayarla (Görev çubuğunda görünmez, her zaman üstte)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 8, 15, 8)
        self.main_layout.setSpacing(6) # İdeal nefes payı
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Üst Panel
        self.top_hbox = QHBoxLayout()
        self.top_hbox.setContentsMargins(0, 5, 0, 0)
        self.pomo_badge = QLabel("🕒 --:--", self)
        self.pomo_badge.setStyleSheet("color: #ff9900; font-weight: bold; font-size: 13px; background: rgba(0,0,0,180); border: 1px solid #ff9900; border-radius: 8px; padding: 4px 10px;")
        
        self.top_hbox.addStretch()
        self.top_hbox.addWidget(self.pomo_badge)
        self.main_layout.addLayout(self.top_hbox)

        # 1.1 XP Bar ve Küçük Level Yazısı
        xp_layout = QHBoxLayout()
        self.level_label = QLabel("Lvl 1", self)
        self.level_label.setStyleSheet("color: #00ff00; font-size: 10px; font-weight: bold;")
        
        self.xp_bar = QProgressBar(self)
        self.xp_bar.setMaximum(config.XP_PER_LEVEL)
        self.xp_bar.setFixedHeight(8)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet("QProgressBar { border: 1px solid #333; border-radius: 4px; background: #111; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #005500, stop:1 #00ff00); border-radius: 4px; }")
        
        xp_layout.addWidget(self.level_label)
        xp_layout.addWidget(self.xp_bar)
        self.main_layout.addLayout(xp_layout)

        # 1.1 Enerji Barı (v4.0 Yeni)
        self.energy_bar = QProgressBar(self)
        self.energy_bar.setMaximum(config.MAX_ENERGY)
        self.energy_bar.setFixedHeight(6)
        self.energy_bar.setTextVisible(False)
        self.energy_bar.setStyleSheet("QProgressBar { border: 1px solid #333; border-radius: 3px; background: #111; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8e44ad, stop:1 #e67e22); border-radius: 3px; }")
        self.main_layout.addWidget(self.energy_bar)

        # 2. Orta Panel (Room) - Dinamik Yapı
        self.room_frame = QFrame()
        self.room_frame.setFixedSize(240, 250) # Hareket alanı için yükselttik
        
        self.img_label = QLabel(self.room_frame)
        self.movie = QMovie(self.happy_path)
        self.movie.setScaledSize(QSize(180, 180))
        self.img_label.setMovie(self.movie)
        self.img_label.move(30, 20) # Başlangıçta yukarıda (Bar'a yakın)
        self.movie.start()
        
        self.health_banner = QLabel("Dik Dur!", self.room_frame)
        self.health_banner.setStyleSheet("background: #e67e22; color: white; font-weight: bold; font-size: 10px; border-radius: 5px; padding: 4px 10px; border: 1px solid white;")
        self.health_banner.move(75, 20)
        self.health_banner.setVisible(False)

        self.main_layout.addWidget(self.room_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 3. Mesaj Balonu
        self.msg_label = QLabel(self.room_frame)
        self.msg_label.setFixedSize(220, 65)
        self.msg_label.move(10, -5)
        self.msg_label.setStyleSheet("""
            background-color: white; 
            border: 2px solid #2ecc71; 
            border-radius: 12px; 
            padding: 8px; 
            color: #222; 
            font-weight: bold; 
            font-size: 13px;
        """)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setWordWrap(True)
        self.msg_label.hide()
        
        self.setLayout(self.main_layout)
        self.setFixedSize(280, 390) 
        self.show()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(config.ASSETS_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QIcon.Mode.Normal.Normal))
        
        tray_menu = QMenu()
        tray_menu.addAction("📊 Dashboard", self.open_dashboard)
        tray_menu.addSeparator()
        tray_menu.addAction("❌ Kapat", self.force_quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def open_dashboard(self):
        # Dashboard'u Robot'un COCUGU YAPMA (Bağımsız olsun ama bir referansta tutulsun)
        if not self.dashboard_window:
            self.dashboard_window = Dashboard(self.stats_data, self.monitor.custom_whitelist)
        else:
            self.dashboard_window.stats = self.stats_data
            self.dashboard_window.update_display()
        self.dashboard_window.show()
        self.dashboard_window.raise_()
        self.dashboard_window.activateWindow()

    def update_status(self, focused, title, is_afk, stats, pomo, health):
        self.stats_data = stats
        self.current_window_title = title
        self.level_label.setText(f"Lvl {stats['level']}")
        self.xp_bar.setValue(int(stats['xp'] % config.XP_PER_LEVEL))
        self.energy_bar.setValue(int(stats.get('energy', 100)))
        
        # Eşya Açma Mantığı Kaldırıldı (Minimalist Tasarım)

        if pomo['state'] != "inactive":
            m, s = divmod(pomo['timer'], 60)
            self.pomo_badge.setText(f"{'🍅' if pomo['state']=='work' else '☕'} {m:02d}:{s:02d}")
            self.pomo_badge.setVisible(True)
        else:
            self.pomo_badge.setVisible(False)

        if health:
            self.show_message(health)
            # Health banner kalsın şimdilik
            self.health_banner.setText(health)
            self.health_banner.setVisible(True)
            QTimer.singleShot(6000, lambda: self.health_banner.setVisible(False))

        # info_label kaldırıldı (Gereksiz görüldüğü için)

        if is_afk:
            if not self.is_afk:
                self.change_animation(self.sleep_path)
                self.show_message("Zzz... Biraz mola?")
                self.is_afk = True
            return
        
        new_state = "happy" if focused else "angry"
        # Durum değiştiyse VEYA uzun süredir mesaj gelmediyse (Dinamik Döngü)
        now = time.time()
        time_since_last_msg = now - getattr(self, "last_msg_time", 0)
        
        if new_state != self.state or self.is_afk or time_since_last_msg > 300: # 5 dakikada bir hatırla
            self.state = new_state
            self.is_afk = False
            self.change_animation(self.happy_path if focused else self.angry_path)
            self.last_msg_time = now
            
            good_msgs = [
                "🚀 Harika gidiyorsun, böyle devam!", 
                "✨ Atom karınca gibisin!", 
                "🔥 Odaklanma seviyen tavan!",
                "💎 Bugün çok verimlisin!",
                f"📈 Tam {int(stats['focused_min'])} dakikadır odaklısın!" # Bilgiyi buraya gömdük
            ]
            bad_msgs = [
                "🔌 Sanki biraz dağıldık mı?", 
                "🚨 İşe dönme vakti kaptan!", 
                "⚡ Odaklanınca daha iyisin!",
                "🧗‍♂️ Hedefinden sapma!",
                "🛑 Robotumuz biraz üzgün..."
            ]
            self.show_message(random.choice(good_msgs if focused else bad_msgs))

    def show_message(self, text):
        self.msg_label.setText(text)
        self.msg_label.show()
        self.img_label.move(30, 70) # Mesaj gelince robotu aşağı kaydır (Yer aç)
        self.health_banner.move(75, 70)
        # 10 saniye sonra gizle
        QTimer.singleShot(10000, self.hide_message)

    def hide_message(self):
        self.msg_label.hide()
        self.img_label.move(30, 20) # Mesaj gidince robotu yukarı çıkar (Baralara yaklaş)
        self.health_banner.move(75, 20)

    def change_animation(self, path):
        self.movie.stop()
        if os.path.exists(path): self.movie.setFileName(path)
        self.movie.start()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1a1a1a; color: white; border: 1px solid #333; } QMenu::item:selected { background-color: #333; }")
        menu.addAction("📊 İstatistikler & Ayarlar", self.open_dashboard)
        pomo_text = "🍅 Pomodoro Başlat" if self.monitor.pomodoro_state == "inactive" else "⏹️ Pomodoro Durdur"
        menu.addAction(pomo_text, self.toggle_pomodoro)
        menu.addSeparator()
        menu.addAction("✅ Bu Pencereye İzin Ver", lambda: self.monitor.custom_whitelist.add(self.current_window_title))
        menu.addSeparator()
        menu.addAction("❌ Kapat", self.force_quit)
        menu.exec(event.globalPos())

    def toggle_pomodoro(self):
        if self.monitor.pomodoro_state == "inactive":
            self.monitor.start_pomodoro()
            self.msg_label.setText("Pomodoro başladı! 🍅")
        else:
            self.monitor.stop_pomodoro()
            self.msg_label.setText("Pomodoro durduruldu.")

    def force_quit(self):
        try:
            self.monitor.stop()
        except:
            pass
        # os._exit(0) kesin çıkış sağlar, Qt olay döngüsünü zorla kırar
        import os
        os._exit(0)

    def closeEvent(self, event):
        # Robot penceresi kapatılmaya çalışıldığında IGNORE yap (Uygulama tıkır tıkır çalışsın)
        event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.oldPos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # KRİTİK AYAR: Son pencere kapandığında ASLA ÇIKMA
    app.setQuitOnLastWindowClosed(False)
    
    pet = FocusPet()
    
    # Uygulamanın kesinlikle açık kalması için döngüye gir
    sys.exit(app.exec())
