import time
import psutil
import win32gui
import win32process
import win32api
from PyQt6.QtCore import QThread, pyqtSignal
import json
import os
import config

class StatsTracker:
    def __init__(self):
        self.stats_file = config.STATS_FILE
        self.data = self.load_stats()
        self.last_save = time.time()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Eksik alanları varsayılanla doldur (Geriye dönük uyumluluk)
                    defaults = config.get_default_stats()
                    for key, val in defaults.items():
                        if key not in data:
                            data[key] = val
                    return data
            except:
                pass
        return config.get_default_stats()

    def update(self, state, duration_sec): 
        min_val = duration_sec / 60
        if state == "focused":
            self.data["focused_min"] += min_val
            self.data["xp"] += config.XP_FOCUSED_PER_MIN * min_val 
        elif state == "distracted":
            self.data["distracted_min"] += min_val
            self.data["xp"] = max(0, self.data["xp"] - config.XP_DISTRACTED_LOSS_PER_MIN * min_val)
        elif state == "afk":
            self.data["afk_min"] += min_val
            
        self.data["level"] = int(self.data["xp"] // config.XP_PER_LEVEL) + 1
            
        if time.time() - self.last_save > 30:
            self.save_stats()

    def save_stats(self):
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            self.last_save = time.time()
        except:
            pass

class WindowMonitor(QThread):
    # (focused, title, is_afk, stats, pomodoro_info, health_alert)
    focus_changed = pyqtSignal(bool, str, bool, dict, dict, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.stats = StatsTracker()
        
        self.custom_whitelist = set()
        
        # Pomodoro Durumu
        self.pomodoro_state = "inactive" # inactive, work, break
        self.pomodoro_timer = 0
        
        # Sağlık Takibi
        self.last_posture_check = time.time()
        self.last_water_check = time.time()
        self.last_eye_check = time.time()

        self.last_tick_time = time.time()

    def start_pomodoro(self):
        self.pomodoro_state = "work"
        self.pomodoro_timer = config.POM_WORK_SEC if hasattr(config, "POM_WORK_SEC") else config.POMODORO_WORK_SEC
        
    def stop_pomodoro(self):
        self.pomodoro_state = "inactive"
        self.pomodoro_timer = 0

    def get_idle_time(self):
        try:
            last_input_tick = win32api.GetLastInputInfo()
            current_tick = win32api.GetTickCount()
            return (current_tick - last_input_tick) / 1000.0
        except:
            return 0

    def run(self):
        self.last_tick_time = time.time()
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_tick_time
            self.last_tick_time = current_time
            
            # 1. Başlık ve AFK Kontrolü
            title = self.get_active_window_info() or "Masaüstü/Boş"
            idle_sec = self.get_idle_time()
            is_afk = idle_sec > config.AFK_THRESHOLD_SEC
            
            # 2. Pomodoro Güncelleme
            # (Basit sürüm: her saniye düşüyoruz)
            if self.pomodoro_state != "inactive":
                self.pomodoro_timer = max(0, self.pomodoro_timer - dt)
                if self.pomodoro_timer <= 0:
                    if self.pomodoro_state == "work":
                        self.pomodoro_state = "break"
                        self.pomodoro_timer = config.POMODORO_BREAK_SEC
                    else:
                        self.pomodoro_state = "work"
                        self.pomodoro_timer = config.POMODORO_WORK_SEC

            # 3. Sağlık Uyarıları (Health Alerts)
            health_msg = ""
            if not is_afk:
                if current_time - self.last_posture_check > config.HEALTH_POSTURE_SEC:
                    health_msg = "🧍 Dik Durmayı Unutma!"
                    self.last_posture_check = current_time
                elif current_time - self.last_eye_check > config.HEALTH_EYE_SEC:
                    health_msg = "👁️ 20 Saniye Uzağa Bak!"
                    self.last_eye_check = current_time
                elif current_time - self.last_water_check > config.HEALTH_WATER_SEC:
                    health_msg = "💧 Bir Yudum Su İçmelisin."
                    self.last_water_check = current_time

            # 4. İstatistik Güncelleme
            focused = False
            if not is_afk:
                focused = self.is_focused(title)
                state = "focused" if focused else "distracted"
                self.stats.update(state, dt)
            else:
                self.stats.update("afk", dt)
            
            pomo_info = {"state": self.pomodoro_state, "timer": int(self.pomodoro_timer)}
            self.focus_changed.emit(focused, title, is_afk, self.stats.data, pomo_info, health_msg)
            
            time.sleep(1)

    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd: return win32gui.GetWindowText(hwnd)
        except: pass
        return ""

    def is_focused(self, title):
        if not title or title == "Masaüstü/Boş": return False
        title_low = title.lower()
        
        for black in config.DEFAULT_BLACKLIST:
            if black in title_low: return False

        for custom_item in self.custom_whitelist:
            if custom_item in title_low: return True

        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            p_name = process.name().lower()
            
            if "opera" in p_name and ("gx" in p_name or "browser.exe" == p_name):
                return True
                
            if any(b in p_name for b in config.BROWSERS):
                return any(kw in title_low for kw in config.DEFAULT_WHITELIST)
        except: pass
        
        return any(kw in title_low for kw in config.DEFAULT_WHITELIST)

    def stop(self):
        self.running = False
        self.stats.save_stats()
