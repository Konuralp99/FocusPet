import time
import psutil
import win32gui
import win32process
import win32api
from PyQt6.QtCore import QThread, pyqtSignal
import json
import os

class StatsTracker:
    def __init__(self):
        self.stats_file = "stats.json"
        self.data = self.load_stats()
        self.last_save = time.time()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"focused_min": 0, "distracted_min": 0, "afk_min": 0, "xp": 0, "level": 1}

    def update(self, state, duration_sec): 
        # duration_sec: Gerçek geçen saniye (delta time)
        min_val = duration_sec / 60
        
        if state == "focused":
            self.data["focused_min"] += min_val
            # Seviye başına 10 XP, her dakika odaklanma ~10 XP verir (1 saniye = ~0.16 XP)
            self.data["xp"] += 10 * min_val 
        elif state == "distracted":
            self.data["distracted_min"] += min_val
            # Odak bozulduğunda XP kaybı (daha az cezalandırıcı: dakikada 2 XP)
            self.data["xp"] = max(0, self.data["xp"] - 2 * min_val)
        elif state == "afk":
            self.data["afk_min"] += min_val
            
        # Level up logic (her 100 XP bir seviye)
        self.data["level"] = int(self.data["xp"] // 100) + 1
            
        if time.time() - self.last_save > 15: # 15 saniyede bir diske yaz
            self.save_stats()

    def save_stats(self):
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            self.last_save = time.time()
        except Exception as e:
            print(f"Stats kaydetme hatası: {e}")

class WindowMonitor(QThread):
    # (focused, title, is_afk, stats)
    focus_changed = pyqtSignal(bool, str, bool, dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.stats = StatsTracker()
        
        # Karaliste
        self.blacklist_keywords = ["youtube", "netflix", "twitch", "facebook", "instagram", "twitter", "reddit", "game", "oyun"]
        
        # Bilinen Tarayıcılar
        self.browsers = ["msedge.exe", "chrome.exe", "brave.exe", "opera.exe", "opera_gx.exe", "browser.exe"]
        
        # Beyaz liste
        self.whitelist_keywords = [
            "chatgpt", "openai", "opera", "transkript", "ders", "ödev", "çalışma", "öğren", 
            "new chat", "gpt-4", "gpt-3", "ai", "yapay zeka", "google search", "gemini", "claude",
            "sistem", "dinamik", "kontrol", "soru", "yardım", "sınav", "çözüm", "analiz", "mühendis"
        ]
        self.custom_whitelist = set()

        # AFK Tespiti ayarları
        self.afk_threshold_sec = 45 # 45 saniye boyunca işlem yoksa AFK say
        
        # Zamanlayıcı için son güncelleme zamanı
        self.last_tick_time = time.time()
        
    def add_to_whitelist(self, title):
        if title:
            self.custom_whitelist.add(title.lower())

    def get_idle_time(self):
        # Windows API kullanarak sistem genelindeki son giriş zamanını al (milisaniye)
        # Mouse veya klavye fark etmeksizin sistemdeki son aktiviteyi döner
        last_input_tick = win32api.GetLastInputInfo()
        current_tick = win32api.GetTickCount()
        idle_time_sec = (current_tick - last_input_tick) / 1000.0
        return idle_time_sec

    def run(self):
        self.last_tick_time = time.time()
        while self.running:
            # Gerçek geçen süreyi hesapla (Delta Time)
            current_time = time.time()
            dt = current_time - self.last_tick_time
            self.last_tick_time = current_time
            
            title = self.get_active_window_info() or "Masaüstü/Boş"
            idle_sec = self.get_idle_time()
            is_afk = idle_sec > self.afk_threshold_sec
            
            focused = False
            if not is_afk:
                focused = self.is_focused(title)
                state = "focused" if focused else "distracted"
                self.stats.update(state, dt)
            else:
                self.stats.update("afk", dt)
            
            self.focus_changed.emit(focused, title, is_afk, self.stats.data)
            time.sleep(1)

    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return win32gui.GetWindowText(hwnd)
        except:
            pass
        return ""

    def is_focused(self, title):
        if not title or title == "Masaüstü/Boş": return False
        title_low = title.lower()
        
        # 1. Karaliste (Öncelikli)
        for black in self.blacklist_keywords:
            if black in title_low:
                return False

        # 2. Dinamik Whitelist
        for custom_item in self.custom_whitelist:
            if custom_item in title_low:
                return True

        # 3. Süreç ve Tarayıcı Kontrolü
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            p_name = process.name().lower()
            
            # Opera GX her zaman (karaliste hariç) serbest
            if "opera" in p_name and ("gx" in p_name or "browser.exe" == p_name):
                return True
                
            # Diğer tarayıcılar (Sadece whitelist varsa)
            if any(b in p_name for b in self.browsers):
                return any(kw in title_low for kw in self.whitelist_keywords)
        except:
            pass
        
        # 4. Genel Anahtar Kelimeler
        return any(kw in title_low for kw in self.whitelist_keywords)

    def stop(self):
        self.running = False
        self.stats.save_stats()
