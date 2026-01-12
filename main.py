import sys
import os
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu, QProgressBar, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QPixmap, QCursor, QAction, QMovie, QColor
from monitor import WindowMonitor

class FocusPet(QWidget):
    def __init__(self):
        super().__init__()
        
        # Animasyon yolları
        self.happy_path = "assets/happy.gif" if os.path.exists("assets/happy.gif") else "assets/happy.png"
        self.angry_path = "assets/angry.gif" if os.path.exists("assets/angry.gif") else "assets/angry.png"
        self.sleep_path = "assets/sleep.gif" if os.path.exists("assets/sleep.gif") else ("assets/sleep.png" if os.path.exists("assets/sleep.png") else self.happy_path)
        
        self.state = "happy"
        self.is_afk = False
        self.current_window_title = ""
        
        self.initUI()
        self.oldPos = self.pos()
        
        # Monitor Thread
        self.monitor = WindowMonitor()
        self.monitor.focus_changed.connect(self.update_status)
        self.monitor.start()

        # Yaratıcı ve Motive Edici Mesajlar
        self.motivation_messages = [
            "Geleceğin algoritmasını yazıyorsun, devam et! 🚀",
            "XP yağmuru başladı! Odaklanmak sana çok yakışıyor. ✨",
            "Vay canına! Bu hızla gidersen yakında beni bile geçebilirsin. 🤖",
            "Beynin şu an süper bilgisayar modunda, sakın durma!",
            "Her saniye daha akıllı bir versiyonun yükleniyor... %99...",
            "Ders çalışmak değil, imparatorluk kurmak bu! 👑",
            "ChatGPT bile senin odaklanma gücüne hayran kaldı.",
            "Bu verimlilikle Mars'a ilk biz gideceğiz! 🚀",
            "Robot kalbim senin başarınla atıyor (gerçekten!) 💖",
            "Öğrendiğin her bilgi, koduma bir artı satır ekliyor. 💪",
            "Odaklanma canavarı iş başında! Harika gidiyorsun.",
            "Zihnini bir lazer gibi kullanıyorsun, yakıyorsun buraları! 🔥"
        ]
        self.warning_messages = [
            "Hop! Devrelerim yandı, nereye bakıyorsun öyle? 🔌",
            "Dikkat dağıtıcılar saldırıyor! Kalkanları kaldır ve derse dön. 🛡️",
            "Eğer odağın kaçarsa bir sonraki güncellemede emoji alamam... 😢",
            "XP kaybı algılandı! Bu operasyonun patronu sensin, toparlan.",
            "Robotlar yalan söylemez: Şu an yanlış yerdesin dostum. 🚫",
            "YouTube bir yere kaçmıyor ama geleceğin kaçabilir! ⏱️",
            "Sence de şu an ChatGPT ile bir şeyler sorma vakti değil mi?",
            "Eyvah! Odak seviyen %0'a düşmek üzere, acil müdahale! 🚨",
            "Ben burada seni bekliyorum, sen oralarda ne yapıyorsun? 🤖💔",
            "Bak, şu an ders çalışmazsan pillerim biterse karışmam!",
            "Odaklanman lazım, yoksa güncelleme hatası vereceğim! ⚠️",
            "Seni izliyorum... Ve şu an hiç mutlu değilim. 😠"
        ]

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Üst Bilgi (Level ve XP)
        self.stats_layout = QVBoxLayout()
        
        self.level_label = QLabel("LVL 1", self)
        self.level_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px; background: rgba(0,0,0,100); border-radius: 5px; padding: 2px;")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.xp_bar = QProgressBar(self)
        self.xp_bar.setMaximum(100)
        self.xp_bar.setValue(0)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setFixedHeight(8)
        self.xp_bar.setStyleSheet("""
            QProgressBar { border: 1px solid grey; border-radius: 4px; background: rgba(255,255,255,50); }
            QProgressBar::chunk { background-color: #00ff00; border-radius: 4px; }
        """)
        
        self.stats_layout.addWidget(self.level_label)
        self.stats_layout.addWidget(self.xp_bar)
        self.main_layout.addLayout(self.stats_layout)

        # Pet Görseli
        self.img_label = QLabel(self)
        self.movie = QMovie(self.happy_path)
        self.movie.setScaledSize(QSize(200, 200))
        self.img_label.setMovie(self.movie)
        self.movie.start()
        self.main_layout.addWidget(self.img_label)
        
        # Mesaj Etiketi
        self.msg_label = QLabel("Hazır mısın? Başlayalım!", self)
        self.msg_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 230);
            border: 2px solid #333;
            border-radius: 12px;
            padding: 10px;
            color: #111;
            font-weight: bold;
            font-size: 13px;
        """)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setWordWrap(True)
        self.main_layout.addWidget(self.msg_label)
        
        # Alt Bilgi (Odak Süresi)
        self.time_label = QLabel("Odak: 0 dk", self)
        self.time_label.setStyleSheet("color: white; font-size: 11px; background: rgba(0,0,0,80); border-radius: 5px; padding: 2px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.time_label)

        self.setLayout(self.main_layout)
        self.setGeometry(100, 100, 250, 420)
        self.show()

    def update_status(self, focused, title, is_afk, stats):
        self.current_window_title = title
        
        # İstatistikleri Güncelle
        self.level_label.setText(f"LVL {stats['level']}")
        current_xp = stats['xp'] % 100
        self.xp_bar.setValue(int(current_xp))
        
        # Zamanı dakika:saniye formatına çevir
        f_min = stats['focused_min']
        f_total_sec = int(f_min * 60)
        f_display = f"{f_total_sec // 60} dk {f_total_sec % 60} sn"
        
        a_min = stats['afk_min']
        a_total_sec = int(a_min * 60)
        a_display = f"{a_total_sec // 60} dk {a_total_sec % 60} sn"
        
        self.time_label.setText(f"Odak: {f_display} | AFK: {a_display}")

        # AFK Durumu
        if is_afk:
            if not self.is_afk:
                self.movie.stop()
                self.movie.setFileName(self.sleep_path)
                self.movie.start()
                self.msg_label.setText("Zzz... Biraz mola?")
                self.is_afk = True
            return # AFK iken diğer kontrolleri yapma
        
        # AFK'dan yeni dönüldüyse veya Odak Durumu Değiştiyse
        new_state = "happy" if focused else "angry"
        if new_state != self.state or self.is_afk:
            self.state = new_state
            self.is_afk = False
            self.movie.stop()
            path = self.happy_path if focused else self.angry_path
            self.movie.setFileName(path)
            self.img_label.setMovie(self.movie)
            self.movie.start()
            
            msg = random.choice(self.motivation_messages) if focused else random.choice(self.warning_messages)
            self.msg_label.setText(msg)

    def allow_current_window(self):
        if self.current_window_title:
            self.monitor.add_to_whitelist(self.current_window_title)
            self.msg_label.setText("Bu pencere artık dost!")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        contextMenu.setStyleSheet("""
            QMenu { background-color: #333; color: white; border: 1px solid #555; padding: 5px; }
            QMenu::item:selected { background-color: #555; }
        """)
        
        title_info = contextMenu.addAction(f"Hedef: {self.current_window_title[:20]}...")
        title_info.setEnabled(False)
        contextMenu.addSeparator()

        allowAction = contextMenu.addAction("✅ Bu Pencereye İzin Ver")
        allowAction.triggered.connect(self.allow_current_window)
        
        contextMenu.addSeparator()
        
        quitAction = contextMenu.addAction("❌ Kapat")
        quitAction.triggered.connect(QApplication.instance().quit)
        
        contextMenu.exec(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = FocusPet()
    sys.exit(app.exec())
